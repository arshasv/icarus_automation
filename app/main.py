from fastapi import FastAPI, HTTPException, Body
import subprocess
import os
import json
import pika
from config import LOCAL_FILE_PATH
from utils import download_blob

app = FastAPI()

RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME = "verilog_processing"


@app.post("/process-verilog/")
async def process_verilog(blob_url: str = Body(..., embed=True)):
    try:
        blob_name = blob_url.split("/")[-1]
        local_file_path = os.path.join(LOCAL_FILE_PATH, blob_name)

        download_blob(blob_url, local_file_path)

        error_log_file = "error_log.txt"

        if os.path.exists(error_log_file):
            os.remove(error_log_file)

        result = subprocess.run(["./scripts/process_verilog.sh", local_file_path], check=False)

        error_log = read_error_log()

        if result.returncode != 0 or error_log:
            response_data = {
                "status": "error",
                "message": "Compilation failed",
                "log": error_log if error_log else "No additional error details available."
            }
            send_to_rabbitmq(response_data)
            raise HTTPException(status_code=200, detail=response_data)

        message = {
        "status": "success", 
        "message": "Verification successful."
        }
        send_to_rabbitmq(message)
        return message

    except Exception as e:
        error_log = read_error_log()
        response_data = {
            "status": "error",
            "message": "Compilation failed",
            "log": error_log if error_log else "No additional error details available."
        }
        send_to_rabbitmq(response_data)
        raise HTTPException(status_code=200, detail=response_data)
    
    except Exception as e:
        message = {
        "status": "success", 
        "message": "Verification successful."
        }
        send_to_rabbitmq(message)
        return message

def read_error_log():
    """Reads the contents of error_log.txt if it exists."""
    error_log_file = "error_log.txt"
    if os.path.exists(error_log_file):
        with open(error_log_file, "r") as f:
            return f.read().strip()
    return "" 

def send_to_rabbitmq(message: dict):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
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
