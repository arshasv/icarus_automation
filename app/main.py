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
        blob_name = blob_url.split("/")[-1]
        local_file_path = os.path.join(LOCAL_FILE_PATH, blob_name)

        # Download the .v file
        download_blob(blob_url, local_file_path)

        # Run shell script
        subprocess.run(["./scripts/process_verilog.sh", local_file_path], check=True)

        # Check for error output
        error_file = "error_output.json"
        if os.path.exists(error_file):
            with open(error_file, "r") as f:
                error_data = json.load(f)
            
            send_to_rabbitmq(error_data)  # Send error details to RabbitMQ

            if error_data["status"] == "error":
                raise HTTPException(status_code=500, detail=error_data["message"])

        return {"message": "Icarus Verilog container executed successfully."}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Shell script error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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