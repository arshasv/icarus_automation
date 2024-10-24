from fastapi import FastAPI, HTTPException, Body, Request
import subprocess
import os
from config import LOCAL_FILE_PATH
from utils import download_blob

app = FastAPI()

@app.post("/process-verilog/")
async def process_verilog(blob_url: str = Body(..., embed=True)):
    try:
        # Extract file name from the passed URL
        blob_name = blob_url.split("/")[-1]
        
        # Set the local file path where the file will be downloaded
        local_file_path = os.path.join(LOCAL_FILE_PATH, blob_name)
        
        # Download the .v file from Azure Blob (or the passed URL)
        download_blob(blob_url, local_file_path)
        
        # Run the shell script to install Icarus Verilog and process the downloaded .v file
        result = subprocess.run([f"./scripts/process_verilog.sh", local_file_path], check=True)
        
        return {"message": "Icarus Verilog container executed successfully"}
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Shell script error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
