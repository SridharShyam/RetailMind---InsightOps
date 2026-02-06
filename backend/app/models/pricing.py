import numpy as np

def recommend_pricing(product_data, forecast_info, inventory_risk):
    """
    Recommend pricing action based on demand and inventory
    """
    price_history = product_data['price'].tail(7).values
    current_price = price_history[-1] if len(price_history) > 0 else product_data['price'].iloc[-1]
    price_volatility = np.std(price_history) / np.mean(price_history) if len(price_history) > 1 else 0
    
    demand_trend = forecast_info['demand_trend_pct']
    risk_level = inventory_risk['risk_level']
    days_of_stock = inventory_risk['days_of_stock']
    
    # Decision logic
    if risk_level == 'HIGH_RISK' and days_of_stock > 21:
        action = 'DECREASE'
        reason = "High overstock risk - consider promotional pricing to clear inventory"
        suggested_change_pct = -10
    elif risk_level == 'OPPORTUNITY' and demand_trend > 15:
        action = 'INCREASE'
        reason = "Strong demand with low inventory - opportunity for margin improvement"
        suggested_change_pct = 5
    elif demand_trend > 10 and days_of_stock < 10:
        action = 'INCREASE'
        reason = "Growing demand with limited stock - small price increase recommended"
        suggested_change_pct = 3
    elif demand_trend < -10 and days_of_stock > 14:
        action = 'DECREASE'
        reason = "Falling demand with excess stock - consider price reduction"
        suggested_change_pct = -7
    elif abs(demand_trend) < 5 and days_of_stock > 7 and days_of_stock < 14:
        action = 'HOLD'
        reason = "Stable market conditions - maintain current pricing"
        suggested_change_pct = 0
    elif price_volatility > 0.15:
        action = 'HOLD'
        reason = "Recent price volatility - maintain stability before changing"
        suggested_change_pct = 0
    else:
        action = 'HOLD'
        reason = "Market conditions are balanced - no price change needed"
        suggested_change_pct = 0
    
    # Calculate suggested price
    suggested_price = round(current_price * (1 + suggested_change_pct / 100), 2)
    
    return {
        'action': action,
        'reason': reason,
        'current_price': current_price,
        'suggested_price': suggested_price,
        'suggested_change_pct': suggested_change_pct,
        'price_volatility': round(price_volatility, 3)
    }