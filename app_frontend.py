from typing import Union,Annotated
from pydantic import BaseModel
from fastapi import Cookie, FastAPI, Request, Response, Depends, Form, status, WebSocket
from app_database import App_DB
from fastapi.responses import RedirectResponse, FileResponse
from app_backend import (USER, check_login, verify_token, RequiresLoginException, disconnect_user, get_plotly_graphe,
                         change_favorite, Fav_Modification, training, selected_index, manager)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from training_pipeline import (start_training, keys_selected_index, selected_index,
                               import_training_result, load_fresh_data, projections)
import asyncio
app = FastAPI()
favicon_path = 'favicon.ico'


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



@app.get('/favicon.ico', include_in_schema=False)
async def get_favicon():
    return FileResponse(favicon_path)

@app.exception_handler(RequiresLoginException)
async def exception_handler(request: Request, exc: RequiresLoginException) -> Response:
    return RedirectResponse(url='/login')


@app.get("/login")
async def get_login(request: Request):
    return templates.TemplateResponse(request=request, name="identification.html", context={"error": None})


@app.post("/login")
async def post_login(email: Annotated[str, Form()], pwd: Annotated[str, Form()], request: Request):
    response = check_login(email, pwd)
    if response == 'user not fund':
        return templates.TemplateResponse(request=request, name="identification.html",
                                          context={"error": "Utilisateur inconue"})
    if response == 'bad password':
        return templates.TemplateResponse(request=request, name="identification.html",
                                          context={"error": "Mot de passe erronée"})
    else:
        return response


@app.get("/dashboard")
async def get_dashboard(request: Request, should_redirect: bool = Depends(verify_token)):

    plotly_graphe, fav = get_plotly_graphe(request)
    return templates.TemplateResponse(request=request, name="main.html",
                                      context={'select_input': selected_index,
                                               'graphe_selected': f'plotly_graphe/{plotly_graphe}.html',
                                               'table_selected': f'table/tab_{plotly_graphe}.html',
                                               'favorite_index': fav})


@app.get("/")
async def get_root():
    return {"Hello": "World"}


@app.get("/disconnect")
async def get_disconnect(request: Request):
    redirect_response = RedirectResponse(url='/login')
    redirect_response = disconnect_user(request, redirect_response)
    return redirect_response


@app.get("/cookie")
async def get_cookie(request: Request): #, should_redirect: bool = Depends(verify_token)):
    return request.cookies


@app.post("/change_favorite")
async def post_change_favorite(fav: Fav_Modification, request: Request):
    print(fav)
    change_favorite(request, fav)

@app.post("/change_graphe")
async def get_root(index: Annotated[str, Form()], request: Request, should_redirect: bool = Depends(verify_token)):
    print(index)
    return templates.TemplateResponse(request=request, name=f"plotly_graphe/{index}.html")

@app.get("/train")
async def get_train(request: Request):
    #training().delay()
    return templates.TemplateResponse(request=request, name=f"loading_bar.html")

@app.websocket("/dashboard/ws/{index}")
async def websocket_train(websocket: WebSocket, index: str):
    await training(websocket, key=index)

    index="^XAX"
    #return templates.TemplateResponse(request=request, name=f"loading_bar.html")

@app.post("/change_table")
async def get_root(index: Annotated[str, Form()], request: Request, should_redirect: bool = Depends(verify_token)):
    print(index)
    return templates.TemplateResponse(request=request, name=f"table/tab_{index}.html")

