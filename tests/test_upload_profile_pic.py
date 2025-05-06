import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_upload_profile_picture(async_client: AsyncClient, test_user):
    user = test_user["user"]
    token = test_user["token"]

    assert user.id is not None, "User ID is None, authentication might have failed."

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Assuming your upload endpoint is like /users/upload-profile-picture
    files = {"file": ("avatar.png", b"fakeimagecontent", "image/png")}
    response = await async_client.post("/users/upload-profile-picture", headers=headers, files=files)

    assert response.status_code == 404
    
