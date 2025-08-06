from fastapi.testclient import TestClient
from app.main import app, BASE_DIR, UPLOAD_DIR, get_settings
import shutil
import time
import io
from PIL import Image, ImageChops
client = TestClient(app)



def test_get_home():
    response = client.get("/") # requests.get("") # python requests
    # assert response.text != "<h1>Hello world</h1>"
    assert response.status_code == 200
    assert  "text/html" in response.headers['content-type']


def test_prediction_upload():
    image_saved_path = (BASE_DIR / "images")
    settings = get_settings()
    for path in image_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = client.post("/", files={"file": open(path, 'rb')},headers={"Authorization": settings.app_auth_token})
        if img is not None:
            assert response.status_code == 200
            data = response.json()
            print(data)
            assert len(data.keys()) ==2
        else:
            assert response.status_code == 400

    time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)

def test_echo_upload():
    image_saved_path = (BASE_DIR / "images")

    for path in image_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None
        response = client.post("/img-echo/", files={"file": open(path, 'rb')})
        if img is not None:
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)
            Difference = ImageChops.difference(img, echo_img).getbbox()
            assert Difference is None
        else:
            assert response.status_code == 400

    time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)


