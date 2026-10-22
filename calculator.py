def calculate_total(dishes, portions=1, tax_rate=0.0, discount=0.0):
    """Calculate a deterministic total. tax_rate and discount are decimal fractions."""
    subtotal = sum(float(d["price"]) * int(portions) for d in dishes)
    discounted = subtotal * (1 - float(discount))
    return round(discounted * (1 + float(tax_rate)), 2)
