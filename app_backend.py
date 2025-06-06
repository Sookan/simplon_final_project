from typing import Union
from pydantic import BaseModel
from fastapi import Cookie, FastAPI, Request, Response, Depends, status, WebSocket
from app_database import App_DB
from fastapi.responses import RedirectResponse
import sys
import asyncio
sys.path.append('../patchTST/')

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from training_pipeline import (start_training, keys_selected_index, selected_index,
                               import_training_result, load_fresh_data, projections)



class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_prgress_message(self, progress: int, message: str, websocket: WebSocket):
        await websocket.send_json({'progess': progress, 'message': message})

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

class USER(BaseModel):
    email: str
    token: Union[str, None] = None
    user_id: Union[int, None] = None

class Fav_Modification(BaseModel):
    index: Union[str, None]
    how: Union[str, None]

class RequiresLoginException(Exception):
    pass


def check_login(email, psw):
    db = App_DB()
    db_responce = db.check_user_password(email, psw)
    if db_responce is None:
        return "user not fund"
    elif not (db_responce[1] is None):
        user_id, token, email = db_responce
        user = USER(user_id=user_id, token=token, email=email)
        response = RedirectResponse(url='/dashboard', status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="access_token", value=token)
        response.set_cookie(key="user_id", value=user_id)
        return response
    else:
        return "bad password"


def disconnect_user(request: Request, response: RedirectResponse):
    cookies = request.cookies
    db = App_DB()
    db.delete_user_token(cookies["user_id"], cookies["access_token"])
    response.delete_cookie("access_token")
    response.delete_cookie("user_id")
    return response


def get_plotly_graphe(request: Request):
    cookies = request.cookies
    db = App_DB()
    fav = db.get_user_fav(cookies["user_id"], cookies["access_token"])
    print(fav)
    if fav is None:
        return '^FCHI', "pas de favorie"
    else:
        return fav[0], fav[0]



def verify_token(request: Request):
    cookies = request.cookies
    if ('user_id' not in cookies or 'access_token' not in cookies):
        raise RequiresLoginException

    db = App_DB()
    db_responce = db.check_user_token(cookies['user_id'], cookies['access_token'])
    if db_responce is None:
        raise RequiresLoginException


def change_favorite(request: Request, fav: Fav_Modification):
    cookies = request.cookies
    db = App_DB()
    if fav.how.lower() == 'del':
        db.delete_user_fav(cookies['user_id'], cookies['access_token'])
    elif fav.how.lower() == 'change':
        db.change_user_fav(cookies['user_id'], cookies['access_token'], fav.index)

async def training(websocket, key):
    await manager.connect(websocket)
    await asyncio.sleep(0.1)
    await manager.send_prgress_message(0, "chargement index...", websocket)
    await asyncio.sleep(0.1)
    load_fresh_data([key], pipeline_path="../patchTST/")
    i = 1
    for pred_len in projections:
        await manager.send_prgress_message(10*i, f"projection à j+{pred_len}...", websocket)
        await asyncio.sleep(0.1)
        i += 1
        start_training(key, pred_len=pred_len, seq_len=max(30, pred_len), pipeline_path="../patchTST/", target_path="")
    await manager.send_prgress_message(90, f"importation...", websocket)
    await asyncio.sleep(0.1)
    import_training_result(key, projections, pipeline_path="../patchTST/")
    await manager.send_prgress_message(100, f"terminé", websocket)
    await asyncio.sleep(0.1)
    await manager.disconnect(websocket)
    await asyncio.sleep(0.1)

async def redirect() -> bool:
    raise RequiresLoginException


