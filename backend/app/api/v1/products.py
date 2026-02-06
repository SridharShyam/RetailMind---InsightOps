"""
Product analysis API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.schemas import (
    ProductAnalysisResponse,
    ProductListResponse,
    ForecastResponse,
    PricingRecommendationResponse,
    InventoryRiskResponse,
    ErrorResponse,
    TransactionRequest,
    TransactionResponse,
    InsightsResponse
)
from app.services.product_service import ProductService, get_product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(
    service: ProductService = Depends(get_product_service)
):
    """
    Get high-level business insights
    """
    try:
        result = await service.get_insights_summary()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=ProductListResponse)
async def list_products(
    service: ProductService = Depends(get_product_service)
):
    """Get list of all available products"""
    try:
        result = await service.list_products()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_name}/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(
    product_name: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Complete product analysis
    
    Returns:
    - Demand forecast
    - Inventory risk assessment
    - Pricing recommendations
    - Competition analysis
    - Seasonality patterns
    - Overall AI recommendation
    """
    try:
        result = await service.analyze_product(product_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_name}/forecast", response_model=ForecastResponse)
async def get_forecast(
    product_name: str,
    days: int = 7,
    service: ProductService = Depends(get_product_service)
):
    """
    Get demand forecast for a product
    
    Parameters:
    - product_name: Name of the product
    - days: Number of days to forecast (1-30)
    """
    try:
        if days < 1 or days > 30:
            raise HTTPException(status_code=400, detail="Days must be between 1 and 30")
        
        result = await service.get_product_forecast(product_name, days)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_name}/pricing", response_model=PricingRecommendationResponse)
async def get_pricing_recommendation(
    product_name: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Get AI-powered pricing recommendation
    
    Returns:
    - Action (INCREASE, DECREASE, HOLD)
    - Current and suggested price
    - Reasoning
    """
    try:
        result = await service.get_pricing_recommendation(product_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_name}/inventory", response_model=InventoryRiskResponse)
async def get_inventory_risk(
    product_name: str,
    service: ProductService = Depends(get_product_service)
):
    """
    Get inventory risk assessment
    
    Returns:
    - Risk level (HIGH_RISK, MEDIUM_RISK, OPPORTUNITY, STABLE)
    - Days of stock
    - Expiry information
    - Action recommendations
    """
    try:
        result = await service.get_inventory_risk(product_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transaction", response_model=TransactionResponse)
async def process_transaction(
    request: TransactionRequest,
    service: ProductService = Depends(get_product_service)
):
    """
    Process a sales or restock transaction
    
    Effect:
    - Updates inventory count
    - Logs transaction history
    - Updates sales history (if SALE)
    - Affects future forecasts
    """
    try:
        result = await service.process_transaction(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
