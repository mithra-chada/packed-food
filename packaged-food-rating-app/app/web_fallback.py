import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")

def google_search(query, num_results=2):
    """Search Google Programmable Search Engine"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": API_KEY, "cx": CX, "num": num_results}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    return []
