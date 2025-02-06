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

        # Download the .v file
        download_blob(blob_url, local_file_path)

        # Run shell script
        subprocess.run(["./scripts/process_verilog.sh", local_file_path], check=True)

        # Check for output files
        error_file = "error_output.json"
        success_file = "success_output.json"

        if os.path.exists(error_file):
            with open(error_file, "r") as f:
                error_data = json.load(f)

            print(f" [x] Sent {error_data}")  # Log the error message before raising an exception
            send_to_rabbitmq(error_data)
            raise HTTPException(status_code=500, detail=error_data["message"])

        if os.path.exists(success_file):
            with open(success_file, "r") as f:
                success_data = json.load(f)

            print(f" [x] Sent {success_data}")  # Log the success message
            send_to_rabbitmq(success_data)
            return success_data

        # If neither file exists, assume an unknown failure
        raise HTTPException(status_code=500, detail="Unexpected error occurred. No output file was created.")

    except subprocess.CalledProcessError as e:
        error_message = {"status": "error", "message": f"Shell script error: {str(e)}"}
        print(f" [x] Sent {error_message}")  # Log the error before raising
        send_to_rabbitmq(error_message)
        raise HTTPException(status_code=500, detail=error_message["message"])

    except Exception as e:
        error_message = {"status": "error", "message": str(e)}
        print(f" [x] Sent {error_message}")  # Log the error before raising
        send_to_rabbitmq(error_message)
        raise HTTPException(status_code=500, detail=error_message["message"])


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
        print(f" [x] Sent {message}")  # Log every message sent to RabbitMQ
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        raise
    except Exception as e:
        print(f"Failed to send message to RabbitMQ: {e}")
        raise
