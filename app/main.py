from fastapi import FastAPI, HTTPException
import subprocess
import os
from .config import LOCAL_FILE_PATH
from .utils import download_blob

app = FastAPI()

@app.get("/retrieve-latest-v-file")
async def retrieve_latest_v_file():
    """Retrieve the latest .v file from Blob Storage."""
    blob_url = "https://generativeaidocs.blob.core.windows.net/verigen/latest_generated_code.v"
    local_file_path = os.path.join(LOCAL_FILE_PATH, "latest_generated_code.v")

    try:
        download_blob(blob_url, local_file_path)
        return {"message": "Successfully retrieved the latest .v file", "file_path": local_file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-verilog")
async def process_verilog():
    """Process the .v file using Icarus Verilog."""
    local_file_path = os.path.join(LOCAL_FILE_PATH, "latest_generated_code.v")

    if not os.path.exists(local_file_path):
        raise HTTPException(status_code=404, detail="The .v file does not exist. Please retrieve it first.")

    try:
        # Run the shell script with the downloaded file as an argument
        result = subprocess.run([f"./scripts/process_verilog.sh", local_file_path], check=True, capture_output=True, text=True)
        return {"message": "Icarus Verilog processing completed successfully", "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Shell script error: {str(e)}")
