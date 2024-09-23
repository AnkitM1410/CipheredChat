from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from utility import sha256, generate_verification_id, one_day_form_now, is_valid_verification_id
from model import Signup
from functools import lru_cache
from datetime import datetime

sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

USERS_ = sb.table('Users') if sb else None
VERIFICATION_ = sb.table('Verification') if sb else None
CHAT_ = sb.table('Chats') if sb else None
MESSAGES_ = sb.table('Messages') if sb else None


def is_user_id_available(user_id: str): 
    """
    Checks both in USER and VERIFICATION table.
    """
    avaliable_in_users = 0 if USERS_.select('user_id').eq('user_id', user_id).execute().data else 1
    avaliable_in_verification = 0 if USERS_.select('user_id').eq('user_id', user_id).execute().data else 1

    if avaliable_in_users and avaliable_in_verification:
        return 1
    return 0

def user_exists(email_id: str):
    return True if USERS_.select('email_id').eq('email_id', email_id).execute().data else False

def user_exists_in_verification(email_id: str):
    return True if VERIFICATION_.select('email_id').eq('email_id', email_id).execute().data else False

def auth_user(email_id: str, password: str):
    email_id=email_id.lower()

    user_data = USERS_.select('password', 'user_id').eq('email_id', email_id).execute()
    if user_data.data:
        if user_data.data[0]['password']==password:
            del user_data.data[0]['password']
            return True, user_data.data[0]
    return False, None

def create_verification_record(signup: Signup):
    new_verification_id = generate_verification_id()
    
    # To Mitigate an (almost)Impossible condition.
    while not verification_id_exist(new_verification_id):
        new_verification_id = generate_verification_id()

    data, count = VERIFICATION_.insert(
        {
            'verification_id': new_verification_id,
            'user_id': signup.user_id,
            'email_id': signup.email_id,
            'first_name': signup.first_name,
            'last_name': signup.last_name,
            'password': sha256(signup.password)[::-1]
        }
    ).execute()

    if data:
        return True, new_verification_id
    else:
        return False, ''

def delete_verification_record(verification_id: str):
    responce = VERIFICATION_.delete().eq('verification_id', verification_id).execute()
    return True if responce else False

def verification_id_exist(verification_id: str, return_data: bool = False):
    '''
    Returns Exist(Bool) and UserData(Dict) if it exist. (In case the verification_id don't exit returns empty dict.)
    '''
    if is_valid_verification_id(verification_id):
        verification_data = VERIFICATION_.select('*').eq('verification_id', verification_id).execute()
        if verification_data.data:
            if return_data:
                return True, verification_data.data[0]
            else:
                return True

    if return_data:
        return False
    else:
        return False, None

def create_user(user_data):
    data, count = USERS_.insert(
        {
            'user_id': user_data.get("user_id"),
            'email_id': user_data.get("email_id"),
            'first_name': user_data.get("first_name", ""),
            'last_name': user_data.get("last_name", ""),
            'password': user_data.get("password")
        }
    ).execute()

    if data:
        return True
    else:
        return False
    
# Chat channel Mangement.
def available_chat_channels(user_id: str):
    chat_channels = CHAT_.select('*').or_(f"user1.eq.{user_id},user2.eq.{user_id}").execute()
    if chat_channels.data:
        payload = []
        for channel in chat_channels.data:
            channel_data = {}
            channel_data['chat_id'] = channel['chat_id']
            channel_data['send_to'] = channel['user2'] if channel['user1']==user_id else channel['user1']
            payload.append(channel_data)
        return True, payload

    return False, None

# Messages Management.

def fetch_messages(chat_id: str, after: str = None):
    query = MESSAGES_.select('message_id', 'message', 'sent_at').eq('chat_id', chat_id)
    if after:
        query = query.gt('sent_at', after)
    
    messages = query.execute()
    return messages.data

async def save_message(chat_id: str, message_id: str, message: str):
    data, count = MESSAGES_.insert(
        {   
            "chat_id": chat_id,
            "message_id": message_id,
            "message": message,
        }
    ).execute()

    if data:
        return True
    else:
        return False


if __name__ == "__main__":
    print(fetch_messages(chat_id='abc', after="2003-09-18T15:30:29"))