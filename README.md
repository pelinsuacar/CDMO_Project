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
Since we used the Gurobi solver, a <a href="https://www.gurobi.com/solutions/gurobi-optimizer/?campaignid=2027425882&adgroupid=138872525680&creative=596136109143&keyword=gurobi%20license&matchtype=e&_bn=g&gad_source=1&gclid=CjwKCAiAzc2tBhA6EiwArv-i6QzG3C48HySxbs07F6mmt1CsZH_kHf4i3Iz25G8J2SFh1Qj67lGefhoCAncQAvD_BwE">licence</a> is needed in order to run the biggest instances.<br>
You will need to add your **license code** in the following lines and uncomment them before running the model:
``` python
"""LICENSE"""
# LICENSE FOR ACADEMIC VERSION OF GUROBI
# Create an environment with your WLS license
#params = {    }
#env = gp.Env(params=params)
```
After doing that, you can run the model with the following command:
```
./MIP/MIP.py
```

