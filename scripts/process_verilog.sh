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

# Define the error log path
error_log="/usr/src/app/error_log.txt"

# Verify the file exists
if [ -f "$v_file_path" ]; then
    echo "Processing $v_file_path with Icarus Verilog..." >> "$error_log"

    # Run Icarus Verilog and capture errors
    if ! iverilog -o output_file "$v_file_path" 2>> "$error_log"; then
        echo "Icarus Verilog compilation failed. Check error_log.txt for details." >> "$error_log"
    else
        vvp output_file >> "$error_log" 2>&1
    fi

    echo "Verilog processing completed." >> "$error_log"
else
    echo "Error: File not found!" >> "$error_log"
    exit 1
fi

# Output the contents of the error log to the container's standard output
echo "---- Error Log ----"
cat "$error_log"