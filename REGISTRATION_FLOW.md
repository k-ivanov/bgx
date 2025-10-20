# User Registration & Activation Flow

## Overview

The BGX Racing Platform now includes a complete user registration system with activation codes for account verification.

## Backend Changes

### 1. Updated Models (`bgx-api/accounts/models.py`)
- `User` model already has:
  - `activation_code`: CharField for storing activation code
  - `is_activated`: BooleanField to track activation status
  - `generate_activation_code()`: Method to generate unique codes
  - `activate()`: Method to activate accounts

### 2. Updated Serializers (`bgx-api/accounts/serializers.py`)
- Added `is_activated` field to `UserSerializer`
- Modified `UserRegistrationSerializer` to generate activation codes on user creation
- Added `UserActivationSerializer` for validating activation codes

### 3. Updated Views (`bgx-api/accounts/views.py`)
- Modified `create()` method to return activation code after registration
- Added `activate()` action endpoint at `/api/users/activate/`
- Activation generates JWT tokens and logs user in automatically

### 4. API Endpoints

#### Registration
```
POST /api/users/
Body: {
  "username": "string",
  "email": "string@example.com",
  "password": "string",
  "password2": "string",
  "first_name": "string",
  "last_name": "string"
}

Response: {
  "user": {...},
  "activation_code": "abc123...",
  "message": "Registration successful! Please use the activation code to activate your account."
}
```

#### Activation
```
POST /api/users/activate/
Body: {
  "activation_code": "abc123..."
}

Response: {
  "message": "Account activated successfully!",
  "user": {...},
  "refresh": "jwt_token",
  "access": "jwt_token"
}
```

## Frontend Changes

### 1. New Components

#### Register Component (`bgx-fe/src/components/Register.jsx`)
- Beautiful registration form with validation
- Fields: First Name, Last Name, Username, Email, Password, Confirm Password
- Client-side validation (password matching, minimum length)
- Success screen displaying activation code
- Copy-to-clipboard functionality for activation code
- Auto-navigation to activation page

#### Activate Component (`bgx-fe/src/components/Activate.jsx`)
- Activation code input form
- Validates activation code with backend
- Success animation and auto-redirect
- Stores JWT tokens in localStorage
- User-friendly error messages

### 2. Updated Components

#### App.jsx
- Added routes for `/register` and `/activate`
- Updated header with "Register" and "Activate" buttons
- Improved navigation with Tailwind styling

#### API Client (`bgx-fe/src/api/api.js`)
- `register(userData)`: Register new user
- `activateAccount(activationCode)`: Activate account
- `login(username, password)`: Login endpoint (prepared for future use)

### 3. Styling
- Tailwind CSS for modern, responsive design
- Custom gradient themes (primary: #667eea, secondary: #764ba2)
- Mobile-friendly forms
- Beautiful success screens with emojis and animations

## User Flow

### Step 1: Registration
1. User navigates to `/register` or clicks "Register" button
2. Fills in registration form:
   - First Name
   - Last Name
   - Username
   - Email
   - Password (min 8 characters)
   - Confirm Password
3. Submits form
4. Backend creates user with `is_activated=False`
5. Backend generates unique activation code
6. Success screen displays activation code
7. User can copy the code and continue to activation

### Step 2: Activation
1. User navigates to `/activate` (auto or manual)
2. Enters activation code (pre-filled if coming from registration)
3. Submits form
4. Backend validates code and activates account
5. Backend generates JWT tokens
6. Frontend stores tokens and logs user in
7. Success screen displays and auto-redirects to home

### Step 3: Authenticated Access
- User is now logged in with JWT tokens
- Can access protected features (future implementation)
- Tokens stored in localStorage for persistent sessions

## Security Features

✅ Password validation (Django's built-in validators)
✅ Password confirmation matching
✅ Unique username and email constraints
✅ Activation code required before account is active
✅ JWT token-based authentication
✅ Client-side and server-side validation
✅ Secure password hashing

## Testing the Flow

### 1. Start Backend
```bash
make start
# or
docker-compose up
```

### 2. Start Frontend
```bash
cd bgx-fe
npm install  # First time only
npm run dev
```

### 3. Register a User
1. Navigate to `http://localhost:5173`
2. Click "Register"
3. Fill in the form:
   - First Name: John
   - Last Name: Doe
   - Username: johndoe
   - Email: john@example.com
   - Password: SecurePass123
   - Confirm Password: SecurePass123
4. Click "Create Account"
5. Copy the activation code shown

### 4. Activate Account
1. Click "Continue to Activation"
2. Paste the activation code
3. Click "Activate Account"
4. See success message and auto-redirect

## Database Check

You can verify activation in Django admin or via psql:

```bash
make psql
SELECT username, email, is_activated, activation_code FROM accounts_user;
```

## Future Enhancements

Potential improvements:
- [ ] Email delivery of activation codes
- [ ] Activation code expiration (24-48 hours)
- [ ] Resend activation code functionality
- [ ] Password reset flow
- [ ] Login component
- [ ] Protected routes requiring authentication
- [ ] User profile page
- [ ] Rider profile creation after activation

## API Documentation

View full API documentation at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Routes

### Frontend Routes
- `/` - Home (championships and races)
- `/race/:raceId` - Race detail with category results
- `/register` - User registration
- `/activate` - Account activation

### Backend API Routes
- `POST /api/users/` - User registration
- `POST /api/users/activate/` - Account activation
- `POST /api/auth/login/` - Login (JWT tokens)
- `POST /api/auth/refresh/` - Refresh JWT token
- `GET /api/users/me/` - Get current user info (authenticated)

## Troubleshooting

### "Activation code invalid"
- Check that the code was copied correctly
- Verify code exists in database
- Ensure account hasn't already been activated

### "Username already exists"
- Choose a different username
- Check database for existing users

### Frontend not connecting to backend
- Ensure backend is running on `http://localhost:8000`
- Check `.env` file for correct `VITE_API_URL`
- Verify CORS settings in Django

### Activation code not showing
- Check browser console for errors
- Verify backend endpoint is responding
- Check Django logs for errors

## Summary

✅ Complete registration flow with activation codes
✅ Beautiful, modern UI with Tailwind CSS
✅ Secure authentication with JWT tokens
✅ Mobile-responsive design
✅ User-friendly error handling
✅ Success animations and auto-redirects
✅ Copy-to-clipboard functionality
✅ Public API access for results viewing
✅ Protected endpoints for user management

The registration system is now fully functional and ready for testing! 🎉

