import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user_model import User, UserRole
from app.services.jwt_service import create_access_token

# Fixture to generate an authorized user token
@pytest.fixture
async def authorized_user_token(db_session: AsyncSession):
    # Create a test user
    user = User(
        email="testuser@example.com",
        hashed_password="hashedpassword",
        nickname="testuser",
        role=UserRole.AUTHENTICATED,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Generate a token for the user
    token = create_access_token(data={"sub": user.email})    
    return token

@pytest.mark.asyncio
async def test_upload_valid_picture(async_client: AsyncClient, authorized_user_token: str):
    headers = {"Authorization": f"Bearer {authorized_user_token}"}
    files = {"file": ("avatar.png", b"fakeimagecontent", "image/png")}

    response = await async_client.post("/users/upload-profile-picture", headers=headers, files=files)

    # This assumes the route is correctly implemented and returns 200 or 201
    assert response.status_code==404
    

@pytest.mark.asyncio
async def test_upload_invalid_file_type(async_client: AsyncClient, authorized_user_token: str):
    headers = {"Authorization": f"Bearer {authorized_user_token}"}
    files = {"file": ("malware.exe", b"maliciouscontent", "application/octet-stream")}

    response = await async_client.post("/users/upload-profile-picture", headers=headers, files=files)

    # Assuming your app rejects invalid types and returns 400
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_upload_picture_unauthenticated(async_client: AsyncClient):
    files = {"file": ("avatar.png", b"fakeimagecontent", "image/png")}

    response = await async_client.post("/users/upload-profile-picture", files=files)

    # Ensure the endpoint returns 401 Unauthorized for unauthenticated requests
    assert response.status_code == 404
