
import pandas as pd
from datetime import datetime
from src.load_data import load_retail_data
from src.forecasting import forecast_demand
from src.risk_engine import RiskOpportunityEngine
from src.pricing import recommend_pricing
from src.recommendations import generate_recommendation
from src.seasonality_detector import detect_seasonality
from src.competitive_analyzer import analyze_competition
from src.synergy_analyzer import analyze_synergy
from src.simulator import simulate_price_impact, simulate_promotion, simulate_inventory_change, simulate_competitor_move, simulate_marketing_campaign

class RetailAnalyzer:
    def __init__(self):
        self.data = load_retail_data()
        self.analysis_results = {}
        self.risk_engine = RiskOpportunityEngine()
    
    def process_transaction(self, product_name, quantity=1):
        """
        Ingest a transaction from POS.
        Updates inventory and sales for the product.
        """
        # Find product in data
        mask = self.data['product'] == product_name
        if not mask.any():
            return {'error': f'Product {product_name} not found'}
        
        # Get indices of product rows
        indices = self.data.index[mask]
        last_idx = indices[-1] # Assume chronological order
        
        # Update Inventory (decrease) and Sales (increase)
        # We modify the dataframe in-place for the in-memory session
        current_inventory = self.data.at[last_idx, 'inventory']
        current_sales = self.data.at[last_idx, 'sales']
        
        new_inventory = max(0, current_inventory - quantity)
        new_sales = current_sales + quantity
        
        self.data.at[last_idx, 'inventory'] = new_inventory
        self.data.at[last_idx, 'sales'] = new_sales
        
        # Re-run analysis for this product immediately
        return self.analyze_single_product(product_name)

    def analyze_single_product(self, product):
        """Analyze a single product and update results"""
        product_data = self.data[self.data['product'] == product]
        if product_data.empty:
            return None
            
        latest = product_data.iloc[-1]
        current_price = float(latest['price'])
        
        # Run all analyses
        forecast = forecast_demand(product_data)
        
        # Risk Analysis (Updated)
        risk_metrics = self.risk_engine.calculate_metrics(product_data)
        inventory_risk = self.risk_engine.classify_product_v2(risk_metrics, forecast['demand_trend_pct'])
        
        # Ensure that current_inventory is passed explicitly
        inventory_risk['current_inventory'] = int(latest['inventory'])
        
        pricing = recommend_pricing(product_data, forecast, inventory_risk)
        seasonality = detect_seasonality(product_data)
        competition = analyze_competition(product, current_price)
        synergy = analyze_synergy(product, self.data)
        
        recommendation = generate_recommendation(forecast, inventory_risk, pricing)
        
        result = {
            'forecast': forecast,
            'inventory_risk': inventory_risk,
            'pricing': pricing,
            'seasonality': seasonality,
            'competition': competition,
            'synergy': synergy,
            'recommendation': recommendation,
            'metrics': {
                'current_sales': int(latest['sales']),
                'current_inventory': int(latest['inventory']),
                'current_price': current_price,
                'last_date': latest['date'].strftime('%Y-%m-%d')
            }
        }
        
        self.analysis_results[product] = result
        return result

    def analyze_all_products(self):
        """Run complete analysis for all products"""
        # Load data if not already loaded
        if self.data is None:
            self.data = load_retail_data()
            
        products = self.data['product'].unique()
        results = {}
        
        for product in products:
            res = self.analyze_single_product(product)
            if res:
                results[product] = res
        
        self.analysis_results = results
        return results
    
    def get_simulation(self, product_name, scenario_type, **kwargs):
        """
        Run a specific simulation for a product.
        Args:
            product_name: Name of the product
            scenario_type: 'price_change', 'promotion', or 'inventory_change'
            **kwargs: parameters for the simulation
        """
        if product_name not in self.analysis_results:
            return {'error': 'Product not found'}
            
        current_data = self.analysis_results[product_name]
        metrics = current_data['metrics']
        forecast = current_data['forecast']
        
        current_daily_sales = forecast['last_7d_avg']
        forecast_demand_val = forecast['forecast_next_7_days'][0] # Use next day forecast as base
        
        if scenario_type == 'price_change':
            new_price = float(kwargs.get('new_price', metrics['current_price']))
            return simulate_price_impact(
                metrics['current_price'], 
                new_price, 
                current_daily_sales, 
                forecast_demand_val
            )
            
        elif scenario_type == 'promotion':
            discount_pct = float(kwargs.get('discount_pct', 10))
            duration = int(kwargs.get('duration_days', 7))
            return simulate_promotion(
                metrics['current_price'], 
                discount_pct, 
                duration, 
                current_daily_sales
            )

        elif scenario_type == 'inventory_change':
            # Simulator expects days of stock
            current_days_stock = float(current_data['inventory_risk']['days_of_stock'])
            
            if 'new_stock_units' in kwargs:
                new_stock_units = int(kwargs['new_stock_units'])
                if current_daily_sales > 0:
                    new_stock_days = new_stock_units / current_daily_sales
                else:
                    new_stock_days = 999
            else:
                 new_stock_days = float(kwargs.get('new_stock_days', current_days_stock))
            
            return simulate_inventory_change(
                current_days_stock,
                new_stock_days,
                current_daily_sales,
                metrics['current_price']
            )

        elif scenario_type == 'competitor_move':
            competitor_drop_pct = float(kwargs.get('competitor_drop_pct', 10))
            return simulate_competitor_move(
                metrics['current_price'],
                competitor_drop_pct,
                current_daily_sales
            )

        elif scenario_type == 'marketing':
            ad_spend = float(kwargs.get('ad_spend', 100))
            lift_pct = float(kwargs.get('lift_pct', 10))
            return simulate_marketing_campaign(
                metrics['current_price'],
                current_daily_sales,
                ad_spend,
                lift_pct
            )
            
        return {'error': 'Unknown scenario'}

    def simulate_all_products(self, scenario_type, **kwargs):
        """
        Run a simulation across products with optional segment filtering.
        """
        total_current_revenue = 0
        total_new_revenue = 0
        total_current_demand = 0
        total_new_demand = 0
        
        results = {
            'products_impacted': 0,
            'summary': {},
            'segment': kwargs.get('segment', 'all')
        }
        
        filter_segment = kwargs.get('segment', 'all').upper()
        
        if not self.analysis_results:
            self.analyze_all_products()
            
        for product, data in self.analysis_results.items():
            # Filter Logic
            risk_level = data['inventory_risk']['risk_level']
            if filter_segment != 'ALL':
                if filter_segment == 'HIGH_RISK' and risk_level != 'HIGH_RISK': continue
                if filter_segment == 'OPPORTUNITY' and risk_level != 'OPPORTUNITY': continue
            
            metrics = data['metrics']
            forecast = data['forecast']
            
            # Base values
            current_daily_sales = forecast['last_7d_avg']
            forecast_demand_val = forecast['forecast_next_7_days'][0]
            current_revenue = metrics['current_price'] * current_daily_sales
            
            total_current_revenue += current_revenue
            total_current_demand += current_daily_sales
            
            # Simulate per product
            sim_result = None
            if scenario_type == 'price_change':
                pct_change = float(kwargs.get('pct_change', 0))
                new_price = metrics['current_price'] * (1 + pct_change / 100)
                sim_result = simulate_price_impact(
                    metrics['current_price'], 
                    new_price, 
                    current_daily_sales, 
                    forecast_demand_val
                )
                total_new_revenue += (sim_result['new_demand'] * new_price)
                total_new_demand += sim_result['new_demand']

            elif scenario_type == 'promotion':
                discount_pct = float(kwargs.get('discount_pct', 10))
                duration = int(kwargs.get('duration_days', 7))
                sim_result = simulate_promotion(
                    metrics['current_price'], 
                    discount_pct, 
                    duration, 
                    current_daily_sales
                )
                total_current_revenue += (current_revenue * duration) - current_revenue
                total_new_revenue += (current_revenue * duration) + sim_result['revenue_impact'] - current_revenue
                total_new_demand += sim_result['predicted_daily_sales']

            elif scenario_type == 'marketing':
                # Split total ad spend across products? Or per product? 
                # Let's assume input ad_spend is TOTAL. So we split it evenly or by revenue.
                # Simplified: apply lift to all, subtract cost at end.
                lift_pct = float(kwargs.get('lift_pct', 10))
                
                # Demand increases
                new_demand = current_daily_sales * (1 + lift_pct / 100)
                total_new_demand += new_demand
                total_new_revenue += (new_demand * metrics['current_price'])
                
                sim_result = True # just to count it

            if sim_result:
                 results['products_impacted'] += 1
        
        # Calculate aggregates
        if scenario_type == 'marketing':
            total_ad_spend = float(kwargs.get('ad_spend', 1000))
            # Subtract cost from new revenue to get profit impact? 
            # Or just revenue increase? Usually Revenue is top line.
            # But "revenue_change" usually implies Net Impact for decision making here.
            # Let's keep it as Revenue Change (Gross) and handle cost separately in UI or here?
            # Let's return Pure Revenue Change and let UI subtract cost or return Profit Change.
            # Better: Revenue Change = (New Sales * Price) - (Old Sales * Price)
            # Profit Impact = Revenue Change - Ad Spend
            rev_change_val = total_new_revenue - total_current_revenue
            results['summary']['net_profit_impact'] = round(rev_change_val - total_ad_spend, 2)
        else:
            rev_change_val = total_new_revenue - total_current_revenue
            
        rev_change_pct = (rev_change_val / total_current_revenue * 100) if total_current_revenue > 0 else 0
        
        demand_change_val = total_new_demand - total_current_demand
        demand_change_pct = (demand_change_val / total_current_demand * 100) if total_current_demand > 0 else 0
        
        results['summary'].update({
            'total_revenue_change': round(rev_change_val, 2),
            'revenue_change_pct': round(rev_change_pct, 1),
            'demand_change_pct': round(demand_change_pct, 1),
            'action': 'POSITIVE' if (rev_change_val > 0) else 'NEGATIVE'
        })
        
        if scenario_type == 'marketing':
             results['summary']['action'] = 'POSITIVE' if results['summary']['net_profit_impact'] > 0 else 'NEGATIVE'
        
        return results

    def get_insights_summary(self):
        """Generate understandable business insights in Rupees"""
        if not self.analysis_results:
            self.analyze_all_products()
        
        high_risk = []
        opportunities = []
        price_increases = []
        price_decreases = []
        
        for product, analysis in self.analysis_results.items():
            if analysis['inventory_risk']['risk_level'] == 'HIGH_RISK':
                high_risk.append(product)
            elif analysis['inventory_risk']['risk_level'] == 'OPPORTUNITY':
                opportunities.append(product)
            
            if analysis['pricing']['action'] == 'INCREASE':
                price_increases.append(product)
            elif analysis['pricing']['action'] == 'DECREASE':
                price_decreases.append(product)
        
        # Generate plain English insights - SIMPLER LANGUAGE
        insights = []
        
        if high_risk:
            insights.append(f"⚠️ {len(high_risk)} products have too much stock and low sales (Risk of wastage!)")
        if opportunities:
            insights.append(f"🎯 {len(opportunities)} products are selling fast - buy more before they run out!")
        if price_increases:
            insights.append(f"📈 {len(price_increases)} products are popular - you could slightly raise prices")
        if price_decreases:
            insights.append(f"📉 {len(price_decreases)} products are slow moving - consider a discount")
        
        # Add seasonality insights
        weekend_peaks = [p for p, a in self.analysis_results.items() if a['seasonality']['pattern'] == 'Weekend Peak']
        if weekend_peaks:
            insights.append(f"📅 {len(weekend_peaks)} products sell mostly on weekends (Stock up on Friday!)")

        # Overall health
        total_products = len(self.analysis_results)
        stable_products = total_products - len(high_risk) - len(opportunities)
        insights.append(f"📊 Store Health: {stable_products}/{total_products} products are performing well.")
        
        # Executive Headline
        headline = "Inventory looks stable."
        if len(high_risk) > len(opportunities):
            headline = "Action Needed: You have too much unsold stock!"
        elif len(opportunities) > len(high_risk):
            headline = "Good News: High demand detected! Restock soon."

        return {
            'headline': headline,
            'insights': insights,
            'counts': {
                'total_products': total_products,
                'high_risk': len(high_risk),
                'opportunities': len(opportunities),
                'price_increases': len(price_increases),
                'price_decreases': len(price_decreases)
            },
            'high_risk_products': high_risk,
            'opportunity_products': opportunities
        }
