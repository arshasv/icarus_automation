# Use an official Ubuntu base image
FROM ubuntu:latest

# Set up environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install Icarus Verilog and dependencies
RUN apt-get update && apt-get install -y \
    iverilog \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a directory for the Verilog files
WORKDIR /verilog_files

# Copy the shell script to the container
COPY ./scripts/process_verilog.sh /usr/local/bin/process_verilog.sh
RUN chmod +x /usr/local/bin/process_verilog.sh

# Define entry point (could be overridden in docker-compose or script)
ENTRYPOINT ["/bin/bash"]
