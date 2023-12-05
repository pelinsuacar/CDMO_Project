#!/bin/bash
if [ $# -eq 2 ] 
then
    echo ""
else
    echo "Invalid Argument: Please pass 2 arguments"
    exit 1
fi

timeout=300000

#Inputs for Minizinc
solver="$1"
model="$2"

model_path="./Models/$model"

model_name="${model%.mzn}"

output_file="${model_name}.txt"

#Clean output file
> "$output_file"

echo "Solver: $solver" >> "$output_file"
echo "Model: $model" >> "$output_file"

echo "" >> "$output_file"

for instance in ./Instances; do

	echo "Running $instance" >> "$output_file"

	#Print the minizinc command
	echo "Running minizinc --solver $solver --time-limit $timeout $model_path $instance"

	SECONDS=0
	#Run the minizinc command and print output to the file specified
	minizinc --solver $solver --time-limit $timeout $model_path $instance >> "$output_file"
	duration=$SECONDS

	echo "Finished in $duration seconds"
	echo "Finished in $duration seconds" >> "$output_file"

	echo "" >> "$output_file"