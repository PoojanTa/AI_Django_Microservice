import pathlib
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

BASE_DIR = pathlib.Path(__file__).parent
IMG_DIR = BASE_DIR / "images"
img_path = IMG_DIR / "img.png"

img = Image.open(img_path)

preds = pytesseract.image_to_string(img )
predictions = [x for x in preds.split("\n") if x.strip() != ""]

print(predictions)


