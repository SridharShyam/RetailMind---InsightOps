"""
AI Copilot API endpoints - Natural language interface
"""
from fastapi import APIRouter, HTTPException, Depends

from app.schemas import CopilotQueryRequest, CopilotResponse
from app.services.copilot_service import CopilotService, get_copilot_service

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


@router.post("/query", response_model=CopilotResponse)
async def process_query(
    request: CopilotQueryRequest,
    service: CopilotService = Depends(get_copilot_service)
):
    """
    AI Copilot - Natural language query interface
    
    Ask questions like:
    - "What's the forecast for Coffee Beans?"
    - "Should I increase the price of Fresh Milk?"
    - "What if I reduce Pasta price by 10%?"
    - "Which products are at risk?"
    - "How much inventory should I have for Eggs?"
    
    The AI will understand your intent and provide intelligent responses.
    """
    try:
        result = await service.process_query(request.query, request.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions():
    """
    Get sample queries to help users get started
    """
    return {
        "suggestions": [
            "What's the forecast for Coffee Beans?",
            "Should I change the price of Fresh Milk?",
            "What if I reduce Pasta price by 10%?",
            "Which products have low inventory?",
            "Show me products expiring soon",
            "Analyze Organic Honey",
            "What's the risk level of Artisan Bread?",
            "Simulate a 15% discount on Eggs for 7 days",
            "How much Avocados should I stock?"
        ],
        "categories": {
            "Forecasting": [
                "What will be the demand for [product]?",
                "How many [product] will I sell next week?"
            ],
            "Pricing": [
                "Should I increase price of [product]?",
                "What's the optimal price for [product]?"
            ],
            "Inventory": [
                "Is [product] overstocked?",
                "How many days of stock for [product]?"
            ],
            "Simulation": [
                "What if I reduce [product] price by 10%?",
                "Simulate a promotion on [product]"
            ]
        }
    }