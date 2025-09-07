import requests
from PIL import Image
import pytesseract

def extract_text_from_image(image_file):
    """Extract text from uploaded nutrition label image"""
    img = Image.open(image_file)
    text = pytesseract.image_to_string(img)
    return text.strip()

def lookup_product_by_barcode(barcode: str):
    """Fetch product data from OpenFoodFacts"""
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    data = response.json()
    if data.get('status') == 0:
        return None
    
    return {
        "product_name": data['product'].get('product_name', ''),
        "ingredients_text": data['product'].get('ingredients_text', ''),
        "nutrients": data['product'].get('nutriments', {})
    }
