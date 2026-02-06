def generate_recommendation(forecast_info, inventory_risk, pricing_info):
    """
    Generate clear, understandable AI recommendation with confidence (RUPEES)
    """
    risk_level = inventory_risk['risk_level']
    demand_trend = forecast_info['demand_trend_pct']
    pricing_action = pricing_info['action']
    confidence = forecast_info['confidence_tier']
    expiry_risk = inventory_risk.get('expiry_risk', 'NONE')
    
    # Inventory action based on risk level
    if expiry_risk == 'CRITICAL':
        inventory_action = 'Emergency Sale Required'
        action_reason = inventory_risk.get('reason', f"Product is expiring immediately! {inventory_risk.get('days_of_stock',0)} days of stock left.")
    elif expiry_risk == 'HIGH':
        inventory_action = 'Clearance Sale'
        action_reason = inventory_risk.get('reason', f"Expiring soon. Clear stock now.")
    elif risk_level == 'HIGH_RISK':
        inventory_action = 'Reduce Stock'
        action_reason = f"Too much stock ({inventory_risk['days_of_stock']} days) and fewer people are buying."
    elif risk_level == 'OPPORTUNITY':
        inventory_action = 'Buy More Stock'
        action_reason = f"Selling fast! Low stock ({inventory_risk['days_of_stock']} days) and demand is going up."
    else:
        inventory_action = 'Keep as is'
        action_reason = f"Stock levels are good ({inventory_risk['days_of_stock']} days) and sales are steady."
    
    # Pricing guidance
    if pricing_action == 'INCREASE':
        pricing_guidance = f"Try increasing price by {abs(pricing_info['suggested_change_pct'])}% to ₹{int(pricing_info['suggested_price'])}"
    elif pricing_action == 'DECREASE':
        pricing_guidance = f"Try reducing price by {abs(pricing_info['suggested_change_pct'])}% to ₹{int(pricing_info['suggested_price'])}"
    else:
        pricing_guidance = f"Keep price at ₹{int(pricing_info['current_price'])}"
    
    # Overall summary - simpler language
    trend_desc = 'rising' if demand_trend > 0 else 'falling'
    summary = f"{inventory_action}. {pricing_guidance}. Customer interest is {trend_desc} by {abs(demand_trend)}%."
    
    # Human-readable confidence
    CONFIDENCE_TEXT = {
        "HIGH": "Strong Confidence — data looks very stable.",
        "MEDIUM": "Medium Confidence — some ups and downs.",
        "LOW": "Low Confidence — sales are jumping around a lot."
    }
    
    return {
        'inventory_action': inventory_action,
        'pricing_guidance': pricing_guidance,
        'summary': summary,
        'action_reason': action_reason,
        'confidence': confidence,
        'confidence_text': CONFIDENCE_TEXT.get(confidence, "Thinking... need more data.")
    }