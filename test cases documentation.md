
# ✅ Test Case Documentation: Final Project

This document outlines 10 newly added test cases across `test_users_api.py` and `test_upload_picture.py`. Each test includes a description, the error originally encountered (if any), the root cause, and how it was fixed.

---

## 🔹 File: `tests/test_users_api.py`

### 1. Test: `test_create_user_access_denied`
- **Purpose**: Ensure normal users cannot create new users.
- **Error**: Endpoint allowed access and returned 200.
- **Fix**: Added role-based check; route now blocks non-admins with `403 Forbidden`.

---

### 2. Test: `test_create_user_missing_fields`
- **Purpose**: Handle requests with missing required fields.
- **Error**: App returned 200 OK even when required fields were missing.
- **Fix**: Schema validation updated; FastAPI now returns `422 Unprocessable Entity` for missing fields.

---

### 3. Test: `test_login_success`
- **Purpose**: Verify successful login for a verified user.
- **Error**: None
- **Fix**: Confirmed valid credentials return access token with correct role decoded from JWT.

---

### 4. Test: `test_login_user_not_found`
- **Purpose**: Ensure non-existent users cannot log in.
- **Error**: App returned `500 Internal Server Error`.
- **Fix**: Added proper exception handling in login route; now returns `401 Unauthorized` with correct message.

---

### 5. Test: `test_login_incorrect_password`
- **Purpose**: Prevent login with incorrect password.
- **Error**: App returned `500 Internal Server Error` instead of 401.
- **Fix**: Exception raised on invalid credentials is now correctly caught and returns `401 Unauthorized`.

---

### 6. Test: `test_login_locked_user`
- **Purpose**: Block login attempts from locked users.
- **Error**: App threw a 500 error without a clear message.
- **Fix**: Logic updated to check user status before verifying password; now returns `401 Unauthorized`.

---

### 7. Test: `test_update_user_linkedin`
- **Purpose**: Update user's LinkedIn profile.
- **Error**: Endpoint returned 500 Internal Server Error.
- **Fix**: Resolved model validation and ensured route accepts correct schema; now returns 200 OK on success.

---

## 🔹 File: `tests/test_upload_picture.py`

### 8. Test: `test_upload_valid_picture`
- **Purpose**: Upload a valid PNG file and receive profile URL.
- **Original Error**:
  - `AttributeError: 'User' object has no attribute 'token'`
  - `IntegrityError: missing required columns`
- **Fix**:
  - Used `authorized_user_token` instead of full user object.
  - Fixed ORM field mismatch (`is_verified` not a valid param).
  - Ensured endpoint returns a proper URL.

---

### 9. Test: `test_upload_invalid_file_type`
- **Purpose**: Block non-image files like `.exe`.
- **Original Error**:
  - 200 OK was returned for invalid content type.
- **Fix**:
  - Added content-type validation middleware.
  - Now returns `400 Bad Request`.

---

### 10. Test: `test_upload_picture_unauthenticated`
- **Purpose**: Prevent file upload without JWT token.
- **Original Error**:
  - File uploaded successfully due to missing auth check.
- **Fix**:
  - Added `Depends(get_current_user)` in route.
  - Returns `401 Unauthorized`.




