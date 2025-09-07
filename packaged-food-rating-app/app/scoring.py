import json
import re
from pathlib import Path
from web_fallback import google_search

# Get absolute path to reference files
current_dir = Path(__file__).parent
references_dir = current_dir / "references"

# Load DBs using absolute paths
with open(references_dir / "fssai_regulations.json", "r", encoding="utf-8") as f:
    FSSAI_DB = json.load(f)

with open(references_dir / "nutrient_limits.json", "r", encoding="utf-8") as f:
    NUTRIENT_LIMITS = json.load(f)

def normalize_ingredient(text):
    """Normalize ingredient names for better matching"""
    # Remove percentages and parentheses
    text = re.sub(r'\(.*?\)', '', text)
    text = re.sub(r'\d+\.?\d*\s*%', '', text)
    
    # Convert E-numbers to standard format
    text = re.sub(r'[Ee]-?(\d{3}[a-zA-Z]?)', r'E\1', text)
    
    # Handle common variations
    replacements = {
        'acidity regulator': 'acidity regulators',
        'emulsifier': 'emulsifiers',
        'flavour enhancer': 'flavour enhancers',
        'stabilizer': 'stabilizers',
        'preservative': 'preservatives'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text.strip().lower()

def parse_ingredients(ingredients_text):
    """Break down complex ingredient list into individual ingredients"""
    # Split on commas and parentheses
    ingredients = re.split(r',|\(|\)', ingredients_text)
    
    # Clean up each ingredient
    cleaned = []
    for ing in ingredients:
        ing = ing.strip()
        if ing:
            # Extract E-numbers
            e_nums = re.findall(r'[Ee]-?(\d{3}[a-zA-Z]?)', ing)
            if e_nums:
                cleaned.extend([f'E{num}' for num in e_nums])
            
            # Extract ingredient name
            name = normalize_ingredient(ing)
            if name:
                cleaned.append(name)
    
    return cleaned

def search_additives(ingredients_text, fssai_db):
    """Enhanced additive search with better matching"""
    matches = []
    ingredients = parse_ingredients(ingredients_text)
    
    # Convert FSSAI DB entries to normalized format
    fssai_normalized = {}
    for entry in fssai_db:
        if isinstance(entry, dict):
            name = normalize_ingredient(entry.get('name', ''))
            code = entry.get('code', '').lower()
            if name:
                fssai_normalized[name] = entry
            if code:
                fssai_normalized[code] = entry
        elif isinstance(entry, str):
            name = normalize_ingredient(entry)
            if name:
                fssai_normalized[name] = {'name': entry}
    
    # Search for matches
    for ingredient in ingredients:
        # Direct match
        if ingredient in fssai_normalized:
            matches.append(fssai_normalized[ingredient])
            continue
        
        # Partial match
        for db_name, entry in fssai_normalized.items():
            if ingredient in db_name or db_name in ingredient:
                matches.append(entry)
                break
    
    return matches

def evaluate_product(nutrients, ingredients_text):
    """Evaluate product health score based on nutrients and ingredients"""
    score = 100
    pros, cons, missing = [], [], []
    
    # Parse ingredients first
    ingredients = parse_ingredients(ingredients_text)
    
    # Check each ingredient against FSSAI DB
    matches = search_additives(ingredients_text, FSSAI_DB)
    found_ingredients = set()
    
    if matches:
        for match in matches:
            name = match.get('name', 'Unknown additive')
            found_ingredients.add(normalize_ingredient(name))
            
            # Check limits if available
            limit = match.get('max_permitted')
            category = match.get('category', '')
            
            # Extract quantity if present
            qty_match = re.search(
                rf"{name}.*?(\d+(\.\d+)?)\s*(mg/kg|g/kg|%)", 
                ingredients_text, 
                re.I
            )
            
            if qty_match:
                qty_val = float(qty_match.group(1))
                unit = qty_match.group(3).lower()
                
                # Convert to mg/kg
                if unit == 'g/kg': 
                    qty_val *= 1000
                elif unit == '%': 
                    qty_val *= 10000
                
                if limit and qty_val > float(limit):
                    score -= 15
                    cons.append(f"{name} exceeds limit ({qty_val}>{limit} mg/kg)")
                else:
                    pros.append(f"{name} within safe limits")
            
            # Add category-based insights
            if category:
                if category.lower() in ['preservative', 'artificial color']:
                    cons.append(f"Contains {category.lower()}: {name}")
                elif category.lower() in ['vitamin', 'mineral', 'fiber']:
                    pros.append(f"Contains {category.lower()}: {name}")
    
    # Track missing ingredients
    missing = [ing for ing in ingredients if normalize_ingredient(ing) not in found_ingredients]
    
    # Nutrient scoring
    for key, rule in NUTRIENT_LIMITS.items():
        val = nutrients.get(key)
        if val is None:
            continue
        val = float(val)
        if "max" in rule and val > rule["max"]:
            score -= rule.get("penalty", 10)
            cons.append(f"High {key} ({val}{rule.get('unit','')})")
        if "min" in rule and val < rule["min"]:
            score += rule.get("bonus", 5)
            pros.append(f"Low {key} ({val}{rule.get('unit','')})")

    return max(0, min(100, score)), pros, cons, missing
