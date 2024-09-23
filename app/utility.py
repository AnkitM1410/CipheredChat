"""
Containes all the minor independent functions
"""

# Clean Email
def clean_email(email: str):
    local_part, domain = email.split('@')
    cleaned_local_part = local_part.split('+')[0]
    cleaned_email = f"{cleaned_local_part}@{domain}"
    return cleaned_email.lower()


# Calculation SHA256 Hash
import hashlib
sha256 = lambda input: hashlib.sha256(input.encode()).hexdigest()


# JWT Token Functions
import jwt
from config import  JWT_SECRET, JWT_ALGORITHM

# Checks if cookies/auth_token has all the required feilds
check_auth = lambda auth_token: True if auth_token.get('user_id', None) else False

jwt_encode = lambda payload: jwt.encode(payload=payload, key=JWT_SECRET, algorithm=JWT_ALGORITHM)

def jwt_decode(jwt_token: str):
    auth_token = jwt.decode(jwt=jwt_token, key=JWT_SECRET, algorithms=JWT_ALGORITHM)
    if check_auth(auth_token=auth_token):
        return True, auth_token
    else:
        return False, ''



# Generates Form-ID
import random
uuid_pool = '0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
generate_uuid = lambda: ''.join(random.choice(uuid_pool) for _ in range(5))

# Chat and Message ID
generate_message_id = lambda: ''.join(random.choice(uuid_pool) for _ in range(6))
generate_chat_id = lambda: ''.join(random.choice(uuid_pool) for _ in range(4))

# Generate Verification_id
import re
generate_verification_id = lambda: generate_uuid()+'-'+generate_uuid()+generate_uuid()+'-'+generate_uuid()

def is_valid_verification_id(verification_id: str):
    pattern = r"^[a-zA-Z0-9]{5}-[a-zA-Z0-9]{10}-[a-zA-Z0-9]{5}$"
    return bool(re.fullmatch(pattern, verification_id))

# Manages Time with time-zone
from datetime import datetime, timedelta, timezone
def return_datetime_form_datetime_str(datetime_str):
    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')

def current_time():
    return datetime.now(timezone.utc)

def one_day_form_now():
    new_datetime = datetime.now(timezone.utc) + timedelta(days=1)
    return new_datetime.strftime("%Y-%m-%d %H:%M:%S.%f%z")

def one_month_form_now():
    new_datetime = datetime.now(timezone.utc) + timedelta(weeks=4)
    return new_datetime.strftime("%Y-%m-%d %H:%M:%S.%f%z")
