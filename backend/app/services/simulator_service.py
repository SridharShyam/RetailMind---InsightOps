"""
Simulator service - handles what-if scenario simulations
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models import simulator, forecasting
from app.services.data_service import get_data_service


class SimulatorService:
    """Service for what-if simulations"""
    
    def __init__(self):
        self.data_service = get_data_service()
        self.sim = simulator.WhatIfSimulator()
    
    async def simulate_price_change(self, product_name: str, new_price: float) -> dict:
        """Simulate impact of price change"""
        product_data = self.data_service.get_product_data(product_name)
        
        # Get current metrics
        current_price = product_data['price'].iloc[-1]
        current_demand = product_data['sales'].tail(7).mean()
        
        # Get forecast
        forecast_info = forecasting.forecast_demand(product_data)
        forecast_demand = sum(forecast_info['forecast_days']) / 7
        
        # Run simulation
        result = self.sim.simulate_price_impact(
            current_price=current_price,
            new_price=new_price,
            current_demand=current_demand,
            forecast_demand=forecast_demand,
            elasticity=1.2  # Can be made configurable
        )
        
        return {
            'product_name': product_name,
            'current_price': float(current_price),
            'new_price': float(new_price),
            **result
        }
    
    async def simulate_promotion(
        self, 
        product_name: str, 
        discount_pct: float, 
        duration_days: int
    ) -> dict:
        """Simulate impact of promotion"""
        product_data = self.data_service.get_product_data(product_name)
        
        current_price = product_data['price'].iloc[-1]
        current_daily_sales = product_data['sales'].tail(7).mean()
        
        result = self.sim.simulate_promotion(
            current_price=current_price,
            discount_pct=discount_pct,
            duration_days=duration_days,
            current_daily_sales=current_daily_sales
        )
        
        return {
            'product_name': product_name,
            'current_price': float(current_price),
            **result
        }
    
    async def simulate_inventory_change(
        self, 
        product_name: str, 
        new_stock_days: float
    ) -> dict:
        """Simulate impact of inventory level change"""
        product_data = self.data_service.get_product_data(product_name)
        
        current_demand = product_data['sales'].tail(7).mean()
        current_inventory = product_data['inventory'].iloc[-1]
        current_stock_days = current_inventory / (current_demand if current_demand > 0 else 1)
        price = product_data['price'].iloc[-1]
        
        result = self.sim.simulate_inventory_change(
            current_stock_days=current_stock_days,
            new_stock_days=new_stock_days,
            current_demand=current_demand,
            price=price
        )
        
        return {
            'product_name': product_name,
            'current_stock_days': round(current_stock_days, 1),
            **result
        }
    
    async def simulate_competitor_move(
        self, 
        product_name: str, 
        competitor_price_drop_pct: float
    ) -> dict:
        """Simulate impact of competitor price change"""
        product_data = self.data_service.get_product_data(product_name)
        
        current_price = product_data['price'].iloc[-1]
        current_demand = product_data['sales'].tail(7).mean()
        
        result = self.sim.simulate_competitor_move(
            current_price=current_price,
            competitor_price_drop_pct=competitor_price_drop_pct,
            current_demand=current_demand,
            elasticity=0.7  # Cross-price elasticity
        )
        
        return {
            'product_name': product_name,
            **result
        }
    
    async def simulate_marketing_campaign(
        self,
        product_name: str,
        ad_spend: float,
        expected_lift_pct: float
    ) -> dict:
        """Simulate ROI of marketing campaign"""
        product_data = self.data_service.get_product_data(product_name)
        
        current_price = product_data['price'].iloc[-1]
        current_daily_sales = product_data['sales'].tail(7).mean()
        
        result = self.sim.simulate_marketing_campaign(
            current_price=current_price,
            current_daily_sales=current_daily_sales,
            ad_spend=ad_spend,
            expected_lift_pct=expected_lift_pct
        )
        
        return {
            'product_name': product_name,
            **result
        }

    async def simulate_global_scenario(self, scenario: str, params: dict) -> dict:
        """
        Simulate a store-wide scenario.
        For performance, we might sample products or use aggregate stats.
        here we iterate over a sample of relevant products.
        """
        products = self.data_service.get_all_products()
        
        # Filter based on segment
        segment = params.get('segment', 'all')
        if segment == 'high_risk':
            # Mock filter: assume some are high risk. In real app, filter by risk score.
            products = products[:len(products)//3] 
        elif segment == 'opportunity':
            products = products[len(products)//3:2*len(products)//3]
        
        # Limit to 50 for performance in this demo
        target_products = products[:50]
        
        total_rev_delta = 0
        total_rev_base = 0
        total_demand_delta = 0
        total_demand_base = 0
        net_profit_impact = 0
        
        # Marketing specific
        marketing_daily_lift = 0
        
        for p in target_products:
            try:
                # Reuse existing single-product logic where possible
                if scenario == 'price_change':
                    pct = float(params.get('pct_change', 0))
                    p_data = self.data_service.get_product_data(p)
                    curr_price = float(p_data['price'].iloc[-1])
                    new_price = curr_price * (1 + pct / 100)
                    
                    res = await self.simulate_price_change(p, new_price)
                    
                    # Calculate deltas (approximate based on daily impact * 30 days)
                    base_rev = res['current_demand'] * res['current_price'] * 30
                    new_rev = res['projected_demand'] * res['new_price'] * 30
                    
                    total_rev_base += base_rev
                    total_rev_delta += (new_rev - base_rev)
                    
                    total_demand_base += res['current_demand'] * 30
                    total_demand_delta += (res['projected_demand'] - res['current_demand']) * 30
                    
                elif scenario == 'promotion':
                    discount_pct = float(params.get('discount_pct', 0))
                    duration = int(params.get('duration_days', 1))
                    
                    res = await self.simulate_promotion(p, discount_pct, duration)
                    
                    # Revenue impact is basically the delta
                    impact = res['revenue_impact'] # This is total for duration
                    total_rev_delta += impact
                    # Base revenue for this duration
                    p_data = self.data_service.get_product_data(p)
                    daily = p_data['sales'].tail(7).mean()
                    price = float(p_data['price'].iloc[-1])
                    total_rev_base += (daily * price * duration)
                    
                    # Demand lift
                    base_demand = daily * duration
                    lift = (res['lift_pct'] / 100) * base_demand
                    total_demand_base += base_demand
                    total_demand_delta += lift

                elif scenario == 'marketing':
                    ad_spend = float(params.get('ad_spend', 0)) # This is TOTAL, not per product
                    lift_pct = float(params.get('lift_pct', 0))
                    
                    # For global marketing, we apply lift to ALL products but spend is once
                    # We split spend per product just for calculation or treat differently?
                    # Let's just calculate revenue lift per product assuming global lift
                    res = await self.simulate_marketing_campaign(p, 0, lift_pct) # 0 spend per product, handle total later
                    
                    marketing_daily_lift += res['daily_revenue_increase']
                    
            except Exception:
                continue

        # Summarize
        summary = {}
        
        if scenario == 'marketing':
            ad_spend = float(params.get('ad_spend', 0))
            total_rev_delta = marketing_daily_lift * 30 # Project monthly
            net_profit_impact = total_rev_delta - ad_spend
            
            summary = {
                'total_revenue_change': total_rev_delta,
                'revenue_change_pct': round((total_rev_delta / (ad_spend if ad_spend > 0 else 1)) * 100, 1), # ROI-ish
                'demand_change_pct': float(params.get('lift_pct', 0)),
                'net_profit_impact': net_profit_impact,
                'action': 'POSITIVE' if net_profit_impact > 0 else 'NEGATIVE'
            }
        else:
            rev_pct = (total_rev_delta / total_rev_base * 100) if total_rev_base > 0 else 0
            demand_pct = (total_demand_delta / total_demand_base * 100) if total_demand_base > 0 else 0
            
            summary = {
                'total_revenue_change': round(total_rev_delta, 2),
                'revenue_change_pct': round(rev_pct, 1),
                'demand_change_pct': round(demand_pct, 1),
                'action': 'POSITIVE' if total_rev_delta > 0 else 'NEGATIVE'
            }

        return {
            "products_impacted": len(target_products),
            "summary": summary
        }


def get_simulator_service() -> SimulatorService:
    """Get SimulatorService instance"""
    return SimulatorService()