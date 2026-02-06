
def analyze_synergy(current_product, all_sales_data):
    """
    Identify products that are often bought together (Market Basket Analysis equivalent).
    """
    # Simply using a mock logic here:
    # Products starting with same letter or category might be related.
    # In reality, this would use Apriori algorithm on transaction logs.
    
    # Mock synergies
    synergies = {
        'Coffee Beans': ['Fresh Milk', 'Artisan Bread'],
        'Fresh Milk': ['Cereal', 'Coffee Beans'],
        'Artisan Bread': ['Organic Honey', 'Free-range Eggs'],
        'Pasta': ['Tomato Sauce', 'Olive Oil']
    }
    
    related = synergies.get(current_product, [])
    
    if not related:
        # Fallback random recommendations
        import random
        random.seed(len(current_product)) # standard seed
        # Just pick 2 random other ones? No, let's leave empty if no strict definition
        related = []

    return {
        'related_products': related,
        'cross_sell_opportunity': 'HIGH' if related else 'LOW'
    }
