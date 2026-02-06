"""
AI Copilot service - handles natural language queries
"""
import re
from typing import Dict, Any, List
from app.services.product_service import get_product_service
from app.services.simulator_service import get_simulator_service
from app.services.data_service import get_data_service


class CopilotService:
    """AI Copilot for natural language product intelligence"""
    
    def __init__(self):
        self.product_service = get_product_service()
        self.simulator_service = get_simulator_service()
        self.data_service = get_data_service()
        
        # Intent patterns
        self.intent_patterns = {
            'forecast': [
                r'forecast|predict|demand|how many|sales next',
                r'will.*sell|expected sales|future demand'
            ],
            'pricing': [
                r'price|pricing|cost|how much should',
                r'increase.*price|decrease.*price|optimal price'
            ],
            'inventory': [
                r'stock|inventory|stockout|overstock',
                r'days of stock|running out|too much stock'
            ],
            'simulation': [
                r'what if|simulate|scenario|if i',
                r'happens if|reduce.*by|increase.*by'
            ],
            'comparison': [
                r'compare|vs|versus|better|worse',
                r'which product|best|worst'
            ],
            'risk': [
                r'risk|risky|opportunity|danger|problem',
                r'expiring|expire|clearance'
            ]
        }
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process natural language query and return intelligent response
        """
        query_lower = query.lower()
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        # Extract product name
        products = self.data_service.get_all_products()
        product_name = self._extract_product_name(query_lower, products)
        
        # Process based on intent
        if intent == 'forecast':
            return await self._handle_forecast_query(query, product_name)
        
        elif intent == 'pricing':
            return await self._handle_pricing_query(query, product_name)
        
        elif intent == 'inventory':
            return await self._handle_inventory_query(query, product_name)
        
        elif intent == 'simulation':
            return await self._handle_simulation_query(query, product_name)
        
        elif intent == 'risk':
            return await self._handle_risk_query(query, product_name)
        
        elif intent == 'comparison':
            return await self._handle_comparison_query(query, products)
        
        else:
            return await self._handle_general_query(query, product_name)
    
    def _detect_intent(self, query: str) -> str:
        """Detect user intent from query"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query):
                    return intent
        return 'general'
    
    def _extract_product_name(self, query: str, products: List[str]) -> str:
        """Extract product name from query"""
        # Check for exact or partial matches
        for product in products:
            if product.lower() in query:
                return product
        
        # Try fuzzy matching with product keywords
        for product in products:
            keywords = product.lower().split()
            if any(keyword in query for keyword in keywords if len(keyword) > 3):
                return product
        
        return None
    
    async def _handle_forecast_query(self, query: str, product_name: str) -> Dict[str, Any]:
        """Handle forecasting queries"""
        if not product_name:
            return {
                'query': query,
                'response': "I need to know which product you're asking about. Please specify a product name.",
                'intent': 'forecast',
                'suggestions': [
                    "Try: 'What's the forecast for Coffee Beans?'",
                    "Or: 'How many Eggs will I sell next week?'"
                ]
            }
        
        result = await self.product_service.get_product_forecast(product_name)
        
        forecast_avg = sum(result['forecast_days']) / len(result['forecast_days'])
        trend = "increasing" if result['demand_trend_pct'] > 0 else "decreasing"
        
        response = (
            f"📈 **Forecast for {product_name}:**\n\n"
            f"• Expected daily sales: ~{int(forecast_avg)} units\n"
            f"• 7-day total: {sum(result['forecast_days'])} units\n"
            f"• Trend: {trend} by {abs(result['demand_trend_pct'])}%\n"
            f"• Confidence: {result['confidence_tier']}"
        )
        
        return {
            'query': query,
            'response': response,
            'intent': 'forecast',
            'data': result,
            'suggestions': [
                f"What if I reduce the price of {product_name}?",
                f"Should I stock more {product_name}?"
            ]
        }
    
    async def _handle_pricing_query(self, query: str, product_name: str) -> Dict[str, Any]:
        """Handle pricing queries"""
        if not product_name:
            products_list = ', '.join(self.data_service.get_all_products()[:3])
            return {
                'query': query,
                'response': f"Which product? Try one of: {products_list}",
                'intent': 'pricing',
                'suggestions': ["Show me all products"]
            }
        
        result = await self.product_service.get_pricing_recommendation(product_name)
        
        action_emoji = {
            'INCREASE': '📈',
            'DECREASE': '📉',
            'HOLD': '➡️'
        }
        
        response = (
            f"{action_emoji.get(result['action'], '💰')} **Pricing for {product_name}:**\n\n"
            f"• Action: {result['action']}\n"
            f"• Current: ₹{result['current_price']:.0f}\n"
            f"• Suggested: ₹{result['suggested_price']:.0f} "
            f"({result['suggested_change_pct']:+.1f}%)\n\n"
            f"**Why?** {result['reason']}"
        )
        
        return {
            'query': query,
            'response': response,
            'intent': 'pricing',
            'data': result,
            'suggestions': [
                f"Simulate a 10% price increase for {product_name}",
                f"What's the inventory status of {product_name}?"
            ]
        }
    
    async def _handle_inventory_query(self, query: str, product_name: str) -> Dict[str, Any]:
        """Handle inventory queries"""
        if not product_name:
            return {
                'query': query,
                'response': "Which product's inventory are you asking about?",
                'intent': 'inventory',
                'suggestions': ["Show me high-risk inventory items"]
            }
        
        result = await self.product_service.get_inventory_risk(product_name)
        
        risk_emoji = {
            'HIGH_RISK': '🔴',
            'MEDIUM_RISK': '🟡',
            'OPPORTUNITY': '🟢',
            'STABLE': '⚪'
        }
        
        response = (
            f"{risk_emoji.get(result['risk_level'], '📦')} **Inventory: {product_name}**\n\n"
            f"• Status: {result['risk_level'].replace('_', ' ')}\n"
            f"• Days of stock: {result['days_of_stock']:.1f} days\n"
            f"• Current inventory: {result['current_inventory']} units\n"
            f"• Avg daily sales: {result['avg_daily_sales']:.1f} units\n"
            f"• Expiry: {result['expiry_date']}\n\n"
            f"**Action needed:** {result['reason']}"
        )
        
        return {
            'query': query,
            'response': response,
            'intent': 'inventory',
            'data': result,
            'suggestions': [
                f"Should I order more {product_name}?",
                f"Simulate inventory increase for {product_name}"
            ]
        }
    
    async def _handle_simulation_query(self, query: str, product_name: str) -> Dict[str, Any]:
        """Handle what-if simulation queries"""
        if not product_name:
            return {
                'query': query,
                'response': "Which product do you want to simulate scenarios for?",
                'intent': 'simulation'
            }
        
        # Extract numbers from query
        numbers = re.findall(r'\d+\.?\d*', query)
        
        # Detect simulation type
        if 'price' in query.lower() and numbers:
            # Price simulation
            if 'reduce' in query.lower() or 'decrease' in query.lower():
                change_pct = -float(numbers[0])
            else:
                change_pct = float(numbers[0])
            
            # Get current price and calculate new price
            product_data = self.data_service.get_product_data(product_name)
            current_price = product_data['price'].iloc[-1]
            new_price = current_price * (1 + change_pct / 100)
            
            result = await self.simulator_service.simulate_price_change(product_name, new_price)
            
            response = (
                f"💡 **Simulation: Price change for {product_name}**\n\n"
                f"• Price: ₹{result['current_price']:.0f} → ₹{result['new_price']:.0f} "
                f"({result['price_change_pct']:+.1f}%)\n"
                f"• Demand impact: {result['demand_change_pct']:+.1f}%\n"
                f"• Revenue impact: {result['revenue_change_pct']:+.1f}%\n"
                f"• New demand: {result['new_demand']} units/day\n\n"
                f"**Recommendation:** {result['recommendation']}"
            )
            
            return {
                'query': query,
                'response': response,
                'intent': 'simulation',
                'data': result
            }
        
        return {
            'query': query,
            'response': f"I can simulate price changes, promotions, and inventory adjustments for {product_name}. Try asking:\n• 'What if I reduce price by 10%?'\n• 'Simulate a 15% discount for 7 days'",
            'intent': 'simulation'
        }
    
    async def _handle_risk_query(self, query: str, product_name: str) -> Dict[str, Any]:
        """Handle risk assessment queries"""
        if product_name:
            analysis = await self.product_service.analyze_product(product_name)
            risk = analysis['inventory_risk']
            
            response = (
                f"⚠️ **Risk Assessment: {product_name}**\n\n"
                f"• Risk Level: {risk['risk_level']}\n"
                f"• {risk['reason']}\n"
                f"• Days of stock: {risk['days_of_stock']}\n"
                f"• Expiry risk: {risk['expiry_risk']}"
            )
            
            return {
                'query': query,
                'response': response,
                'intent': 'risk',
                'data': risk
            }
        
        return {
            'query': query,
            'response': "Which product would you like me to assess for risk?",
            'intent': 'risk'
        }
    
    async def _handle_comparison_query(self, query: str, products: List[str]) -> Dict[str, Any]:
        """Handle product comparison queries"""
        return {
            'query': query,
            'response': "Product comparison feature coming soon! For now, you can analyze individual products.",
            'intent': 'comparison',
            'suggestions': [f"Analyze {products[0]}", "Show me all products"]
        }
    
    async def _handle_general_query(self, query: str, product_name: str) -> Dict[str, Any]:
        """Handle general queries"""
        if product_name:
            return {
                'query': query,
                'response': f"I can help with {product_name}! Ask me about:\n• Demand forecast\n• Pricing recommendations\n• Inventory status\n• What-if simulations",
                'intent': 'general',
                'suggestions': [
                    f"Analyze {product_name}",
                    f"What's the forecast for {product_name}?",
                    f"Should I change the price of {product_name}?"
                ]
            }
        
        products_sample = ', '.join(self.data_service.get_all_products()[:5])
        return {
            'query': query,
            'response': (
                "👋 I'm RetailMind AI Copilot!\n\n"
                "I can help you with:\n"
                "• Demand forecasting\n"
                "• Pricing optimization\n"
                "• Inventory management\n"
                "• What-if scenarios\n\n"
                f"Available products: {products_sample}, and more..."
            ),
            'intent': 'general',
            'suggestions': [
                "Show me all products",
                "What products are at risk?",
                f"Analyze {self.data_service.get_all_products()[0]}"
            ]
        }


def get_copilot_service() -> CopilotService:
    """Get CopilotService instance"""
    return CopilotService()