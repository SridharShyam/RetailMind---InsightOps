try:
    from app.schemas import HealthResponse
    from app.config import get_settings
    print("Imports success.")

    s = get_settings()
    print(f"Settings: {s.APP_VERSION}")

    h = HealthResponse(status="ok", version="1.0")
    print(f"Model created: {h}")
    print(f"Dump: {h.model_dump()}")
    
    print("TestClient check...")
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)
    r = client.get("/health")
    print(f"Response: {r.status_code} {r.text}")

except Exception as e:
    import traceback
    traceback.print_exc()
