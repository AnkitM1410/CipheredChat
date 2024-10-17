from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utility import jwt_decode, generate_message_id, current_time, datetime_form_datetime_str
from db import save_message, available_chat_channels, fetch_messages, user_in_channel, create_new_channel, auth_session, chat_channel_available

router = APIRouter()
connected_users = {}

router.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str, session_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {session_id: websocket}
        self.active_connections[user_id][session_id] = websocket

    def disconnect(self, user_id: str, session_id: str):
        if user_id in self.active_connections:
            if session_id in self.active_connections[user_id]:
                del self.active_connections[user_id][session_id]
                print(f"Disconnected {user_id}-{session_id}")
    
    async def send_message_to(self, payload: dict, send_to: str, session_id: str = '', except_session_id: str = ''):
        if send_to in self.active_connections:
            print(self.active_connections[send_to].keys())
            if session_id:
                if session_id in self.active_connections[send_to]:
                    await self.active_connections[send_to][session_id].send_json(payload)
            elif except_session_id:
                for session_id_key in self.active_connections[send_to].keys():
                    if except_session_id!=session_id_key:
                        await self.active_connections[send_to][session_id_key].send_json(payload)
            else:
                for user_sessions in self.active_connections[send_to].values():
                    await user_sessions.send_json(payload)

WS_ = ConnectionManager()


@router.get("/")
async def dashboard(request: Request, response: Response):
    user_id = auth_session(request.cookies.get("session_id", None))
    if user_id:
        return templates.TemplateResponse(request=request, name="dashboard.html")
    return RedirectResponse("/auth")

@router.get("/openChats")
async def open_chats(request: Request, response: Response):
    user_id = auth_session(request.cookies.get("session_id", None))
    if user_id:
        status, open_chat_list = available_chat_channels(user_id=user_id)
        return JSONResponse(content={"status": status, "open_chat_list": open_chat_list})
    return JSONResponse(content={"status": False, "msg": "Invalid Cookie"})

@router.get("/get_chat/{chat_id}")
async def get_chat(request: Request, response: Response, chat_id):
    user_id = auth_session(request.cookies.get("session_id", None))
    if user_id:
        if user_in_channel(user_id=user_id, chat_id=chat_id):
            chats = fetch_messages(chat_id=chat_id)
            return JSONResponse(content={"status": True, "chats": chats})
        else:
            return JSONResponse(content={"status": False, "msg": "Invalid Chat_id or Not a member of the Chat."})
    return JSONResponse(content={"status": False, "msg": "Invalid Cookie"})

@router.get('/chat_channel_available/{user_id}')
async def check_user_id(user_id: str):
    return chat_channel_available(user_id=user_id.lower())


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_data = auth_session(websocket.cookies.get("session_id", None), metadata=True)
    if not user_data:
        await websocket.send_json({'type': 'session_expired'})
        await websocket.close(code=1008)
        return
    
    user_id = user_data["user_id"]
    session_id = user_data["session_id"]
    expires_at = datetime_form_datetime_str(user_data['expires_at'])

    await WS_.connect(websocket, user_id, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            if data:
                if current_time()>expires_at:
                    await WS_.send_message_to(payload= {'type': 'session_expired'}, send_to=user_id)
                    break

                if data['func']=='msg':
                    print(data['temp_message_id'])
                    message_id = generate_message_id()
                    payload = {'type': 'msg','message': data['message'], 'message_id': message_id, 'chat_id': data['chat_id'], 'send_by': user_id, 'send_at': data['send_at']}
                    await save_message(chat_id=data['chat_id'], message_id=message_id, message=data['message'], send_by=user_id, send_at=data['send_at'])

                    # Sends message to all the WS of the reciver
                    await WS_.send_message_to(payload=payload, send_to=data['send_to'])

                    # Sends message to all the other session of original-poster, except for the one who sent it
                    await WS_.send_message_to(payload=payload, send_to=user_id, except_session_id=session_id)

                    # Sends the original session the message_id.
                    await WS_.send_message_to(
                        payload={'type': 'msg_id', 
                                 'temp_message_id': data['temp_message_id'],
                                 'message_id': message_id, 
                                 'send_at': data['send_at']},
                        send_to=user_id,
                        session_id=session_id
                    )


                elif data['func']=='new_chat':
                    new_chat_id = create_new_channel(user_id1=user_id, user_id2=data['user_id'])
                    if new_chat_id:
                        payload = {"type": 'new_chat', "chat_id": new_chat_id}
                        await WS_.send_message_to(send_to=user_id, payload=payload | {'send_to': data['user_id']})
                        await WS_.send_message_to(send_to=data['user_id'], payload=payload | {"send_to": user_id})
                    else:
                        await WS_.send_message_to(send_to=user_id, payload={"type": "err", "msg": "Something went wrong while adding new User."})
            else:
                payload = {'type': 'err', 'msg': 'Invalid func request.'}
                await WS_.send_message_to(payload=payload, send_to=user_id)
                    
    except WebSocketDisconnect:     
        WS_.disconnect(user_id=user_id, session_id=session_id)
    finally:
        # Ensure disconnection happens even if an unexpected error occurs
        WS_.disconnect(user_id=user_id, session_id=session_id)
