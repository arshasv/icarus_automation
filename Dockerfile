# Use an official Python base image
FROM python:3.9-slim

# Set environment variables to prevent prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Icarus Verilog and other dependencies
RUN apt-get update && apt-get install -y \
    iverilog \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements.txt first to leverage Docker layer caching
COPY ./requirements.txt /usr/src/app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./app /usr/src/app
COPY ./scripts /usr/src/app/scripts

# Make the shell script executable
RUN chmod +x /usr/src/app/scripts/process_verilog.sh

# Expose the FastAPI port
EXPOSE 8000

# Environment variables for RabbitMQ
ENV RABBITMQ_HOST=localhost
ENV RABBITMQ_PORT=5672
ENV QUEUE_NAME=verilog_processing

# Command to run FastAPI on container startup
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ," cat /usr/src/app/error_log.txt"]
