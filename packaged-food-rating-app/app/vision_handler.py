import cv2
import numpy as np
from pyzbar import pyzbar
import pytesseract
from PIL import Image
import imutils

def decode_barcode(image):
    """Detect and decode barcodes/QR codes in image with enhanced preprocessing"""
    # Convert to OpenCV format if PIL Image
    if isinstance(image, Image.Image):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Resize image while maintaining aspect ratio
    height, width = image.shape[:2]
    target_width = 1000
    ratio = target_width / width
    dim = (target_width, int(height * ratio))
    image = cv2.resize(image, dim)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Enhanced preprocessing pipeline
    # 1. Noise reduction
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # 2. Increase contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrasted = clahe.apply(denoised)
    
    # 3. Thresholding
    thresh = cv2.threshold(contrasted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # 4. Morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    # Try different image processing combinations
    images_to_try = [
        ("original", gray),
        ("denoised", denoised),
        ("contrasted", contrasted),
        ("threshold", thresh),
        ("morphed", morphed)
    ]
    
    results = []
    for name, img in images_to_try:
        barcodes = pyzbar.decode(img)
        if barcodes:
            for barcode in barcodes:
                data = barcode.data.decode("utf-8")
                type = barcode.type
                results.append({
                    "data": data,
                    "type": type,
                    "method": name
                })
    
    return results

def extract_text_from_image(image_file, preprocess=True):
    """Enhanced text extraction with preprocessing"""
    # Handle different input types
    if isinstance(image_file, Image.Image):
        image = cv2.cvtColor(np.array(image_file), cv2.COLOR_RGB2BGR)
    elif isinstance(image_file, np.ndarray):
        image = image_file
    else:
        # Handle file-like objects (e.g., StreamingUploadedFile)
        image_data = np.frombuffer(image_file.getvalue(), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    
    if preprocess:
        # Resize while maintaining aspect ratio
        image = imutils.resize(image, width=1000)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Thresholding to handle different lighting conditions
        thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Dilation to enhance text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        # Convert to PIL Image for Tesseract
        pil_image = Image.fromarray(dilated)
    else:
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Extract text
    text = pytesseract.image_to_string(pil_image)
    
    return text.strip()

def detect_ingredients_section(image):
    """Detect and extract the ingredients section from product packaging"""
    # Convert to OpenCV format if needed
    if isinstance(image, Image.Image):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    elif isinstance(image, np.ndarray):
        image = image.copy()
    else:
        # Handle file-like objects
        image_data = np.frombuffer(image.getvalue(), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    
    # Create a copy for visualization
    output = image.copy()
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply OCR to detect text regions
    results = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    
    ingredients_box = None
    for i in range(len(results["text"])):
        text = results["text"][i].lower().strip()
        # Look for common ingredients section headers
        if text in ["ingredients", "ingredients:", "ingredients list"]:
            x = results["left"][i]
            y = results["top"][i]
            w = results["width"][i]
            h = results["height"][i]
            # Expand box to include ingredients list
            ingredients_box = (x, y, x + w, y + h * 5)  # Assume ingredients take up 5x header height
            break
    
    if ingredients_box:
        # Extract and process ingredients section
        x1, y1, x2, y2 = ingredients_box
        ingredients_image = image[y1:y2, x1:x2]
        return extract_text_from_image(ingredients_image)
    
    return None