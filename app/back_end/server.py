import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .constants import DIRPATH_FRONT_END, DIRPATH_IMAGES
from .routes import api, home, ping

logger = logging.getLogger(name='uvicorn.error')


def get_app():
    fast_api_app = FastAPI(
        title='2048 Infinite WebApp',
        version='0.0.1',
        description='DESCRIPTION',
        contact={'name': 'Nick Langellier',
                 'email': input('email: ')},
        license_info={'name': 'GNU General Public License',
                      'url': 'https://www.gnu.org/licenses/gpl-3.0.en.html'}
    )

    fast_api_app.mount(
        path='/front-end',
        app=StaticFiles(directory=DIRPATH_FRONT_END),
        name='front-end'
    )
    fast_api_app.mount(
        path='/images',
        app=StaticFiles(directory=DIRPATH_IMAGES),
        name='images'
    )

    fast_api_app.include_router(router=home.router)
    fast_api_app.include_router(router=ping.router)
    fast_api_app.include_router(router=api.router)

    return fast_api_app


app = get_app()
