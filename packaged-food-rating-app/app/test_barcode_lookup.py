import sys
import os
import requests
import json
from pprint import pformat
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.input_handler import lookup_product_by_barcode

def try_barcodespider(barcode):
    """Try BarcodeSpider API as another data source"""
    url = f"https://barcodespider.com/api/{barcode}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"BarcodeSpider API error: {str(e)}")
    return None

def suggest_add_to_openfoodfacts(barcode):
    """Provide instructions to add product to OpenFoodFacts"""
    add_url = f"https://world.openfoodfacts.org/cgi/product.pl?type=add&code={barcode}"
    print("\nProduct not found in OpenFoodFacts database.")
    print("You can help by adding it:")
    print(f"1. Visit: {add_url}")
    print("2. Create an account if you don't have one")
    print("3. Add product information and photos")
    print("\nWould you like to open the add product page? (y/n)")
    if input().lower() == 'y':
        os.system(f'"$BROWSER" {add_url}')

def test_barcode_lookup(barcode):
    """Test barcode lookup with multiple data sources"""
    print(f"\n=== Testing barcode: {barcode} at {datetime.now()} ===\n")

    # Try OpenFoodFacts first
    print("1. Checking OpenFoodFacts...")
    result = lookup_product_by_barcode(barcode)
    
    if not result:
        print("Not found in OpenFoodFacts")
        suggest_add_to_openfoodfacts(barcode)
        
        # Try UPC Item DB
        print("\n2. Checking UPCitemdb...")
        upcitemdb_url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
        try:
            response = requests.get(upcitemdb_url, timeout=5)
            if response.status_code == 200:
                items = response.json().get('items', [])
                if items:
                    print(f"Found product: {items[0].get('title')}")
                    print("Details:")
                    print(json.dumps(items[0], indent=2))
                else:
                    print("No products found in UPCitemdb")
        except Exception as e:
            print(f"UPCitemdb API request failed: {str(e)}")

        # Try BarcodeSpider
        print("\n3. Checking BarcodeSpider...")
        spider_result = try_barcodespider(barcode)
        if spider_result:
            print("Found product in BarcodeSpider:")
            print(json.dumps(spider_result, indent=2))
        else:
            print("Not found in BarcodeSpider")
    else:
        # Display OpenFoodFacts data
        print("Found in OpenFoodFacts:")
        print(f"Name: {result.get('product_name', 'Unknown')}")
        print("\nNutrition Facts (per 100g):")
        nutrients = result.get('nutrients', {})
        for key in ['energy', 'proteins', 'carbohydrates', 'fat', 'sugars', 'saturated-fat']:
            if key in nutrients:
                value = nutrients[f'{key}_100g'] if f'{key}_100g' in nutrients else nutrients[key]
                unit = nutrients.get(f'{key}_unit', 'g')
                print(f"{key.capitalize()}: {value} {unit}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        barcode = sys.argv[1]
    else:
        barcode = "012000000133"  # Default test barcode
    test_barcode_lookup(barcode)