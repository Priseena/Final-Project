from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone
import secrets
from typing import Optional, Dict, List
from pydantic import ValidationError
from sqlalchemy import func, update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_email_service, get_settings
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password
from uuid import UUID
from app.services.email_service import EmailService
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class UserService:
    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        try:
            result = await session.execute(query)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            return None

    @classmethod
    async def _fetch_user(cls, session: AsyncSession, **filters) -> Optional[User]:
        query = select(User).filter_by(**filters)
        result = await cls._execute_query(session, query)
        return result.scalars().first() if result else None

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: UUID) -> Optional[User]:
        return await cls._fetch_user(session, id=user_id)

    @classmethod
    async def get_by_nickname(cls, session: AsyncSession, nickname: str) -> Optional[User]:
        return await cls._fetch_user(session, nickname=nickname)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[User]:
        return await cls._fetch_user(session, email=email)

    @classmethod
    async def create(cls, session: AsyncSession, user_data: Dict[str, str], email_service: EmailService) -> Optional[User]:
        try:
            # Validate user data
            if not user_data.get("email") or "@" not in user_data["email"]:
                raise ValueError("Invalid email address")
            if not user_data.get("password") or len(user_data["password"]) < 8:
                raise ValueError("Password must be at least 8 characters long")
            if not user_data.get("nickname") or len(user_data["nickname"]) < 3:
                raise ValueError("Nickname must be at least 3 characters long")

            # Check if the user already exists
            existing_user = await cls.get_by_email(session, user_data["email"])
            if existing_user:
                raise ValueError("User with the given email already exists")

            # Hash the password and create the user
            user_data["hashed_password"] = hash_password(user_data.pop("password"))
            new_user = User(**user_data)

            # Generate a unique nickname
            new_nickname = generate_nickname()
            while await cls.get_by_nickname(session, new_nickname):
                new_nickname = generate_nickname()
            new_user.nickname = new_nickname

            # Assign role and handle email verification
            user_count = await cls.count(session)
            new_user.role = UserRole.ADMIN if user_count == 0 else UserRole.ANONYMOUS
            if new_user.role == UserRole.ADMIN:
                new_user.email_verified = True
            else:
                new_user.verification_token = generate_verification_token()
                await email_service.send_verification_email(new_user)

            session.add(new_user)
            await session.commit()
            return new_user
        except ValueError as e:
            logger.error(f"Validation error during user creation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {e}")
            return None

    @classmethod
    async def update(cls, session: AsyncSession, user_id: UUID, update_data: Dict[str, str]) -> Optional[User]:
        try:
            # Validate update data
            if "email" in update_data and "@" not in update_data["email"]:
                raise ValueError("Invalid email address")
            if "password" in update_data and len(update_data["password"]) < 8:
                raise ValueError("Password must be at least 8 characters long")

            # Hash the password if provided
            if "password" in update_data:
                update_data["hashed_password"] = hash_password(update_data.pop("password"))

            # Update the user
            query = update(User).where(User.id == user_id).values(**update_data).execution_options(synchronize_session="fetch")
            await cls._execute_query(session, query)

            # Fetch and return the updated user
            updated_user = await cls.get_by_id(session, user_id)
            if updated_user:
                session.refresh(updated_user)
                return updated_user
            else:
                raise ValueError("User not found")
        except ValueError as e:
            logger.error(f"Validation error during user update: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during user update: {e}")
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if not user:
            return False
        await session.delete(user)
        await session.commit()
        return True

    @classmethod
    async def list_users(cls, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await cls._execute_query(session, query)
        return result.scalars().all() if result else []

    @classmethod
    async def register_user(cls, session: AsyncSession, user_data: Dict[str, str], email_service: EmailService) -> Optional[User]:
        return await cls.create(session, user_data, email_service)

    @classmethod
    async def login_user(cls, session: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await cls.get_by_email(session, email)
        if user:
            if not user.email_verified or user.is_locked:
                return None
            if verify_password(password, user.hashed_password):
                user.failed_login_attempts = 0
                user.last_login_at = datetime.now(timezone.utc)
                session.add(user)
                await session.commit()
                return user
            else:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= settings.max_login_attempts:
                    user.is_locked = True
                session.add(user)
                await session.commit()
        return None

    @classmethod
    async def reset_password(cls, session: AsyncSession, user_id: UUID, new_password: str) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user:
            user.hashed_password = hash_password(new_password)
            user.failed_login_attempts = 0
            user.is_locked = False
            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def verify_email_with_token(cls, session: AsyncSession, user_id: UUID, token: str) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.verification_token == token:
            user.email_verified = True
            user.verification_token = None
            user.role = UserRole.AUTHENTICATED
            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def unlock_user_account(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0
            session.add(user)
            await session.commit()
            return True
        return False
    
    @classmethod
    async def is_account_locked(cls, session: AsyncSession, email: str) -> bool:
       """
      Check if a user's account is locked.
       """
       user = await cls.get_by_email(session, email)
       return user.is_locked if user else False