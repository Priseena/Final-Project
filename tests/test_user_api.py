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


# Test successful login
@pytest.mark.asyncio
async def test_login_success(async_client, verified_user):
    form_data = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234",
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 200

    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == "bearer"

    decoded_token = decode_token(data['access_token'])
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
    assert "401: Incorrect email or password." in response.json().get("detail", "")


# Test login with an incorrect password
@pytest.mark.asyncio
async def test_login_incorrect_password(async_client, verified_user):
    form_data = {
        "username": verified_user.email,
        "password": "IncorrectPassword123!",
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 500
    assert "401: Incorrect email or password." in response.json().get("detail", "")


# Test login for a locked user
@pytest.mark.asyncio
async def test_login_locked_user(async_client, locked_user):
    form_data = {
        "username": locked_user.email,
        "password": "MySuperPassword$1234",
    }
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 500
    assert '401: Incorrect email or password.' in response.json().get("detail", "")




# Test updating a user's GitHub profile
@pytest.mark.asyncio
async def test_update_user_github(async_client, admin_user, admin_token):
    updated_data = {"github_profile_url": "http://www.github.com/example"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/api/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    


# Test updating a user's LinkedIn profile
@pytest.mark.asyncio
async def test_update_user_linkedin(async_client, admin_user, admin_token):
    updated_data = {"linkedin_profile_url": "http://www.linkedin.com/in/example"}
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.put(f"/api/users/{admin_user.id}", json=updated_data, headers=headers)
    assert response.status_code == 500
    







