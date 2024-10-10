from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from db import auth_user, user_exists, user_exists_in_verification, delete_verification_record, create_user, create_verification_record, is_user_id_available, verification_id_exist
from model import Login, Signup
from utility import jwt_encode, one_month_form_now, sha256, clean_email
from email_service import  send_signup_notifiction ,send_verification_email


router = APIRouter()

@router.post('/login')
async def login(request: Request, response: Response, login: Login):
    login.email_id=clean_email(login.email_id)
    login.password=sha256(login.password)[::-1]

    auth_status, user_info = auth_user(email_id=login.email_id, password=login.password)
    if auth_status:
        jwt_token = jwt_encode(payload={
            'user_id': user_info['user_id']
            })
        response.set_cookie(key="auth_token", value=jwt_token, max_age=60*60*24*7)
        response.set_cookie(key='user_id', value=user_info['user_id'], max_age=60*60*24*7)
        return {'status': True, 'msg': 'Login Succesfull.'}
    else:
        return {'status': False, 'msg': 'Invalid Credentials.'}


@router.post('/signup')
async def signup(request: Request, response: Response, signup: Signup):
    signup.email_id = clean_email(signup.email_id)

    if user_exists(signup.email_id):
        return {'status': False, 'msg': 'Email already in use.'}
    elif user_exists_in_verification(signup.email_id):
        return {'status': False, 'msg': f'Email already in use. Please verify your account using the Email sent to {signup.email_id}'}
    else:
        user_data = signup.model_dump()
        status, verification_id = create_verification_record(signup)
        if status:
            await send_verification_email(to_addr=user_data['email_id'], user_id=user_data['user_id'], base_url=str(request.base_url), verification_id=verification_id)
            return {'status': True, 'msg': 'Signup complete.'}
        else:
            return {'status': False, 'msg': 'Something went wrong.'}


@router.get('/user_id_available/{user_id}')
async def check_user_id(user_id: str):
    return is_user_id_available(user_id=user_id.lower())

# @router.get('/user_id_available/{email_id}')
# async def check_email_id(email_id: str):
#     return user_exists(email_id=email_id)


@router.get('/v/{verification_id}')
async def verify_and_create_user(requset: Request, responce: Response, verification_id):
    status, verification_data = verification_id_exist(verification_id=verification_id, return_data=True)
    msg = ""
    print(verification_data)
    if status:
        user_created: bool = create_user(user_data=verification_data)
        verification_record_deleted = delete_verification_record(verification_id=verification_id)
        if user_created and verification_record_deleted:
            await send_signup_notifiction(to_addr=verification_data["email_id"])
            auth_token = jwt_encode({"user_id": verification_data["user_id"], "expires_at": one_month_form_now()})
            responce.set_cookie(key="auth_token", value=auth_token)
            return RedirectResponse(url="/c")
    else:
        return HTMLResponse('''<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: black; color: white;  margin: 0; padding: 0; box-sizing: border-box;"><h2>Invalid Link or User Already Created.</h2><a href="/auth" style="color: white; margin-top: 10px;">SignUp/Login -></a></div>''')

@router.get("/x")
async def return_cookie(request: Request, response: Response):
    return request.cookies.get('auth_token')
