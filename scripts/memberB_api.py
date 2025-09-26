from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys
import json

# Add project root to path so we can import scripts
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import scripts.run_detection as rd

app = FastAPI()

class InputData(BaseModel):
    file_path: str

@app.post("/run-agentB")
def run_agent_b(data: InputData):
    input_path = data.file_path

    if not os.path.exists(input_path):
        return {"error": "Input file does not exist"}

    # Overwrite the DATA_PATH in run_detection.py dynamically
    rd.DATA_PATH = input_path

    try:
        rd.main()
    except Exception as e:
        return {"error": str(e)}

    try:
        # Read CSV content
        with open(rd.CSV_OUT, "r") as f:
            csv_content = f.read()

        # Read JSON content
        with open(rd.JSON_OUT, "r") as f:
            json_content = json.load(f)

    except Exception as e:
        return {"error": "Error reading output files: " + str(e)}

    return {
        "status": "success",
        "ml_scores_csv_content": csv_content,
        "anomaly_json_content": json_content
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
