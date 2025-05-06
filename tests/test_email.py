import pytest
from app.services.email_service import EmailService
from app.utils.template_manager import TemplateManager
from unittest.mock import AsyncMock


    
@pytest.mark.asyncio
async def test_send_markdown_email(email_service):

     # Mock the email service method
    mock_email_service = AsyncMock()
    mock_email_service.send_user_email.return_value = True

    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "verification_url": "http://example.com/verify?token=abc123"
    }
    await email_service.send_user_email(user_data, 'email_verification')
    # Manual verification in Mailtrap
    # Add assertions to verify the behavior
    # For example, check if the email service logs an error or handles the expired token gracefully
    assert True  # Replace with actual assertions