from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

app = FastAPI()
app.mount(path='/front-end',
          app=StaticFiles(directory='front-end'),
          name='front-end')


@app.get('/')
def home():
    return FileResponse('front-end/index.html')


@app.get('/items/{item_id}')
def read_item(item_id: int, q: str | None = None):
    return {'item_id': item_id, 'q': q}
