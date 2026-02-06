"""
What-if simulator API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Body, Request

from app.schemas import (
    PriceSimulationRequest,
    PriceSimulationResponse,
    PromotionSimulationRequest,
    PromotionSimulationResponse,
    InventorySimulationRequest,
    InventorySimulationResponse
)
from app.services.simulator_service import SimulatorService, get_simulator_service

router = APIRouter(prefix="/simulator", tags=["What-If Simulator"])


@router.post("/{product_name}/price", response_model=PriceSimulationResponse)
async def simulate_price_change(
    product_name: str,
    request: PriceSimulationRequest,
    service: SimulatorService = Depends(get_simulator_service)
):
    """
    Simulate impact of price change
    
    Shows:
    - Demand impact
    - Revenue impact
    - AI recommendation
    """
    try:
        result = await service.simulate_price_change(product_name, request.new_price)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_name}/promotion", response_model=PromotionSimulationResponse)
async def simulate_promotion(
    product_name: str,
    request: PromotionSimulationRequest,
    service: SimulatorService = Depends(get_simulator_service)
):
    """
    Simulate impact of promotional discount
    
    Parameters:
    - discount_pct: Discount percentage (0-50%)
    - duration_days: Duration in days (1-30)
    
    Returns:
    - Sales lift prediction
    - Revenue impact
    - Profitability assessment
    """
    try:
        result = await service.simulate_promotion(
            product_name,
            request.discount_pct,
            request.duration_days
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{product_name}/inventory", response_model=InventorySimulationResponse)
async def simulate_inventory_change(
    product_name: str,
    request: InventorySimulationRequest,
    service: SimulatorService = Depends(get_simulator_service)
):
    """
    Simulate impact of inventory level change
    
    Returns:
    - Stockout risk reduction
    - Holding cost impact
    - Lost sales risk
    - AI recommendation
    """
    try:
        result = await service.simulate_inventory_change(
            product_name,
            request.new_stock_days
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def simulate_global(
    scenario: str,
    request: Request,
    service: SimulatorService = Depends(get_simulator_service)
):
    """
    Simulate impact of a strategy across the entire store (or a sample).
    Supported scenarios: price_change, promotion, marketing
    """
    try:
        # Pass all query params to service
        params = dict(request.query_params)
        result = await service.simulate_global_scenario(scenario, params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_name}/competitor-impact")
async def simulate_competitor_move(
    product_name: str,
    competitor_drop_pct: float,
    service: SimulatorService = Depends(get_simulator_service)
):
    """
    Simulate impact if competitor drops their price
    
    Parameters:
    - competitor_drop_pct: Competitor price reduction percentage
    
    Returns:
    - Impact on your demand
    - Revenue impact
    - Recommended response
    """
    try:
        result = await service.simulate_competitor_move(
            product_name,
            competitor_drop_pct
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_name}/marketing")
async def simulate_marketing_campaign(
    product_name: str,
    ad_spend: float,
    expected_lift_pct: float,
    service: SimulatorService = Depends(get_simulator_service)
):
    """
    Simulate ROI of marketing campaign
    
    Parameters:
    - ad_spend: Marketing budget
    - expected_lift_pct: Expected sales lift percentage
    
    Returns:
    - Revenue increase
    - Break-even analysis
    - ROI recommendation
    """
    try:
        result = await service.simulate_marketing_campaign(
            product_name,
            ad_spend,
            expected_lift_pct
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))