import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .constants import DIRPATH_FRONT_END, DIRPATH_IMAGES
from .routes import game, home, leader_board

app = FastAPI()
app.mount(path='/front-end',
          app=StaticFiles(directory=DIRPATH_FRONT_END),
          name='front-end')
app.mount(path='/images',
          app=StaticFiles(directory=DIRPATH_IMAGES),
          name='images')
app.include_router(router=home.router)
app.include_router(router=game.router)
app.include_router(router=leader_board.router)

logger = logging.getLogger(name='uvicorn.error')
