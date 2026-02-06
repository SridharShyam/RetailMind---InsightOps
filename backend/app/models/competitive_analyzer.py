
import random

def analyze_competition(product_name, current_price):
    """
    Simulate competitor pricing analysis.
    In a real app, this would scrape or query an API.
    Here we simulate market conditions based on the product name.
    """
    # Mock market data adjustment factors
    # If standard deviation is high, market is volatile
    
    market_variance = 0.15  # +/- 15% price variance in market
    
    # Deterministic "random" for stability based on name hash
    random.seed(hash(product_name))
    avg_market_price = current_price * random.uniform(0.85, 1.15)
    
    price_diff_pct = ((current_price - avg_market_price) / avg_market_price) * 100
    
    position = "Market Aligned"
    if price_diff_pct > 10:
        position = "Premium / Overpriced"
    elif price_diff_pct < -10:
        position = "Budget / Underpriced"
        
    return {
        'avg_market_price': round(avg_market_price, 2),
        'price_difference_pct': round(price_diff_pct, 1),
        'market_position': position,
        'competitor_count': random.randint(2, 6)
    }
