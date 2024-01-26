#!/usr/bin/env python
# coding: utf-8

# In[40]:


import os
import json
from collections import defaultdict
import re

def parse_data(instance):
    
    output = {}
    
    for line in instance:
        #elif "Time taken:" in line:
         #   result['time'] = int(float(re.findall(r"\d+\.\d+|\d+", line)[0])) if int(float(re.findall(r"\d+\.\d+|\d+", line)[0])) < 300 else 300
        if "Successor =" in line:
            output['succ'] = list(map(int, re.findall(r"\d+", line)))
        elif "Num_visit =" in line:
            output['num_visit'] = list(map(int, re.findall(r"\d+", line)))
        elif "predecessor =" in line:
            output['pred'] = list(map(int, re.findall(r"\d+", line)))
        elif "last =" in line:
            output['last'] = list(map(int, re.findall(r"\d+", line)))
        elif "vehicle =" in line:
            output['vehicle'] = list(map(int, re.findall(r"\d+", line)))
        elif "total_couriers " in line:
            output['num_courier'] = int(re.findall(r"\d+", line)[0])
        elif "Maximum Distance =" in line:
            output['obj'] = int(re.findall(r"\d+", line)[0])
        elif "Finished in " in line:
            output['time'] = int(re.findall(r"\d+", line)[0])
            
    return output


def find_route_a(succ, num_visit):
    cust_list = {}
    num = len(num_visit) + 1
    loop = int(len(succ)/num)
    
    for i in range(1,loop+1):
        flag = True
        k = i*num-1
        
        if succ[k] != num:
            cust_list[i]=[succ[k]]
            k = (succ[k]-1) + num*(i-1)
        else:
            cust_list[i] = []
            
            
        while flag:
            if succ[k] != num:
                cust_list[i].append(succ[k])
                k = (succ[k]-1) + num*(i-1)
            else:
                flag = False           
    
    return list(cust_list.values())


def find_route_b(pred, last, vehicle, num_courier):
    cust_list = dict.fromkeys(list(range(1,num_courier + 1)), [])
    for i in range(len(last)):
        not_last = True
        if last[i] == 1:
            courier_num = vehicle[i]
            cust_list[courier_num]=[i+1]
            while not_last:
                if pred[i] != len(pred) + 1:
                    cust_list[courier_num].insert(0,pred[i])
                    i = pred[i]-1
                else:
                    not_last = False            
    return list(dict(sorted(cust_list.items())).values())

def main():
    
    input_folder = "./CP/Outputs" #replace this with the path containing .txt files for the outputs
    output_folder = "./res/CP"

    all_instances_data = {1: {}, 2: {}, 3: {}, 4: {}, 5: {} ,6: {}, 7: {}, 8: {}, 9: {}, 10: {}, 11: {}, 12: {}, 13: {}, \
                       14: {}, 15: {}, 16: {}, 17: {}, 18: {}, 19: {}, 20: {}, 21: {}}


    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):

            with open(os.path.join(input_folder, filename), 'r') as f:
                lines = f.read()
                solver_name = lines[0:].split(":")[1].split()[0]
                model_name = lines[0:].split(":")[2].split(".mzn")[0]
                

                groups = [[line.split("  ")[0] for line in group.split("\n") if line != ""] for group in lines.split("\n\n")]

                if 'CP_B' in model_name:

                    for instance in groups[1:]:

                        instance_number = int(re.search(r'\d+', instance[0]).group())
    
                        res = parse_data(instance)
                        try:
                            sol = find_route_b(res['pred'], res['last'], res['vehicle'], res['num_courier'])

                            obj = res["obj"]

                            if res["time"] < 300:
                                opt = True
                            else:
                                opt = False
                                res["time"] = 300

                            data = dict([(model_name,dict([
                                ('time', res["time"]),
                                ('optimal',opt),
                                ('obj', obj),
                                ('sol', sol)
                                ]))])

                        except:
                            data = {}
                            
                        all_instances_data[instance_number].update(data)
                    
                
                elif 'CP_A' in model_name:

                    for instance in groups[1:]:


                        instance_number = int(re.search(r'\d+', instance[0]).group())
        
                        res = parse_data(instance)
                        try:
                            sol = find_route_a(res['succ'], res['num_visit'])
                            obj = res["obj"]

                            if res["time"] < 300:
                                opt = True

                            else:
                                opt = False
                                res["time"] = 300

                            data = dict([(model_name,dict([
                                ('time', res["time"]),
                                ('optimal',opt),
                                ('obj', obj),
                                ('sol', sol)
                                ]))])

                        except:
                            data = {}
                    
                        all_instances_data[instance_number].update(data)

                            
    for instance in all_instances_data.keys():                  
        json_string = json.dumps(all_instances_data[instance])
        json_filename = os.path.join(output_folder, f"{instance}.json")
        with open(json_filename, 'w') as json_file:
            json_file.write(json_string)

if __name__ == "__main__":
    main()

