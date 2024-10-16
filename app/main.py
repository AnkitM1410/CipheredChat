from fastapi import  FastAPI, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from routes import chat, auth
from email_service import send_email
from utility import jwt_encode, jwt_decode
from db import user_exists, auth_session

app = FastAPI(debug=True)

app.include_router(chat.router, prefix="/c")
app.include_router(auth.router, prefix="/authentication")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

origins = ["http://192.168.29.53:6969, http://127.0.0.1:6969"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def home_page(request: Request, response: Response):
    return templates.TemplateResponse(request=request, name="home.html")
    
@app.get('/auth')
async def auth(request: Request):
    user_id = auth_session(request.cookies.get('session_id', None))
    if user_id:
        return RedirectResponse('/')
            
    return templates.TemplateResponse(request=request, name="auth.html")

@app.get("/TnC")
async def TnC(request: Request):
    return templates.TemplateResponse(request=request, name="terms_and_conditions.html")

@app.get("/welcome")
async def TnC(request: Request):
    return templates.TemplateResponse(request=request, name="welcome.html")

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return templates.TemplateResponse(request=request, name="404.html")


    