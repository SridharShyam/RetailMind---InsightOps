
import pandas as pd
import numpy as np

class WhatIfSimulator:
    """AI-driven business decision simulator"""
    
    def __init__(self):
        # Default elasticities if not overridden
        self.default_elasticity = 1.0
        
    def simulate_price_impact(self, current_price, new_price, current_demand, forecast_demand, elasticity=None):
        """Simulate impact of price change"""
        if elasticity is None:
            elasticity = self.default_elasticity
            
        price_change_pct = (new_price - current_price) / current_price * 100
        
        # Calculate demand impact
        demand_change_pct = -elasticity * price_change_pct
        new_demand = current_demand * (1 + demand_change_pct / 100)
        forecast_new = forecast_demand * (1 + demand_change_pct / 100)
        
        # Revenue impact
        current_revenue = current_demand * current_price
        new_revenue = new_demand * new_price
        revenue_change_pct = (new_revenue - current_revenue) / current_revenue * 100 if current_revenue > 0 else 0
        
        return {
            'scenario': 'price_change',
            'price_change_pct': round(price_change_pct, 1),
            'demand_change_pct': round(demand_change_pct, 1),
            'new_demand': int(max(0, new_demand)),
            'forecast_new': int(max(0, forecast_new)),
            'revenue_change_pct': round(revenue_change_pct, 1),
            'recommendation': 'INCREASE' if revenue_change_pct > 0 else 'DECREASE' if revenue_change_pct < -5 else 'HOLD'
        }
    
    def simulate_promotion(self, current_price, discount_pct, duration_days, current_daily_sales):
        """Simulate impact of promotion"""
        # Simple model: 1% discount = 2% sales lift (elasticity of 2)
        lift_pct = discount_pct * 2
        
        predicted_daily_sales = current_daily_sales * (1 + lift_pct / 100)
        total_sales_units = predicted_daily_sales * duration_days
        
        discounted_price = current_price * (1 - discount_pct / 100)
        total_revenue = total_sales_units * discounted_price
        
        baseline_revenue = current_daily_sales * duration_days * current_price
        revenue_change = total_revenue - baseline_revenue
        
        return {
            'scenario': 'promotion',
            'discount_pct': discount_pct,
            'lift_pct': discount_pct * 2,
            'predicted_daily_sales': int(predicted_daily_sales),
            'revenue_impact': round(revenue_change, 2),
            'is_profitable': revenue_change > 0,
            'recommendation': 'RUN' if revenue_change > 0 else 'MODIFY'
        }

    def simulate_inventory_change(self, current_stock_days, new_stock_days, current_demand, price):
        """Simulate impact of inventory level change"""
        stock_change_pct = ((new_stock_days - current_stock_days) / current_stock_days * 100)
        
        # Stockout risk reduction (diminishing returns)
        stockout_risk_reduction = min(40, abs(stock_change_pct) * 0.8) if stock_change_pct > 0 else 0
        
        # Holding cost impact (estimated 0.1% per day per unit value)
        holding_cost_impact = (new_stock_days - current_stock_days) * current_demand * price * 0.001
        
        # Lost sales risk (if decreasing inventory below 7 days)
        lost_sales_risk = 0
        if new_stock_days < 7 and current_stock_days >= 7:
            lost_sales_risk = (7 - new_stock_days) * 5 # 5% per day under 7
            
        return {
            'scenario': 'inventory_change',
            'stock_change_pct': round(stock_change_pct, 1),
            'stockout_risk_reduction': round(stockout_risk_reduction, 1),
            'holding_cost_change': round(holding_cost_impact, 2),
            'lost_sales_risk_pct': round(lost_sales_risk, 1),
            'recommendation': 'INCREASE' if stock_change_pct > 0 and stockout_risk_reduction > 20 else 
                            'DECREASE' if stock_change_pct < 0 and holding_cost_impact > 10 else 'HOLD'
        }

    def simulate_competitor_move(self, current_price, competitor_price_drop_pct, current_demand, elasticity=None):
        """Simulate impact if a competitor drops their price"""
        if elasticity is None:
            elasticity = 0.5 # Cross-elasticity is usually lower than own-price elasticity
            
        # If competitor drops price by 10%, our demand drops by (10 * 0.5)%
        demand_drop_pct = competitor_price_drop_pct * elasticity
        
        new_demand = current_demand * (1 - demand_drop_pct / 100)
        
        # We maintain price, so revenue drops linearly with demand
        revenue_change_pct = -demand_drop_pct
        
        return {
            'scenario': 'competitor_move',
            'competitor_drop_pct': competitor_price_drop_pct,
            'demand_impact_pct': -round(demand_drop_pct, 1),
            'revenue_impact_pct': -round(demand_drop_pct, 1),
            'recommendation': 'MATCH_PRICE' if demand_drop_pct > 10 else 'MONITOR'
        }

    def simulate_marketing_campaign(self, current_price, current_daily_sales, ad_spend, expected_lift_pct):
        """Simulate ROI of a marketing campaign"""
        # New Sales
        new_daily_sales = current_daily_sales * (1 + expected_lift_pct / 100)
        daily_revenue_lift = (new_daily_sales - current_daily_sales) * current_price
        
        # Calculate break-even days
        if daily_revenue_lift > 0:
            break_even_days = ad_spend / daily_revenue_lift
        else:
            break_even_days = 999
            
        return {
            'scenario': 'marketing',
            'ad_spend': ad_spend,
            'traffic_lift_pct': expected_lift_pct,
            'daily_revenue_increase': round(daily_revenue_lift, 2),
            'break_even_days': round(break_even_days, 1),
            'recommendation': 'RUN_CAMPAIGN' if break_even_days < 7 else 'REDUCE_COST'
        }

# Module level wrappers for compatibility
_sim_instance = WhatIfSimulator()

def simulate_price_impact(*args, **kwargs):
    return _sim_instance.simulate_price_impact(*args, **kwargs)

def simulate_promotion(*args, **kwargs):
    return _sim_instance.simulate_promotion(*args, **kwargs)

def simulate_inventory_change(*args, **kwargs):
    return _sim_instance.simulate_inventory_change(*args, **kwargs)

def simulate_competitor_move(*args, **kwargs):
    return _sim_instance.simulate_competitor_move(*args, **kwargs)

def simulate_marketing_campaign(*args, **kwargs):
    return _sim_instance.simulate_marketing_campaign(*args, **kwargs)
