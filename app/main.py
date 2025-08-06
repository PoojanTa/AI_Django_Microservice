from fastapi import (FastAPI,Request,Header,Depends,HTTPException,File, UploadFile)
import pathlib
import uuid
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from functools import lru_cache
import os
import io
import pathlib
from pydantic_settings import BaseSettings
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class Settings(BaseSettings):
    app_auth_token: str
    debug: bool = False
    echo_active : bool  = False
    app_auth_token_prod:str= None
    skip_auth:bool =False

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()



DEBUG = get_settings().debug


BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def home_view(request : Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("home.html", {"request": request, "abc":123})


def verify_auth(authorization=Header(None), settings: Settings = Depends(get_settings)):
    if settings.debug and settings.skip_auth:
        return
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    label, token = authorization.split()
    if authorization != settings.app_auth_token:
        raise HTTPException(status_code=401, detail="Invalid authorization token")




@app.post("/")
async def prediction_view(file: UploadFile = File(...), authorization = Header(None) , settings: Settings = Depends(get_settings)):

    verify_auth(authorization, settings)
    file_bytes = io.BytesIO(await file.read())
    try:
        img = Image.open(file_bytes)
    except:
        raise HTTPException(status_code=400, detail=f"Invalid image file:")
    preds = pytesseract.image_to_string(img )
    predictions = [x for x in preds.split("\n") if x.strip() != ""]
    return {"predictions": predictions, "original":preds}



@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(file: UploadFile = File(...), settings: Settings = Depends(get_settings)):
    if  not settings.echo_active:
        raise HTTPException(status_code=400, detail="Invalid Endpoint try another")
    UPLOAD_DIR.mkdir(exist_ok=True)
    file_bytes = io.BytesIO(await file.read())
    try:
        img = Image.open(file_bytes)
    except:
        raise HTTPException(status_code=400, detail=f"Invalid image file:")
    fname = pathlib.Path(file.filename)
    fext = fname.suffix
    dest = UPLOAD_DIR / f"{uuid.uuid4()}{fext}"
    img.save(dest)
    return dest



#https://youtu.be/JxH7cdDCFwE?si=Oe417bseA8JdGqqY 49 mins


