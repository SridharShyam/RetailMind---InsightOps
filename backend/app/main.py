"""
RetailMind AI - FastAPI Application
Main entry point
"""
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.api.v1 import products, simulator, copilot
from app.schemas import HealthResponse, ErrorResponse

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    RetailMind AI - Autonomous Market Intelligence Copilot
    
    Predict demand, optimize pricing, and avoid losses with AI-powered insights.
    
    ## Features
    
    * Demand Forecasting - Predict future sales with ML models
    * Smart Pricing - Get AI-powered pricing recommendations
    * Inventory Intelligence - Avoid stockouts and overstocking
    * What-If Simulator - Test scenarios before making decisions
    * AI Copilot - Natural language interface for insights
    
    ## Quick Start
    
    1. Get all products: `GET /api/v1/products/`
    2. Analyze a product: `GET /api/v1/products/{product_name}/analyze`
    3. Ask AI Copilot: `POST /api/v1/copilot/query`
    
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error="Invalid input",
            detail=str(exc)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.DEBUG else "An error occurred"
        ).model_dump()
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION
    )


# Include routers
app.include_router(products.router, prefix=settings.API_V1_PREFIX)
app.include_router(simulator.router, prefix=settings.API_V1_PREFIX)
app.include_router(copilot.router, prefix=settings.API_V1_PREFIX)

# --- Frontend Integration ---

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
TEMPLATES_DIR = FRONTEND_DIR / "templates"

# Mount Static Files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize Templates
try:
    from fastapi.templating import Jinja2Templates
    import jinja2
    print(f"DEBUG: Jinja2 version {jinja2.__version__} detected.")
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
except ImportError as e:
    print(f"CRITICAL ERROR: Jinja2 Import Failed: {e}")
    # Fallback to prevent crash, but frontend won't work
    templates = None
except Exception as e:
    print(f"CRITICAL ERROR: Template Init Failed: {e}")
    templates = None


# Frontend Routes
@app.get("/", tags=["Frontend"])
async def read_root(request: Request):
    if not templates: return JSONResponse({"error": "Frontend Unavailable (Jinja2 missing)"}, status_code=500)
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/dashboard", tags=["Frontend"])
async def read_dashboard(request: Request):
    if not templates: return JSONResponse({"error": "Frontend Unavailable"}, status_code=500)
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/insights", tags=["Frontend"])
async def read_insights(request: Request):
    if not templates: return JSONResponse({"error": "Frontend Unavailable"}, status_code=500)
    return templates.TemplateResponse("insights.html", {"request": request})


@app.get("/simulator", tags=["Frontend"])
async def read_simulator(request: Request):
    if not templates: return JSONResponse({"error": "Frontend Unavailable"}, status_code=500)
    return templates.TemplateResponse("simulator.html", {"request": request})


@app.get("/about", tags=["Frontend"])
async def read_about(request: Request):
    if not templates: return JSONResponse({"error": "Frontend Unavailable"}, status_code=500)
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/products", tags=["Frontend"])
async def read_products_page(request: Request):
    if not templates: return JSONResponse({"error": "Frontend Unavailable"}, status_code=500)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/product/{product_name}", tags=["Frontend"])
async def read_product_detail(request: Request, product_name: str):
    if not templates: return JSONResponse({"error": "Frontend Unavailable"}, status_code=500)
    
    analysis = None
    try:
        from app.services.product_service import get_product_service
        service = get_product_service()
        # Fetch full analysis for the template
        analysis = await service.analyze_product(product_name)
    except Exception as e:
        print(f"Error fetching analysis for {product_name}: {e}")
    
    return templates.TemplateResponse("product.html", {
        "request": request, 
        "product_name": product_name,
        "analysis": analysis
    })

# Real Upload Endpoint
@app.post("/api/upload_inventory", tags=["Frontend"])
async def upload_inventory(file: UploadFile = File(...)):
    """
    Handle inventory CSV upload from home page.
    """
    import pandas as pd
    import io
    from app.services.data_service import get_data_service
    from app.models import database
    
    try:
        content = await file.read()
        # Decode and read csv
        s = str(content, 'utf-8')
        data = io.StringIO(s)
        df = pd.read_csv(data)
        
        # Merge into DB
        print(f"Received upload: {len(df)} rows")
        result = database.merge_csv_data(df)
        
        if 'error' in result:
             return JSONResponse(status_code=400, content=result)
        
        # Force Reload in Service
        get_data_service().reload_data()
        
        return {
            "status": "success",
            "message": f"Processed {file.filename} successfully. {result.get('products_updated', 0)} products updated.",
            "warnings": []
        }
    except Exception as e:
        print(f"Upload failed: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 60)
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Frontend: http://{settings.HOST}:{settings.PORT}/")
    print("=" * 60)
    
    # Preload data
    try:
        from app.services.data_service import get_data_service
        data_service = get_data_service()
        data_service.load_data()
        print("Data loaded successfully")
    except Exception as e:
        print(f"Warning: Could not preload data - {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print(f"Shutting down {settings.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )