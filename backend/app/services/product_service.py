"""
Product service - orchestrates all product analysis
"""
import sys
import os

# Add models directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models import forecasting, inventory_risk, pricing, recommendations
from models import competitive_analyzer, seasonality_detector
from app.services.data_service import get_data_service


class ProductService:
    """Service for complete product analysis"""
    
    def __init__(self):
        self.data_service = get_data_service()
    
    async def analyze_product(self, product_name: str) -> dict:
        """
        Complete product analysis pipeline
        Returns all insights in a single call
        """
        # Get product data
        product_data = self.data_service.get_product_data(product_name)
        
        if product_data.empty:
            raise ValueError(f"No data found for product: {product_name}")
        
        # Get current metrics
        current_price = float(product_data['price'].iloc[-1])
        current_inventory = int(product_data['inventory'].iloc[-1])
        current_sales = float(product_data['sales'].tail(7).mean())
        last_date = str(product_data['date'].iloc[-1].date())
        
        # 1. Demand Forecasting
        forecast_info = forecasting.forecast_demand(product_data)
        
        # 2. Inventory Risk Assessment
        inventory_risk_info = inventory_risk.assess_inventory_risk(
            product_data, 
            forecast_info
        )
        
        # 3. Pricing Recommendation
        pricing_info = pricing.recommend_pricing(
            product_data, 
            forecast_info, 
            inventory_risk_info
        )
        
        # 4. Competition Analysis
        competition_info = competitive_analyzer.analyze_competition(
            product_name, 
            current_price
        )
        
        # 5. Seasonality Detection
        seasonality_info = seasonality_detector.detect_seasonality(product_data)
        
        # 6. Overall Recommendation
        recommendation = recommendations.generate_recommendation(
            forecast_info,
            inventory_risk_info,
            pricing_info
        )
        
        # 7. Synergy (Related Products)
        synergy_info = {
            'related_products': []  # Placeholder for now
        }
        
        return {
            'product_name': product_name,
            'current_price': current_price,
            'metrics': {
                'current_price': current_price,
                'current_inventory': current_inventory,
                'current_sales': round(current_sales, 1),
                'last_date': last_date
            },
            'forecast': {
                'demand_trend_pct': forecast_info.get('demand_trend_pct', 0),
                'forecast_next_7_days': forecast_info.get('forecast_days', []),
                'confidence_tier': forecast_info.get('confidence_tier', 'MEDIUM'),
                'confidence_score': forecast_info.get('confidence_score', 0.5)
            },
            'inventory_risk': {
                'risk_level': inventory_risk_info.get('risk_level', 'STABLE'),
                'reason': inventory_risk_info.get('reason', 'No significant risk detected'),
                'days_of_stock': inventory_risk_info.get('days_of_stock', 0)
            },
            'pricing': {
                'action': pricing_info.get('action', 'HOLD'),
                'reason': pricing_info.get('reason', 'Price is optimal'),
                'current_price': pricing_info.get('current_price', current_price),
                'suggested_price': pricing_info.get('suggested_price', current_price),
                'suggested_change_pct': pricing_info.get('suggested_change_pct', 0)
            },
            'seasonality': {
                'pattern': seasonality_info.get('pattern', 'No clear pattern'),
                'best_sales_day': seasonality_info.get('best_sales_day', 'N/A'),
                'weekend_lift_pct': seasonality_info.get('weekend_lift_pct', 0)
            },
            'competition': {
                'market_position': competition_info.get('market_position', 'COMPETITIVE'),
                'avg_market_price': competition_info.get('avg_market_price', current_price),
                'price_difference_pct': competition_info.get('price_difference_pct', 0)
            },
            'synergy': synergy_info,
            'recommendation': {
                'confidence': recommendation.get('confidence', 'MEDIUM'),
                'inventory_action': recommendation.get('inventory_action', 'MONITOR'),
                'summary': recommendation.get('summary', 'Continue current strategy'),
                'action_reason': recommendation.get('action_reason', 'Product performance is stable'),
                'pricing_guidance': recommendation.get('pricing_guidance', 'Maintain current pricing')
            }
        }
    
    async def get_product_forecast(self, product_name: str, days: int = 7) -> dict:
        """Get demand forecast only"""
        product_data = self.data_service.get_product_data(product_name)
        forecast_info = forecasting.forecast_demand(product_data)
        
        return {
            'product_name': product_name,
            **forecast_info
        }
    
    async def get_pricing_recommendation(self, product_name: str) -> dict:
        """Get pricing recommendation only"""
        product_data = self.data_service.get_product_data(product_name)
        
        # Need forecast and inventory for pricing
        forecast_info = forecasting.forecast_demand(product_data)
        inventory_risk_info = inventory_risk.assess_inventory_risk(
            product_data, 
            forecast_info
        )
        
        pricing_info = pricing.recommend_pricing(
            product_data, 
            forecast_info, 
            inventory_risk_info
        )
        
        return {
            'product_name': product_name,
            **pricing_info
        }
    
    async def get_inventory_risk(self, product_name: str) -> dict:
        """Get inventory risk assessment only"""
        product_data = self.data_service.get_product_data(product_name)
        forecast_info = forecasting.forecast_demand(product_data)
        
        inventory_risk_info = inventory_risk.assess_inventory_risk(
            product_data, 
            forecast_info
        )
        
        return {
            'product_name': product_name,
            **inventory_risk_info
        }
    

    async def list_products(self) -> dict:
        """Get all available products with summary stats"""
        product_names = self.data_service.get_all_products()
        products_summary = []
        
        for name in product_names:
            try:
                # Reuse data fetching
                product_data = self.data_service.get_product_data(name)
                if product_data.empty: continue
                
                # Basic Stats
                current_price = float(product_data['price'].iloc[-1])
                
                # Forecast (Required for Risk/Days of Stock)
                forecast_info = forecasting.forecast_demand(product_data)
                
                # Inventory Risk
                inv_risk = inventory_risk.assess_inventory_risk(product_data, forecast_info)
                
                # Construct Summary
                products_summary.append({
                    'product_name': name,
                    'risk_level': inv_risk.get('risk_level', 'STABLE'),
                    'days_of_stock': inv_risk.get('days_of_stock', 0.0),
                    'demand_trend_pct': forecast_info.get('demand_trend_pct', 0.0),
                    'current_price': current_price,
                    'expiry_risk': inv_risk.get('expiry_risk', 'LOW'),
                    # Extended metrics
                    'pricing_action': pricing.recommend_pricing(product_data, forecast_info, inv_risk).get('action', 'HOLD'),
                    'confidence_tier': forecast_info.get('confidence_tier', 'MEDIUM'),
                    'market_position': competitive_analyzer.analyze_competition(name, current_price).get('market_position', 'N/A'),
                    'risk_reason': inv_risk.get('reason', '')
                })
            except Exception as e:
                print(f"Error summarizing {name}: {e}")
                continue

        return {
            'products': products_summary,
            'total_count': len(products_summary)
        }
        
    async def process_transaction(self, request) -> dict:
        """Process a sale or restock transaction"""
        result = self.data_service.process_transaction(
            request.product_name,
            request.quantity,
            request.transaction_type
        )
        
        if 'error' in result:
             raise ValueError(result['error'])
             
        return result

    async def get_insights_summary(self) -> dict:
        """
        Generate business insights based on all products.
        Replaces legacy frontend logic.
        """
        products = self.data_service.get_all_products()
        
        high_risk_prods = []
        opportunity_prods = []
        
        for name in products:
            try:
                p_data = self.data_service.get_product_data(name)
                if p_data.empty: continue
                
                forecast_info = forecasting.forecast_demand(p_data)
                risk = inventory_risk.assess_inventory_risk(p_data, forecast_info)
                
                if risk.get('risk_level') == 'HIGH_RISK':
                    high_risk_prods.append(name)
                elif risk.get('risk_level') == 'OPPORTUNITY':
                    opportunity_prods.append(name)
                    
            except Exception:
                continue

        # Generate text
        insights_text = []
        if high_risk_prods:
            insights_text.append(f"Found {len(high_risk_prods)} products at high risk of stockout or expiry.")
        if opportunity_prods:
            insights_text.append(f"Identified {len(opportunity_prods)} products with pricing opportunities.")
        insights_text.append(f"Analyzed {len(products)} total SKUs for patterns.")

        return {
            "counts": {
                "total_products": len(products),
                "high_risk": len(high_risk_prods),
                "opportunities": len(opportunity_prods)
            },
            "insights": insights_text,
            "high_risk_products": high_risk_prods[:10],
            "opportunity_products": opportunity_prods[:10],
            "daily_actions": [
                "Review high risk items for immediate restock",
                "Check expiry dates for perishable warnings", 
                "Monitor competitor price moves for top sellers"
            ],
            "weekly_strategy": [
                "Run simulation for potential store-wide sale",
                "Adjust prices for 'Opportunity' products",
                "Clear out forecast anomalies"
            ]
        }


def get_product_service() -> ProductService:
    """Get ProductService instance"""
    return ProductService()