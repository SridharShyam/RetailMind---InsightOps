import pandas as pd
import numpy as np

def forecast_demand(product_data):
    """
    Simple demand forecasting using rolling averages and trend detection
    """
    # Sort by date
    product_data = product_data.sort_values('date')
    
    # Calculate 7-day moving average
    product_data['7d_avg'] = product_data['sales'].rolling(window=7, min_periods=1).mean()
    
    # Calculate trend (simple linear regression on last 14 days)
    recent_data = product_data.tail(14)
    if len(recent_data) >= 7:
        x = np.arange(len(recent_data))
        y = recent_data['sales'].values
        slope = np.polyfit(x, y, 1)[0]
        
        # Normalize trend to percentage
        avg_sales = recent_data['sales'].mean()
        trend_pct = (slope / max(avg_sales, 1)) * 100 if avg_sales > 0 else 0
    else:
        trend_pct = 0
    
    # Calculate volatility (coefficient of variation)
    if product_data['sales'].std() > 0 and product_data['sales'].mean() > 0:
        volatility = product_data['sales'].std() / product_data['sales'].mean()
    else:
        volatility = 0
    
    # Confidence score based on volatility and data points
    confidence = max(0.1, 1 - min(volatility, 0.5))
    confidence_tier = 'HIGH' if confidence > 0.7 else 'MEDIUM' if confidence > 0.4 else 'LOW'
    
    # Generate next 7 days forecast
    last_avg = product_data['7d_avg'].iloc[-1] if not product_data.empty else product_data['sales'].mean()
    forecast_days = []
    
    for i in range(1, 8):
        # Apply trend to forecast
        forecast_value = last_avg * (1 + (trend_pct / 100) * i / 7)
        forecast_days.append(max(1, int(forecast_value)))
    
    return {
        'forecast_days': forecast_days,
        'demand_trend_pct': round(trend_pct, 1),
        'confidence_score': round(confidence, 2),
        'confidence_tier': confidence_tier,
        'last_7d_avg': round(last_avg, 1) if last_avg else 0
    }