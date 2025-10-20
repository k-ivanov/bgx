# Rider Account Claim Flow

## Overview

The BGX Racing Platform uses a **rider-matching registration flow** where riders must match with their pre-existing profiles in the system before they can create login credentials. This ensures that only legitimate, registered riders can create accounts.

---

## 🎯 Concept

### Traditional Registration vs Rider Claim Flow

**Traditional Registration:**
- User creates account from scratch
- No verification of rider identity
- Anyone can register

**Rider Claim Flow (BGX):**
- Rider profiles pre-exist in system (imported from CSV)
- Users must match with their existing profile
- Claim account by setting username/password
- Verified rider identity

---

## 📋 User Flow

### Step 1: Find Your Profile
User enters their information to find matching rider profiles:

**Required:**
- First Name
- Last Name

**Optional (helps narrow search):**
- License Number
- Date of Birth

### Step 2: Select Your Profile
If multiple matches are found, user selects their correct profile:
- Shows rider name
- Shows license number (if available)
- Shows club affiliation
- Shows licensed status

### Step 3: Claim Account
User sets up login credentials for the matched profile:
- Choose username
- Enter email address
- Create password
- Confirm password

### Step 4: Activation
System provides activation code:
- User receives activation code
- Must activate account before logging in
- Activation code sent to entered email (in production)

---

## 🔧 Technical Implementation

### Backend (Django)

#### New Field: `is_claimed`
Added to `User` model to track if account has been claimed:

```python
is_claimed = models.BooleanField(
    default=False,
    help_text="Whether this pre-existing user account has been claimed by the rider"
)
```

#### New Serializers

**`RiderMatchSerializer`**
```python
class RiderMatchSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    license_number = serializers.CharField(required=False, allow_blank=True, max_length=50)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
```

**`ClaimAccountSerializer`**
```python
class ClaimAccountSerializer(serializers.Serializer):
    rider_id = serializers.IntegerField(required=True)
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
```

#### New API Endpoints

**1. Match Rider**
```
POST /api/users/match_rider/
```

Searches for riders matching the provided criteria.

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "license_number": "12345",  // optional
  "date_of_birth": "1990-01-01"  // optional
}
```

**Response:**
```json
{
  "matches": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "license_number": "12345",
      "club": "Racing Club",
      "is_licensed": true,
      "username": "john.doe.1"
    }
  ],
  "message": "Found 1 matching rider(s)"
}
```

**2. Claim Account**
```
POST /api/users/claim_account/
```

Claims an existing user account for a matched rider.

**Request:**
```json
{
  "rider_id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "password2": "SecurePass123"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_rider": true,
    "is_activated": false
  },
  "rider": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "license_number": "12345",
    "club": "Racing Club"
  },
  "activation_code": "abc123xyz...",
  "message": "Account claimed successfully! Please use the activation code to activate your account."
}
```

#### Business Logic

**Match Rider Logic:**
1. Search for riders by first name AND last name (case-insensitive)
2. If license number provided, filter by license number
3. If date of birth provided, filter by date of birth
4. Only return riders whose user accounts are NOT claimed (`is_claimed=False`)
5. Return list of matching riders with details

**Claim Account Logic:**
1. Verify rider exists by `rider_id`
2. Get associated user account
3. Check if account is already claimed → reject if yes
4. Check if username is available → reject if taken
5. Check if email is available → reject if taken
6. Update user account:
   - Set new username
   - Set email
   - Set password (hashed)
   - Mark as `is_claimed=True`
   - Mark as `is_rider=True`
   - Generate activation code
7. Return user data and activation code

### Frontend (React)

#### Multi-Step Form

**State Management:**
```javascript
const [step, setStep] = useState(1) // 1: Match, 2: Select, 3: Claim, 4: Success

// Step 1: Match data
const [matchData, setMatchData] = useState({
  first_name: '',
  last_name: '',
  license_number: '',
  date_of_birth: '',
})

// Step 2: Matched riders
const [matchedRiders, setMatchedRiders] = useState([])
const [selectedRider, setSelectedRider] = useState(null)

// Step 3: Claim data
const [claimData, setClaimData] = useState({
  username: '',
  email: '',
  password: '',
  password2: '',
})

// Step 4: Success data
const [activationCode, setActivationCode] = useState(null)
```

**API Integration:**
```javascript
// Step 1: Search for riders
const response = await matchRider(matchData)

