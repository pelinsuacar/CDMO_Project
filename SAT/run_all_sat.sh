#!/bin/bash

instance_dir="../Instances"

# For each file in the directory
for instance in "$instance_dir"/*.dat; do
  #remove instance_dir from $instance
  filename=$(basename "$instance")
  echo "$filename"

  # Pass the filename to the sat_model.py program
  python3 sat_model.py $filename
done

