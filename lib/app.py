from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from lib.config import www_path

app = FastAPI()
app.mount('/', StaticFiles(directory=www_path()), name='static')
