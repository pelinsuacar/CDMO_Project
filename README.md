# CDMO_Project
Project exam for the course in "Combinatorial Decision Making and Optimization" of the Master's degree in Artificial Intelligence, University of Bologna.
### Contributors
- Pelinsu Acar
- Daniele Napolitano
- Alessandro Folloni

# Docker instructions
First download only the <a href="https://github.com/pelinsuacar/CDMO_Project/blob/main/Dockerfile">Dockerfile</a>, then on the working directory run:

```
sudo docker build . -t cdmo
```
Then to run it and enter the shell:
```
sudo docker run -it cdmo
```

### CP
To run the code for the Constraint Programming part, run the following commands:
```
bash ./CP/run_CP_all_instances.sh <method> <model_name.mzc>
```
Where the possible methods are:
- chuffed
- gecode

### SAT

### MIP
