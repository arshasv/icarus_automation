#!/bin/bash

# Check if Icarus Verilog is installed
if ! command -v iverilog &> /dev/null
then
    echo "Icarus Verilog not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y iverilog
fi

# Get the file path from the first argument
v_file_path=$1

# Define the log file for errors
error_log="error_log.txt"

# Verify the file exists
if [ -f "$v_file_path" ]; then
    echo "Processing $v_file_path with Icarus Verilog..."
    
    # Run Icarus Verilog and capture errors
    iverilog -o output_file "$v_file_path" 2> "$error_log"
    
    # Check if iverilog encountered any errors
    if [ $? -ne 0 ]; then
        echo "Error during iverilog compilation. Check $error_log for details."
        echo "{\"status\":\"error\", \"message\":\"Compilation failed\", \"log\":\"$(cat $error_log)\"}" > error_output.json
        exit 1
    fi
    
    # Run the simulation and capture runtime errors
    vvp output_file 2>> "$error_log"
    
    # Check if vvp encountered any errors
    if [ $? -ne 0 ]; then
        echo "Error during simulation. Check $error_log for details."
        echo "{\"status\":\"error\", \"message\":\"Simulation failed\", \"log\":\"$(cat $error_log)\"}" > error_output.json
        exit 1
    fi
    
    # If no errors, create success output
    echo "{\"status\":\"success\", \"message\":\"Verification successful.\"}" > success_output.json
    exit 0
else
    echo "{\"status\":\"error\", \"message\":\"File not found!\"}" > error_output.json
    exit 1
fi
