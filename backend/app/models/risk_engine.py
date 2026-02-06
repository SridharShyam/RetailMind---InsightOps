# models/risk_engine.py
import pandas as pd
import numpy as np
from datetime import datetime

class RiskOpportunityEngine:
    """AI-powered product risk and opportunity classifier"""
    
    def __init__(self):
        self.thresholds = {
            'high_risk_trend': -10,  # % weekly decline
            'high_opportunity_trend': 15,  # % weekly growth
            'overstock_threshold': 25,  # days of inventory
            'understock_threshold': 7,   # days of inventory
            'high_volatility': 0.4,      # coefficient of variation
            'low_volatility': 0.2
        }
    
    def calculate_metrics(self, product_data):
        """Calculate key metrics for risk assessment"""
        recent = product_data.tail(30)
        latest = product_data.iloc[-1]
        
        # Safe calculations
        sales_mean = recent['sales'].mean()
        sales_std = recent['sales'].std()
        
        metrics = {
            'product': product_data['product'].iloc[0],
            'current_avg': sales_mean,
            'trend_7d': self._calculate_trend(recent, 7),
            'trend_30d': self._calculate_trend(recent, 30),
            'volatility': sales_std / sales_mean if sales_mean > 0 else 0,
            'days_of_stock': (recent['inventory'].iloc[-1] / sales_mean) if sales_mean > 0 else 999,
            'stockout_risk': self._calculate_stockout_risk(recent),
            'price_stability': 1 - (recent['price'].std() / recent['price'].mean()) if recent['price'].mean() > 0 else 1,
            'expiry_date': latest.get('expiry_date', None),
            'date': latest['date']
        }
        return metrics
    
    def _calculate_trend(self, data, days):
        """Calculate % change over specified period"""
        if len(data) < days:
            return 0
        
        recent = data['sales'].tail(days)
        older = data['sales'].iloc[-days*2:-days] if len(data) >= days*2 else data['sales'].iloc[:days]
        
        if len(older) == 0 or older.mean() == 0:
            return 0
        
        return ((recent.mean() - older.mean()) / older.mean()) * 100
    
    def _calculate_stockout_risk(self, recent_data):
        """Calculate probability of stockout"""
        sales_std = recent_data['sales'].std()
        sales_mean = recent_data['sales'].mean()
        inventory_mean = recent_data['inventory'].mean()
        
        if sales_mean == 0:
            return 0
        
        # Simplified stockout probability
        z_score = (inventory_mean - sales_mean) / (sales_std + 1e-6)
        risk = max(0, min(1, 0.5 - 0.2 * z_score))  # Normal distribution approximation
        return risk

    def classify_product_v2(self, metrics, forecast_growth):
        """Enhanced classification with 3-color system and trend arrows"""
        
        # Calculate enhanced risk score (0-100)
        risk_score = 0
        opportunity_score = 0
        expiry_risk_level = 'NONE'
        expiry_message = ""
        
        # --- EXPIRY CHECK ---
        if metrics.get('expiry_date') is not None and not pd.isna(metrics.get('expiry_date')):
            current_date = metrics['date']
            expiry_date = metrics['expiry_date']
            
            # Ensure proper datetime types
            if not isinstance(current_date, datetime):
                current_date = pd.to_datetime(current_date)
            if not isinstance(expiry_date, datetime):
                expiry_date = pd.to_datetime(expiry_date)
            
            days_to_expiry = (expiry_date - current_date).days
            
            expiry_message = f"Days to expiry: {days_to_expiry}."
            
            if days_to_expiry <= 1:
                expiry_risk_level = 'CRITICAL'
                risk_score += 100 # Force High Risk
                expiry_message = f"CRITICAL: Product expires in {days_to_expiry} days! Clearance required."
            elif days_to_expiry <= 3:
                expiry_risk_level = 'HIGH'
                risk_score += 50
                expiry_message = f"WARNING: Product expires in {days_to_expiry} days. Promotion required."
            elif days_to_expiry <= 7:
                expiry_risk_level = 'MEDIUM'
                risk_score += 20
                expiry_message = f"NOTICE: Product expiring soon ({days_to_expiry} days)."

        # RISK FACTORS (adds to red score)
        if metrics['trend_7d'] < -10:
            risk_score += 30
        if metrics['days_of_stock'] > 25:
            risk_score += 25
        if metrics['stockout_risk'] > 0.3:
            risk_score += 20
        if metrics['volatility'] > 0.4:
            risk_score += 15
        
        # OPPORTUNITY FACTORS (adds to green score)
        if metrics['trend_7d'] > 15:
            opportunity_score += 30
        if metrics['days_of_stock'] < 7:
            opportunity_score += 25
        if forecast_growth > 10:
            opportunity_score += 20
        if metrics['volatility'] < 0.2 and metrics['trend_7d'] > 5:
            opportunity_score += 15
        
        # Determine category
        if risk_score >= 60 and opportunity_score < 30:
            category = "HIGH_RISK" # Changed to match existing API expected format
            color = "red"
            icon = "🔴"
            priority = 1
        elif opportunity_score >= 60 and risk_score < 30:
            category = "OPPORTUNITY" # "HIGH OPPORTUNITY" -> OPPORTUNITY to match simple API
            color = "green"
            icon = "🟢"
            priority = 1
        elif risk_score > opportunity_score:
            category = "MEDIUM_RISK" # "MODERATE RISK"
            color = "orange"
            icon = "🟡"
            priority = 2
        elif opportunity_score > risk_score:
            category = "STABLE" # "MODERATE OPPORTUNITY" -> STABLE/GOOD
            color = "lightgreen"
            icon = "🟡"
            priority = 2
        else:
            category = "STABLE" # "NEUTRAL"
            color = "gray"
            icon = "⚪"
            priority = 3
        
        # Determine trend arrow
        trend = metrics['trend_7d']
        if trend > 5:
            trend_arrow = "↗️"
            trend_text = f"+{trend:.1f}%"
        elif trend < -5:
            trend_arrow = "↘️"
            trend_text = f"{trend:.1f}%"
        else:
            trend_arrow = "➡️"
            trend_text = f"{trend:.1f}%"
        
        # Days until stockout calculation
        if metrics['days_of_stock'] <= 3:
            stockout_status = "IMMINENT"
            stockout_color = "red"
        elif metrics['days_of_stock'] <= 7:
            stockout_status = "SOON"
            stockout_color = "orange"
        else:
            stockout_status = "SAFE"
            stockout_color = "green"
        
        final_reason = self._get_recommended_action(category, metrics)
        if expiry_message:
            final_reason = f"{expiry_message} {final_reason}"

        return {
            'risk_level': category, # Mapped to risk_level for compatibility
            'color': color,
            'icon': icon,
            'priority': priority,
            'risk_score': risk_score,
            'opportunity_score': opportunity_score,
            'trend_arrow': trend_arrow,
            'trend_text': trend_text,
            'days_of_stock': round(metrics['days_of_stock'], 1),
            'stockout_status': stockout_status,
            'stockout_color': stockout_color,
            'reason': final_reason,
            'recommended_action': self._get_recommended_action(category, metrics),
            'avg_daily_sales': round(metrics['current_avg'], 1),
            'expiry_risk': expiry_risk_level
        }

    def _get_recommended_action(self, category, metrics):
        """Get specific action based on category"""
        actions = {
            "HIGH_RISK": [
                f"Discount by 15-20% to clear excess stock",
                "Bundle with trending products",
                "Reduce next order by 30%"
            ],
            "OPPORTUNITY": [
                f"Increase inventory to meet demand",
                "Feature in prime display location",
                "Consider slight price increase (3-5%)"
            ],
            "MEDIUM_RISK": [
                "Monitor closely for 7 days",
                "Prepare discount plan if trend continues"
            ],
            "STABLE": [
                "Maintain current levels",
                "Check competitor pricing"
            ]
        }
        # Fixed: return string not list
        return actions.get(category, ["Monitor as usual"])[0] 
