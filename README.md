# RetailMind AI - InsightOps

**Autonomous Market Intelligence Copilot**

RetailMind AI is an advanced ML Simulator Platform designed to predict demand, optimize pricing, and avoid losses with AI-powered insights. It combines a powerful FastAPI backend with a responsive, interactive frontend to provide a comprehensive retail analytics dashboard.

## 🚀 Features

*   **Demand Forecasting**: Predict future sales trends using sophisticated Machine Learning models.
*   **Smart Pricing**: Get AI-powered pricing recommendations to maximize revenue.
*   **Inventory Intelligence**: Real-time detection of stockouts, overstocking, and inventory health monitoring.
*   **what-If Simulator**: Test various market scenarios and pricing strategies before implementing them.
*   **AI Copilot**: Natural language interface to ask questions about your data and get instant insights.
*   **Interactive Dashboard**: Visual analytics with dynamic charts and real-time updates.

## 🛠️ Technology Stack

*   **Backend**: Python, FastAPI, Uvicorn, Pandas, Scikit-learn
*   **Frontend**: HTML5, CSS3, JavaScript, Jinja2 Templates
*   **Data Processing**: Pandas, NumPy
*   **Architecture**: Monolithic service serving both API and Static/Template content.

## 📋 Prerequisites

*   Python 3.8 or higher
*   pip (Python Package Manager)

## 📂 Project Structure

```text
InsightOps/
├── backend/                # Backend Application Code
│   ├── app/
│   │   ├── api/            # API Route Definitions
│   │   ├── core/           # Core Logic & Config
│   │   ├── models/         # Database Models
│   │   ├── schemas/        # Pydantic Schemas
│   │   ├── services/       # Business Logic Services
│   │   └── main.py         # Application Entry Point
│   ├── data/               # Data Storage
│   └── requirements.txt    # Project Dependencies
├── frontend/               # Frontend Assets
│   ├── static/             # CSS, JS, Images
│   └── templates/          # Jinja2 HTML Templates
└── README.md
```

## 🔍 Key Endpoints

*   `GET /api/v1/products/`: List all products
*   `GET /api/v1/products/{product_name}/analyze`: Detailed product analysis
*   `POST /api/v1/copilot/query`: AI Assistant query interface