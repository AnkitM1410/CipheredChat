from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Database - SupaBase Keys
SUPABASE_URL = getenv('SUPABASE_URL')
SUPABASE_KEY = getenv('SUPABASE_KEY')

# Google Email App Credentials
EMAIL_SENDER = getenv("EMAIL_SENDER")
EMAIL_SENDER_APP_PASSWORD = getenv("EMAIL_SENDER_APP_PASSWORD")

JWT_SECRET = getenv("JWT_SECRET")
JWT_ALGORITHM = getenv("JWT_ALGORITHM")