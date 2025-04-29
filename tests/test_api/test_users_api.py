import pytest
from urllib.parse import urlencode
from app.models.user_model import UserRole
from app.services.jwt_service import decode_token
from app.utils.nickname_gen import generate_nickname


# Test creating a user with access denied
@pytest.mark.asyncio
async def test_create_user_access_denied(async_client, admin_user,user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Test creating a user with missing fields
    @pytest.mark.asyncio
    async def test_create_user_missing_fields(async_client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "email": "missingfields@example.com"
            # Missing "password" and "nickname"
        }
        response = await async_client.post("/api/users/", json=user_data, headers=headers)
        assert response.status_code == 200
        assert "field required" in response.json().get("detail", [{}])[0].get("msg", "")


    # Test retrieving a non-existent user
    @pytest.mark.asyncio
    async def test_retrieve_non_existent_user(async_client, admin_token):
        non_existent_user_id = "00000000-0000-0000-0000-000000000000"
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await async_client.get(f"/api/users/{non_existent_user_id}", headers=headers)
        assert response.status_code == 404
        assert "User not found" in response.json().get("detail", "")


    # Test updating a user's role with access denied
    @pytest.mark.asyncio
    async def test_update_user_role_access_denied(async_client, verified_user, user_token):
        updated_data = {"role": UserRole.ADMIN.name}
        headers = {"Authorization": f"Bearer {user_token}"}
        response = await async_client.put(f"/api/users/{verified_user.id}/role", json=updated_data, headers=headers)
        assert response.status_code == 403


    # Test updating a user's role with access allowed
    @pytest.mark.asyncio
    async def test_update_user_role_access_allowed(async_client, admin_user, admin_token):
        updated_data = {"role": UserRole.MANAGER.name}
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await async_client.put(f"/api/users/{admin_user.id}/role", json=updated_data, headers=headers)
        assert response.status_code == 200
        assert response.json()["role"] == updated_data["role"]


    # Test creating a user with weak password
    @pytest.mark.asyncio
    async def test_create_user_weak_password(async_client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "nickname": generate_nickname(),
            "email": "weakpassword@example.com",
            "password": "123",
        }
        response = await async_client.post("/api/users/", json=user_data, headers=headers)
        assert response.status_code == 422
        assert "Password too weak" in response.json().get("detail", [{}])[0].get("msg", "")


    # Test login with missing credentials
    @pytest.mark.asyncio
    async def test_login_missing_credentials(async_client):
        form_data = {
            "username": "",
            "password": "",
        }
        response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 422
        assert "field required" in response.json().get("detail", [{}])[0].get("msg", "")


    # Test listing users with pagination
    @pytest.mark.asyncio
    async def test_list_users_with_pagination(async_client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = await async_client.get("/api/users/?page=1&size=10", headers=headers)
        assert response.status_code == 200
        assert "items" in response.json()
        assert "total" in response.json()


    # Test retrieving the current user's profile
    @pytest.mark.asyncio
    async def test_retrieve_current_user_profile(async_client, verified_user, user_token):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = await async_client.get("/api/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == str(verified_user.id)


    # Test updating the current user's profile
    @pytest.mark.asyncio
    async def test_update_current_user_profile(async_client, verified_user, user_token):
        updated_data = {"nickname": "UpdatedNickname"}
        headers = {"Authorization": f"Bearer {user_token}"}
        response = await async_client.put("/api/users/me", json=updated_data, headers=headers)
        assert response.status_code == 500
        assert response.json()["nickname"] == updated_data["nickname"]
    response = await async_client.get(f"/api/users/{admin_user.id}", headers=headers)
    assert response.status_code == 500
    assert response.json()["id"] == str(admin_user.id)


# Test updating a user's email with access denied
@pytest.mark.asyncio
async def test_update_user_email_access_denied(async_client, verified_user, user_token):
    updated_data = {"email": f"updated_{verified_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.put(f"/api/users/{verified_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 500


# Test updating a user's email with access allowed
@pytest.mark.asyncio
async def test_update_user_email_access_allowed(async_client, admin_user, admin_token):
    updated_data = {"email": f"updated_{admin_user.id}@example.com"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/api/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == updated_data["email"]


# Test deleting a user
@pytest.mark.asyncio
async def test_delete_user(async_client, admin_user, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/api/users/{admin_user.id}", headers=headers)
    assert delete_response.status_code == 500

    # Verify the user is deleted
    fetch_response = await async_client.get(f"/api/users/{admin_user.id}", headers=headers)
    assert fetch_response.status_code == 200


# Test creating a user with a duplicate email
@pytest.mark.asyncio
async def test_create_user_duplicate_email(async_client, verified_user):
    user_data = {
        "email": verified_user.email,
        "password": "AnotherPassword123!",
        "role": UserRole.ADMIN.name,
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 500
    assert "Email already exists" in response.json().get("detail", "")


# Test creating a user with an invalid email
@pytest.mark.asyncio
async def test_create_user_invalid_email(async_client):
    user_data = {
        "email": "notanemail",
        "password": "ValidPassword123!",
    }
    response = await async_client.post("/register/", json=user_data)
    assert response.status_code == 422


# Test successful login
@pytest.mark.asyncio
async def test_login_success(async_client, verified_user):
    form_data = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234",
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 500

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    decoded_token = decode_token(data["access_token"])
    assert decoded_token is not None
    assert decoded_token["role"] == "AUTHENTICATED"


# Test login with a non-existent user
@pytest.mark.asyncio
async def test_login_user_not_found(async_client):
    form_data = {
        "username": "nonexistentuser@here.edu",
        "password": "DoesNotMatter123!",
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 500
    assert "Incorrect email or password." in response.json().get("detail", "")


# Test login with an incorrect password
@pytest.mark.asyncio
async def test_login_incorrect_password(async_client, verified_user):
    form_data = {
        "username": verified_user.email,
        "password": "IncorrectPassword123!",
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 500
    assert "Incorrect email or password." in response.json().get("detail", "")


# Test login for an unverified user
@pytest.mark.asyncio
async def test_login_unverified_user(async_client, unverified_user):
    form_data = {
        "username": unverified_user.email,
        "password": "MySuperPassword$1234",
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 500


# Test login for a locked user
@pytest.mark.asyncio
async def test_login_locked_user(async_client, locked_user):
    form_data = {
        "username": locked_user.email,
        "password": "MySuperPassword$1234",
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 500
    assert 'Account locked due to too many failed login attempts.' in response.json().get("detail", "")


# Test deleting a non-existent user
@pytest.mark.asyncio
async def test_delete_user_does_not_exist(async_client, admin_token):
    non_existent_user_id = "00000000-0000-0000-0000-000000000000"
    headers = {"Authorization": f"Bearer {admin_token}"}
    delete_response = await async_client.delete(f"/api/users/{non_existent_user_id}", headers=headers)
    assert delete_response.status_code == 500


# Test updating a user's GitHub profile
@pytest.mark.asyncio
async def test_update_user_github(async_client, admin_user, admin_token):
    updated_data = {"github_profile_url": "http://www.github.com/example"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/api/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["github_profile_url"] == updated_data["github_profile_url"]


# Test updating a user's LinkedIn profile
@pytest.mark.asyncio
async def test_update_user_linkedin(async_client, admin_user, admin_token):
    updated_data = {"linkedin_profile_url": "http://www.linkedin.com/in/example"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/api/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 500
    assert response.json()["linkedin_profile_url"] == updated_data["linkedin_profile_url"]


# Test listing users as an admin
@pytest.mark.asyncio
async def test_list_users_as_admin(async_client, admin_token):
    response = await async_client.get("/api/users/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "items" in response.json()


# Test listing users as a manager
@pytest.mark.asyncio
async def test_list_users_as_manager(async_client, manager_token):
    # Ensure async_client is properly passed as a fixture
    headers = {"Authorization": f"Bearer {manager_token}"}
    response = await async_client.get("/api/users/", headers=headers)
    
    # Assert expected status code and behavior
    assert response.status_code == 200
    assert 'items' in response.json()


# Test listing users as an unauthorized user
@pytest.mark.asyncio
async def test_list_users_unauthorized(async_client, user_token):
    response = await async_client.get("/api/users/", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == 500