// Step 3: Claim account
const response = await claimAccount({
  rider_id: selectedRider.id,
  ...claimData
})
```

---

## 🔒 Security Features

### Prevents Duplicate Claims
- Once claimed, account cannot be claimed again
- `is_claimed` flag prevents re-claiming
- Shown in admin panel

### Username/Email Validation
- Username must be unique across system
- Email must be unique across system
- Validated server-side

### Password Security
- Minimum 8 characters
- Django password validators applied
- Hashed using Django's secure hashing

### Activation Required
- Account must be activated before use
- Activation code required
- Prevents immediate unauthorized access

---

## 👨‍💼 Admin Panel

### New Filter
Admin can filter users by `is_claimed` status:
- **Claimed** - Account has been claimed by rider
- **Unclaimed** - Pre-existing account not yet claimed

### New Badge
`is_claimed_badge` shows claim status:
- ✓ Claimed (blue)
- ○ Unclaimed (gray)

### Admin View
```
Username | Email | Name | Claimed | Activated | Is Rider | ...
---------|-------|------|---------|-----------|----------|----
john.doe.1 | - | John Doe | ○ Unclaimed | ⚠ Pending | ✓ | ...
johndoe | john@... | John Doe | ✓ Claimed | ✓ Activated | ✓ | ...
```

---

## 📊 Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Import Riders from CSV                     │
│                                                                │
│  Creates: User (unclaimed) + Rider                           │
│  Username: firstname.lastname.number (placeholder)            │
│  Password: Random (unusable)                                  │
│  is_claimed: False                                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                  Rider Visits Registration Page               │
│                                                                │
│  Step 1: Enters name, license number (optional)              │
│  API: POST /api/users/match_rider/                           │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                  System Finds Matching Riders                 │
│                                                                │
│  Query: first_name + last_name (+ optional filters)          │
│  Filter: is_claimed=False (only unclaimed accounts)          │
│  Returns: List of matching riders                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Rider Selects Their Profile                │
│                                                                │
│  Shows: Name, License, Club                                   │
│  Rider clicks on correct profile                             │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Rider Claims Account                       │
│                                                                │
│  Step 3: Sets username, email, password                      │
│  API: POST /api/users/claim_account/                         │
│                                                                │
│  Updates User:                                                │
│    - username: johndoe                                        │
│    - email: john@example.com                                 │
│    - password: (hashed)                                       │
│    - is_claimed: True                                         │
│    - activation_code: (generated)                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Activation Code Shown                      │
│                                                                │
│  Rider receives activation code                              │
│  Must activate before login                                   │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Rider Activates Account                    │
│                                                                │
│  API: POST /api/users/activate/                              │
│  Updates: is_activated: True                                 │
│  Returns: JWT tokens                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

### Test Scenarios

**1. Happy Path:**
- Rider enters correct name
- System finds match
- Rider claims account
- Activates successfully

**2. Multiple Matches:**
- Rider enters name (common name)
- System finds multiple riders
- Rider selects correct one
- Claims successfully

**3. No Matches:**
- Rider enters incorrect name
- System finds no matches
- Shows error message
- Prompts to contact admin

**4. Already Claimed:**
- Rider tries to claim account
- Account already claimed
- Shows error
- Prompts to use password reset

**5. Username Taken:**
- Rider selects profile
- Tries username that's taken
- System rejects
- Rider tries different username

---

## 📝 User Instructions

### For Riders

**"How do I register?"**

1. **Find Your Profile:**
   - Go to Registration page
   - Enter your first and last name exactly as they appear in race results
   - If you have a license number, enter it to narrow the search
   - Click "Find My Profile"

2. **Select Your Profile:**
   - If multiple profiles are found, select yours
   - Check the license number and club to confirm it's you
   - Click on your profile

3. **Set Up Your Account:**
   - Choose a username (unique)
   - Enter your email address
   - Create a secure password (minimum 8 characters)
   - Confirm your password
   - Click "Claim Account"

4. **Activate Your Account:**
   - Save the activation code shown
   - Go to Activation page
   - Enter your activation code
   - Your account is now active!

**"What if I can't find my profile?"**
- Make sure you're entering your name exactly as it appears in race results
- Try without entering a license number
- Contact the system administrator if you still can't find your profile

**"What if it says my account is already claimed?"**
- Someone may have already claimed your account
- Contact the system administrator immediately
- Use the password reset feature if you forgot your password

---

## 🔄 Migration from Old System

If you had an old registration system and want to migrate:

### Step 1: Mark existing claimed accounts
```python
# In Django shell or migration
User.objects.filter(
    is_rider=True,
    is_activated=True
).update(is_claimed=True)
```

### Step 2: Keep unclaimed accounts available
```python
# Unclaimed accounts remain is_claimed=False
# These can be claimed by riders
```

---

## 🚀 Deployment Checklist

- [ ] Run migrations for `is_claimed` field
- [ ] Update admin panel to show claim status
- [ ] Deploy new API endpoints
- [ ] Deploy updated frontend
- [ ] Update user documentation
- [ ] Train support staff on new flow
- [ ] Monitor for issues in first week

---

## 📚 Related Documentation

- `REGISTRATION_FLOW.md` - Original registration documentation
- `bgx-api/accounts/models.py` - User model with `is_claimed` field
- `bgx-api/accounts/views.py` - `match_rider` and `claim_account` endpoints
- `bgx-fe/src/components/Register.jsx` - Multi-step registration form

---

## 💡 Benefits

### For the Platform
- ✅ Verified rider identity
- ✅ Prevents fake registrations
- ✅ Links account to existing race history
- ✅ Maintains data integrity

### For Riders
- ✅ Access to their race history
- ✅ Claim their existing results
- ✅ One account, all races
- ✅ Easy profile management

### For Admins
- ✅ Reduced support tickets
- ✅ Easy to track claimed vs unclaimed
- ✅ Better data quality
- ✅ Clear audit trail

---

## 🎯 Future Enhancements

- Email verification during matching
- SMS verification option
- Automatic email with activation code
- Photo verification for high-stakes accounts
- Integration with national racing federation databases
- Social proof (team verification)

---

This rider claim flow ensures that only legitimate riders can access the platform while maintaining a smooth user experience! 🏍️✨

