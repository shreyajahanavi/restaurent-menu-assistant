def filter_menu(menu, vegetarian_only=False, max_price=None):
    """Structured filters should enforce hard constraints after vector retrieval."""
    output = []
    for dish in menu:
        if vegetarian_only and not dish.get("vegetarian", False):
            continue
        if max_price is not None and float(dish["price"]) > float(max_price):
            continue
        output.append(dish)
    return output
