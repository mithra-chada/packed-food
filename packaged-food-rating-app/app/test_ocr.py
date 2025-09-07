from PIL import Image
import pytesseract

# Optional: print Tesseract version
print("Tesseract version:", pytesseract.get_tesseract_version())

# OCR test
img = Image.open("nu-facts.jpg")  # Make sure this image is in your project
text = pytesseract.image_to_string(img)
print("--- OCR Output ---")
print(text)