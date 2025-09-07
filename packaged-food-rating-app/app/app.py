import streamlit as st
from scoring import evaluate_product
from input_handler import lookup_product_by_barcode
from vision_handler import decode_barcode, extract_text_from_image, detect_ingredients_section
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="🥗 Food Health Analyzer")

st.title("🥗 Food Health Analyzer")
st.write("Scan a product barcode or upload a nutrition label to get a health score (0–100).")

method = st.radio("Choose input method:", ["Camera", "Barcode", "Upload Image"])

nutrients, ingredients = {}, ""

if method == "Camera":
    img_file = st.camera_input("Take a picture of the product", help="Hold the camera steady and ensure good lighting")
    if img_file:
        with st.spinner("Processing image..."):
            try:
                # Show debug information
                st.write("📷 Processing image...")
                image = Image.open(img_file)
                
                # Display the image
                st.image(image, caption="Captured Image", use_column_width=True)
                
                # Try to detect barcode
                barcodes = decode_barcode(image)
                
                if barcodes:
                    for barcode in barcodes:
                        st.success(f"✅ Found {barcode['type']} barcode: {barcode['data']} (using {barcode['method']} processing)")
                        product = lookup_product_by_barcode(barcode['data'])
                        if product:
                            st.subheader(product.get("product_name", "Unknown Product"))
                            nutrients = product.get("nutrients", {})
                            ingredients = product.get("ingredients_text", "")
                        else:
                            st.warning("Product not found in database")
                else:
                    st.warning("No barcode detected. Please try again with these tips:")
                    st.info("""
                    📸 Tips for better barcode scanning:
                    - Ensure good lighting
                    - Hold the camera steady
                    - Keep the barcode centered
                    - Avoid glare or shadows
                    - Try different angles
                    """)
                    
                    # Try to extract ingredients as fallback
                    ingredients = detect_ingredients_section(image)
                    if not ingredients:
                        ingredients = extract_text_from_image(img_file)
                    if ingredients:
                        st.text_area("Extracted Text", ingredients, height=200)
                    
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
                st.info("Please try taking another picture")

elif method == "Barcode":
    barcode = st.text_input("Enter Barcode:")
    if barcode:
        product = lookup_product_by_barcode(barcode)
        if product:
            st.subheader(product.get("product_name", "Unknown Product"))
            nutrients = product.get("nutrients", {})
            ingredients = product.get("ingredients_text", "")
        else:
            st.error("❌ Product not found")

elif method == "Upload Image":
    uploaded = st.file_uploader("Upload Image", type=["jpg", "png"])
    if uploaded:
        try:
            # Display uploaded image
            image = Image.open(uploaded)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            
            # Try to detect barcode first
            barcodes = decode_barcode(image)
            if barcodes:
                st.success(f"Found barcode: {barcodes[0]['data']}")
                product = lookup_product_by_barcode(barcodes[0]['data'])
                if product:
                    st.subheader(product.get("product_name", "Unknown Product"))
                    nutrients = product.get("nutrients", {})
                    ingredients = product.get("ingredients_text", "")
            else:
                # Try to extract ingredients
                with st.spinner("Analyzing image..."):
                    ingredients = detect_ingredients_section(image)
                    if not ingredients:
                        ingredients = extract_text_from_image(uploaded)
                    st.text_area("Extracted Text", ingredients, height=200)
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            st.info("Please try uploading a different image")

if nutrients or ingredients:
    score, pros, cons, missing = evaluate_product(nutrients, ingredients)

    st.metric("Health Score", f"{score}/100")

    if pros:
        st.success("✅ Pros\n" + "\n".join([f"- {p}" for p in pros]))
    if cons:
        st.error("⚠️ Cons\n" + "\n".join([f"- {c}" for c in cons]))
    if missing:
        st.info("🔍 No data found for: " + ", ".join(missing))
