from datetime import datetime, timedelta
import pandas as pd

def assess_inventory_risk(product_data, forecast_info, current_date=None):
    """
    Assess inventory risk based on days of stock, demand trend, AND expiry dates.
    """
    if current_date is None:
        current_date = datetime.now() if isinstance(product_data.iloc[-1]['date'], datetime) else pd.to_datetime(product_data.iloc[-1]['date'])

    # Get latest inventory
    latest = product_data.iloc[-1]
    current_inventory = latest['inventory']
    sales_velocity = latest.get('sales_velocity', 1)
    expiry_date = latest.get('expiry_date', None)
    
    # Calculate days of stock
    avg_daily_sales = forecast_info['last_7d_avg']
    if avg_daily_sales > 0:
        days_of_stock = current_inventory / avg_daily_sales
    else:
        days_of_stock = 999
    
    # Get demand trend
    demand_trend = forecast_info['demand_trend_pct']
    
    # --- Expiry Risk Logic ---
    expiry_risk_level = 'NONE'
    expiry_message = ""
    
    if expiry_date is not pd.NaT and expiry_date is not None:
        if not isinstance(expiry_date, datetime):
            expiry_date = pd.to_datetime(expiry_date)
            
        days_to_expiry = (expiry_date - current_date).days
        
        if days_to_expiry <= 1:
            expiry_risk_level = 'CRITICAL'
            expiry_message = f"CRITICAL: Product expires in {days_to_expiry} days!"
        elif days_to_expiry <= 3:
            expiry_risk_level = 'HIGH'
            expiry_message = f"WARNING: Product expires in {days_to_expiry} days."
        elif days_to_expiry <= 7:
            expiry_risk_level = 'MEDIUM'
            expiry_message = f"NOTICE: Product expires in {days_to_expiry} days."
    
    # --- Inventory Risk Classification ---
    risk_level = 'STABLE'
    reason = f"Balanced inventory ({days_of_stock:.1f} days) with stable demand"

    # Prioritize Expiry Risk if Critical
    if expiry_risk_level == 'CRITICAL':
        risk_level = 'HIGH_RISK'
        reason = expiry_message + " Immediate clearance recommended."
    elif days_of_stock > 21 and demand_trend < -5:
        risk_level = 'HIGH_RISK'
        reason = f"Overstocked with {days_of_stock:.1f} days of inventory and falling demand"
    elif days_of_stock > 14 and demand_trend < 0:
        risk_level = 'MEDIUM_RISK'
        reason = f"High inventory ({days_of_stock:.1f} days) with stable or falling demand"
    elif days_of_stock < 3 and demand_trend > 10:
        risk_level = 'OPPORTUNITY'
        reason = f"Low stock ({days_of_stock:.1f} days) with strong rising demand"
    elif days_of_stock < 7 and demand_trend > 5:
        risk_level = 'OPPORTUNITY'
        reason = f"Low inventory ({days_of_stock:.1f} days) with growing demand"
    
    # Append expiry warning if not already in reason
    if expiry_risk_level in ['HIGH', 'MEDIUM'] and expiry_message not in reason:
        reason += f" {expiry_message}"

    return {
        'risk_level': risk_level,
        'days_of_stock': round(days_of_stock, 1),
        'reason': reason,
        'current_inventory': int(current_inventory),
        'avg_daily_sales': round(avg_daily_sales, 1),
        'expiry_date': expiry_date.strftime('%Y-%m-%d') if expiry_date and expiry_date is not pd.NaT else 'N/A',
        'expiry_risk': expiry_risk_level
    }