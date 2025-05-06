# Profile Picture Upload Feature

## Overview
This feature allows users to upload profile pictures, which are stored in MinIO (S3-compatible storage).

## Endpoint
- **POST** `/users/{user_id}/upload-profile-pic`

### Request
- **Headers**: `Authorization: Bearer <token>`
- **Body**: Multipart form data with a file.

### Response
```json
{
  "image_url": "http://minio:9000/profile-pictures/user_1_test.png"
}