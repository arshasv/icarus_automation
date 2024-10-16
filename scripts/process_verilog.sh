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

# Verify the file exists
if [ -f "$v_file_path" ]; then
    echo "Processing $v_file_path with Icarus Verilog..."
    
    # Run Icarus Verilog
    iverilog -o output_file "$v_file_path"
    vvp output_file
    
    echo "Verilog processing completed."
else
    echo "Error: File not found!"
    exit 1
fi
