import logging
import subprocess
import os
import json
import pika
from fastapi import FastAPI, HTTPException, Body
from config import LOCAL_FILE_PATH
from utils import download_blob

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

RABBITMQ_HOST = "rabbitmq"
QUEUE_NAME = "verilog_processing"


@app.post("/process-verilog/")
async def process_verilog(blob_url: str = Body(..., embed=True)):
    try:
        blob_name = os.path.basename(blob_url)
        local_file_path = os.path.join(LOCAL_FILE_PATH, blob_name)

        # Download the .v file
        download_blob(blob_url, local_file_path)

        # Define error log file
        error_log_file = "error_log.txt"

        # Remove previous error log if it exists
        if os.path.exists(error_log_file):
            os.remove(error_log_file)

        # Run shell script and capture logs
        result = subprocess.run(
            ["./scripts/process_verilog.sh", local_file_path], 
            text=True, capture_output=True, check=False
        )

        # Read error log if available
        error_log = read_error_log()
        stderr_output = result.stderr.strip() if result.stderr else ""

        if result.returncode != 0 or error_log or stderr_output:
            response_data = {
                "status": "error",
                "message": "Compilation failed",
                "log": error_log if error_log else stderr_output
            }
            send_to_rabbitmq(response_data)
            logging.error(f"Compilation failed: {response_data}")
            raise HTTPException(status_code=400, detail=response_data)

        # Success response
        message = {"status": "success", "message": "Verification successful."}
        send_to_rabbitmq(message)
        logging.info("Verification successful.")
        return message

    except Exception as e:
        error_log = read_error_log()
        response_data = {
            "status": "error",
            "message": "Compilation failed",
            "log": error_log if error_log else str(e)
        }
        send_to_rabbitmq(response_data)
        logging.exception("Unexpected error during processing.")
        raise HTTPException(status_code=400, detail=response_data)


def read_error_log():
    """Reads the contents of error_log.txt if it exists."""
    error_log_file = "error_log.txt"
    if os.path.exists(error_log_file):
        with open(error_log_file, "r") as f:
            return f.read().strip()
    return ""  # Return empty string if no errors are logged


def send_to_rabbitmq(message: dict):
    """Sends a message to RabbitMQ with error handling."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        logging.info(f"Sent message to RabbitMQ: {message}")
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        logging.error(f"Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        logging.error(f"Failed to send message to RabbitMQ: {e}")

