"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============= Health Check =============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)


# ============= Error Schemas =============

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ============= Product Schemas =============

class ProductSummary(BaseModel):
    """Summary of a product for dashboard"""
    product_name: str
    risk_level: str
    days_of_stock: float
    demand_trend_pct: float
    current_price: float
    expiry_risk: str
    # Extended fields for dashboard
    pricing_action: Optional[str] = "HOLD"
    confidence_tier: Optional[str] = "MEDIUM"
    market_position: Optional[str] = "N/A"
    risk_reason: Optional[str] = ""


class ProductAnalysisResponse(BaseModel):
    """Complete product analysis response"""
    product_name: str
    current_price: float
    
    # Forecasting
    forecast: Dict[str, Any]
    
    # Inventory Risk
    inventory_risk: Dict[str, Any]
    
    # Pricing
    pricing_recommendation: Dict[str, Any]
    
    # Competition
    competition: Dict[str, Any]
    
    # Seasonality
    seasonality: Dict[str, Any]
    
    # Overall Recommendation
    recommendation: Dict[str, Any]
    
    # Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)


class ProductListResponse(BaseModel):
    """List of available products"""
    products: List[ProductSummary]
    total_count: int


# ============= Forecasting Schemas =============

class ForecastRequest(BaseModel):
    """Request for demand forecasting"""
    product_name: str
    forecast_days: int = Field(default=7, ge=1, le=30)


class ForecastResponse(BaseModel):
    """Demand forecast response"""
    product_name: str
    forecast_days: List[int]
    demand_trend_pct: float
    confidence_score: float
    confidence_tier: str
    last_7d_avg: float


# ============= Pricing Schemas =============

class PricingRecommendationResponse(BaseModel):
    """Pricing recommendation response"""
    product_name: str
    action: str  # INCREASE, DECREASE, HOLD
    reason: str
    current_price: float
    suggested_price: float
    suggested_change_pct: float
    price_volatility: float


# ============= Inventory Schemas =============

class InventoryRiskResponse(BaseModel):
    """Inventory risk assessment response"""
    product_name: str
    risk_level: str  # HIGH_RISK, MEDIUM_RISK, OPPORTUNITY, STABLE
    days_of_stock: float
    reason: str
    current_inventory: int
    avg_daily_sales: float
    expiry_date: str
    expiry_risk: str


# ============= Simulation Schemas =============

class PriceSimulationRequest(BaseModel):
    """Price change simulation request"""
    product_name: str
    new_price: float = Field(gt=0)


class PriceSimulationResponse(BaseModel):
    """Price change simulation response"""
    scenario: str
    price_change_pct: float
    demand_change_pct: float
    new_demand: int
    forecast_new: int
    revenue_change_pct: float
    recommendation: str


class PromotionSimulationRequest(BaseModel):
    """Promotion simulation request"""
    product_name: str
    discount_pct: float = Field(ge=0, le=50)
    duration_days: int = Field(ge=1, le=30)


class PromotionSimulationResponse(BaseModel):
    """Promotion simulation response"""
    scenario: str
    discount_pct: float
    lift_pct: float
    predicted_daily_sales: int
    revenue_impact: float
    is_profitable: bool
    recommendation: str


class InventorySimulationRequest(BaseModel):
    """Inventory change simulation request"""
    product_name: str
    new_stock_days: float = Field(gt=0)


class InventorySimulationResponse(BaseModel):
    """Inventory simulation response"""
    scenario: str
    stock_change_pct: float
    stockout_risk_reduction: float
    holding_cost_change: float
    lost_sales_risk_pct: float
    recommendation: str


# ============= Copilot Schemas =============

class CopilotQueryRequest(BaseModel):
    """AI Copilot natural language query"""
    query: str = Field(min_length=3, max_length=500)
    context: Optional[Dict[str, Any]] = None


class CopilotResponse(BaseModel):
    """AI Copilot response"""
    query: str
    response: str
    intent: str  # forecast, pricing, inventory, simulation, general
    data: Optional[Dict[str, Any]] = None
    suggestions: List[str] = []


# ============= Analytics Schemas =============

class DashboardMetricsResponse(BaseModel):
    """Dashboard overview metrics"""
    total_products: int
    high_risk_products: int
    opportunities: int
    total_inventory_value: float
    avg_days_of_stock: float
    products_expiring_soon: int
    top_growing_products: List[Dict[str, Any]]
    top_declining_products: List[Dict[str, Any]]


# ============= Insights Schemas =============

class InsightsResponse(BaseModel):
    """Business insights response"""
    counts: Dict[str, int]
    insights: List[str]
    high_risk_products: List[str]
    opportunity_products: List[str]
    daily_actions: List[str]
    weekly_strategy: List[str]


# ============= Transaction Schemas =============

class TransactionRequest(BaseModel):
    """Request to record a sale or restock transaction"""
    product_name: str
    quantity: int = Field(gt=0)
    transaction_type: str = Field(pattern="^(SALE|RESTOCK)$")


class TransactionResponse(BaseModel):
    """Response for transaction processing"""
    status: str
    new_inventory: int
    message: Optional[str] = None
