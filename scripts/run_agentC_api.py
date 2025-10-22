"""
Member C API - Serves verification_report.json
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import sys

app = FastAPI()

# Path to verification_report.json
VERIFICATION_REPORT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "verification_report.json"
)

@app.get("/get-verification-report")
def get_verification_report():
    """
    Serve verification_report.json to Member D
    """
    if not os.path.exists(VERIFICATION_REPORT_PATH):
        raise HTTPException(status_code=404, detail="verification_report.json not found")
    return FileResponse(
        VERIFICATION_REPORT_PATH,
        media_type='application/json',
        filename="verification_report.json"
    )

if __name__ == "__main__":
    import uvicorn
    
    # Add project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    print(f"Serving verification_report.json from: {VERIFICATION_REPORT_PATH}")
    
    uvicorn.run(
        "scripts.run_agentC_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )