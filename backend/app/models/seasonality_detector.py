
import pandas as pd
import numpy as np

def detect_seasonality(product_data):
    """
    Detect weekly and monthly seasonality patterns.
    """
    df = product_data.copy()
    if 'date' not in df.columns:
        return {'seasonality': 'Unknown', 'best_day': 'Unknown'}

    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Weekly Analysis
    daily_avg = df.groupby('day_of_week')['sales'].mean()
    best_day = daily_avg.idxmax()
    worst_day = daily_avg.idxmin()
    
    # Calculate variability
    weekend_days = ['Saturday', 'Sunday']
    weekend_avg = daily_avg[daily_avg.index.isin(weekend_days)].mean()
    weekday_avg = daily_avg[~daily_avg.index.isin(weekend_days)].mean()
    
    is_weekend_heavy = weekend_avg > weekday_avg * 1.2
    
    if is_weekend_heavy:
        pattern = "Weekend Peak"
    elif weekend_avg < weekday_avg * 0.8:
        pattern = "Weekday Peak"
    else:
        pattern = "Consistent Daily"
        
    return {
        'pattern': pattern,
        'best_sales_day': best_day,
        'worst_sales_day': worst_day,
        'weekend_lift_pct': round(((weekend_avg - weekday_avg)/weekday_avg)*100, 1) if weekday_avg > 0 else 0
    }
