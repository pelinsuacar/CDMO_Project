#!/bin/bash
if [ $# -eq 4 ] 
then
    echo ""
else
    echo "Invalid Argument: Please pass 4 arguments"
    exit 1
fi

timeout=300000

#Inputs for Minizinc
solver="$1"
model="$2"
instance="$3"
output_file="$4"

#Paths of the model and instance
inst_path="./Instances/$instance"
model_path="./Models/$model"

#Clean output file
> "$output_file"

echo "Solver: $solver" >> "$output_file"
echo "Model: $model" >> "$output_file"

echo "" >> "$output_file"

echo "Running $instance" >> "$output_file"

#Print the minizinc command
echo "Running minizinc --solver $solver --time-limit $timeout --output-time $model_path $inst_path"

SECONDS=0
#Run the minizinc command and print output to the file specified
minizinc --solver $solver --time-limit $timeout --output-time $model_path $inst_path >> "$output_file"
duration=$SECONDS

echo "Finished in $duration seconds"
