import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .constants import DIRPATH_FRONT_END, DIRPATH_IMAGES
from .routes import router

app = FastAPI()
app.mount(path='/front-end',
          app=StaticFiles(directory=DIRPATH_FRONT_END),
          name='front-end')
app.mount(path='/images',
          app=StaticFiles(directory=DIRPATH_IMAGES),
          name='images')
app.include_router(router=router)

logger = logging.getLogger(name='uvicorn.error')
