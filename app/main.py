from fastapi import FastAPI, HTTPException, Body
import subprocess
import os
import pika
from config import LOCAL_FILE_PATH
from utils import download_blob

app = FastAPI()

# RabbitMQ connection parameters
RABBITMQ_HOST = "localhost"  # Replace with your RabbitMQ host if running remotely
QUEUE_NAME = "verilog_processing"

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
        
        # If processing is successful, send a message to RabbitMQ
        message = {
            "status": "success",
            "file": blob_name,
            "path": local_file_path
        }
        send_to_rabbitmq(message)
        
        return {"message": "Icarus Verilog container executed successfully and message sent to RabbitMQ"}
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Shell script error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def send_to_rabbitmq(message: dict):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost'))
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=str(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        print(f" [x] Sent {message}")
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        raise
    except Exception as e:
        print(f"Failed to send message to RabbitMQ: {e}")
        raise