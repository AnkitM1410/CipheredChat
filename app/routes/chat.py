from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utility import jwt_decode, generate_message_id
from db import save_message, available_chat_channels, fetch_messages, user_in_channel

router = APIRouter()
connected_users = {}

router.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
    
    async def send_message_to(self, payload: dict, send_to: str):
        if send_to in self.active_connections:
            print(f"SENDING {payload['type']} TO {send_to}")
            await self.active_connections[send_to].send_json(payload)

WS_ = ConnectionManager()


@router.get("/")
async def dashboard(request: Request, response: Response):
    auth_token = request.cookies.get("auth_token")
    if auth_token:
        auth_status, auth_json = jwt_decode(jwt_token=auth_token)
        if auth_status:
            return templates.TemplateResponse(request=request, name="dashboard.html")
    else:
        return RedirectResponse("/auth")

@router.get("/openChats")
async def open_chats(request: Request, response: Response):
    auth_token = request.cookies.get("auth_token")
    if auth_token:
        auth_status, auth_json = jwt_decode(jwt_token=auth_token)
        if auth_status:
            status, open_chat_list = available_chat_channels(user_id=auth_json.get('user_id'))
            return JSONResponse(content={"status": status, "open_chat_list": open_chat_list})
    return JSONResponse(content={"status": False, "msg": "Invalid Cookie"})

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    auth_token = websocket.cookies.get("auth_token", None)
    if not auth_token:
        await websocket.send_text("Authentication failed: No token provided")
        await websocket.close(code=1008)
        return

    auth_status, auth_json = jwt_decode(jwt_token=auth_token)
    if not auth_status:
        await websocket.send_text(f"Authentication failed: Invalid Auth Token.")
        await websocket.close(code=1008)
        return

    user_id = auth_json.get('user_id', None)
    if not user_id:
        await websocket.send_text("Authentication failed: No user ID in token")
        await websocket.close(code=1008)
        return

    await WS_.connect(websocket, user_id)
    try:
        print(WS_.active_connections.keys())
        while True:
            data = await websocket.receive_json()
            print(data)
            if data:
                if data['func']=='new_msg':
                    message_id = generate_message_id()
                    payload = {'type': 'msg','message': data['message'], 'message_id': message_id, 'chat_id': data['chat_id']}
                    await save_message(chat_id=data['chat_id'], message_id=message_id, message=data['message'], send_by=user_id, send_at=data['send_at'])
                    await WS_.send_message_to(payload=payload, send_to=data['send_to'])
                elif data['func']=='new_chat':
                    pass
            else:
                payload = {'type': 'error', 'msg': 'Invalid func request.'}
                await WS_.send_message_to(payload=payload, send_to=user_id)
                    
    except WebSocketDisconnect:     
        WS_.disconnect(user_id)
    finally:
        # Ensure disconnection happens even if an unexpected error occurs
        WS_.disconnect(user_id)

@router.get("/get_chat/{chat_id}")
async def get_chat(request: Request, response: Response, chat_id):
    auth_token = request.cookies.get("auth_token")
    if auth_token:
        auth_status, auth_json = jwt_decode(jwt_token=auth_token)
        if auth_status:
            if user_in_channel(user_id=auth_json['user_id'], chat_id=chat_id):
                chats = fetch_messages(chat_id=chat_id)
                print(chats)
                return JSONResponse(content={"status": True, "chats": chats})
            else:
                return JSONResponse(content={"status": False, "msg": "Invalid Chat_id or Not a member of the Chat."})
    return JSONResponse(content={"status": False, "msg": "Invalid Cookie"})


