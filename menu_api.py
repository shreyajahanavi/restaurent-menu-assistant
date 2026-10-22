"""Optional adapter for a real menu API.

Set MENU_API_URL to the restaurant/provider endpoint and MENU_API_KEY if required.
Because menu APIs differ, map the provider response to the normalized schema below.
Never mark allergy data verified unless the source explicitly confirms ingredients/allergens.
"""
import os
import requests

def fetch_menu():
    url = os.getenv("MENU_API_URL")
    if not url:
        return None
    headers = {}
    if os.getenv("MENU_API_KEY"):
        headers["Authorization"] = f"Bearer {os.environ['MENU_API_KEY']}"
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    payload = response.json()
    # Adjust this mapping to the actual provider's API response.
    items = payload.get("items", payload if isinstance(payload, list) else [])
    normalized = []
    for i, item in enumerate(items):
        normalized.append({
            "id": str(item.get("id", f"api-{i}")),
            "name": item["name"],
            "price": float(item["price"]),
            "vegetarian": bool(item.get("vegetarian", False)),
            "category": item.get("category", "Other"),
            "description": item.get("description", ""),
            "ingredients": item.get("ingredients", []),
            "allergens": item.get("allergens", []),
            "allergen_verified": bool(item.get("allergen_verified", False)),
            "cross_contact_unknown": item.get("cross_contact_unknown", True),
        })
    return normalized
