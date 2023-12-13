from itertools import combinations
import json 
from z3 import *

################ ENCODINGS #################

# naive encoding
def at_least_one_np(bool_vars):
    return Or(bool_vars)

def at_most_one_np(bool_vars, name=""):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one_np(bool_vars, name=""):
    return at_most_one_np(bool_vars) + [at_least_one_np(bool_vars)]


#sequential encoding
def at_least_one_seq(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_seq(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    s = [Bool(f"s_{name}_{i}") for i in range(n - 1)] #the trick to distinguish variables is using index numbers
    constraints.append(Or(Not(bool_vars[0]), s[0])) #implication 
    constraints.append(Or(Not(bool_vars[n-1]), Not(s[n-2]))) #s has length n-1
    for i in range(1, n - 1):
        constraints.append(Or(Not(bool_vars[i]), s[i]))
        constraints.append(Or(Not(bool_vars[i]), Not(s[i-1])))
        constraints.append(Or(Not(s[i-1]), s[i]))
    return And(constraints) #CNF

def exactly_one_seq(bool_vars, name):
    return And(at_least_one_seq(bool_vars), at_most_one_seq(bool_vars, name))


#bitwise encoding
def toBinary(num, length = None):
    num_bin = bin(num).split("b")[-1]
    if length:
        return "0"*(length - len(num_bin)) + num_bin
    return num_bin
    
def at_least_one_bw(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_bw(bool_vars, name):
    constraints = []
    n = len(bool_vars)
    m = math.ceil(math.log2(n))
    r = [Bool(f"r_{name}_{i}") for i in range(m)]
    binaries = [toBinary(i, m) for i in range(n)]
    for i in range(n):
        for j in range(m):
            phi = Not(r[j])
            if binaries[i][j] == "1":
                phi = r[j]
            constraints.append(Or(Not(bool_vars[i]), phi))        
    return And(constraints)

def exactly_one_bw(bool_vars, name):
    return And(at_least_one_bw(bool_vars), at_most_one_bw(bool_vars, name)) 


#heule encoding
def at_least_one_he(bool_vars):
    return at_least_one_np(bool_vars)

def at_most_one_he(bool_vars, name):
    if len(bool_vars) <= 4:
        return And(at_most_one_np(bool_vars))
    y = Bool(f"y_{name}")
    return And(And(at_most_one_np(bool_vars[:3] + [y])), And(at_most_one_he(bool_vars[3:] + [Not(y)], name+"_")))

def exactly_one_he(bool_vars, name):
    return And(at_most_one_he(bool_vars, name), at_least_one_he(bool_vars))

###########################################à

# BOOL TO INT FUNCTIONS (for num_visit_bool)
# the int value of the first array must be less than the int value of the second array
def bool_to_int_constraint(b_arr_1, b_arr_2, n_int_encoding):
    return Sum([b_arr_1[i]*(2**i) for i in range(n_int_encoding)]) <  Sum([b_arr_2[i]*(2**i) for i in range(n_int_encoding)])

# useful after solving to convert the num_visit_bool array to an array of integers
def num_visit_bool_to_int(num_visit_bool, n_int_encoding, n):
    final_arr=[]
    for i in range(n):
        sum=0
        for j in range(n_int_encoding):
            if num_visit_bool[i][j]:
                sum+=2**j
        final_arr.append(sum)
    return final_arr


# READ INSTANCE FILE (+ debug prints)
def read_instance(file_path, instance, verbose=True):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        m = int(lines[0])
        n = int(lines[1])
        l = list(map(int, lines[2].split()))
        S = list(map(int, lines[3].split()))
        D = []
        for line in lines[4:]:
            D.append(list(map(int, line.split())))
        n_int_encoding=math.floor(math.log2(n))
        if verbose:
            #debug prints
            print("INSTANCE", instance)
            print("num_couriers:", m)
            print(f"num_items: {n} (num_locations = {n+1}) -> {n_int_encoding} bits for encoding")
            print("max load:", l)
            print("Size of items:", S)
            print("Distance matrix:") #distance is from i(row) to j(column)
            for vector in D:
                print(vector)
            print("-"*30, "\n\n")
        return m, n, l, S, D, n_int_encoding


        
def print_output(model, num_visit, m, n, D, pred, courier_matrix, solution, distance_vect):
    print("num_visit:", num_visit)
    print("\nCOURIER MATRIX:")
    for i in range(m):
        print("courier",i,end=": ")
        print(courier_matrix[i])

    print("\nPREDECESSOR MATRIX:")
    for i in range(-1,n+1):
        for j in range(n):
            if i==-1:
                print(j, end=" ")
            else:
                print(1 if model[pred[i][j]] else 0, end=" ")
        if i==-1:
            print("\n")
        else:
            print(" ", i)

    print("\nSOLUTION:")
    for sol in solution:
        print(sol)

    print("\nDISTANCES:")
    print(distance_vect)

    print("-"*30, "\n")



# MAKE JSON FILE
def make_json(filename, solvers, times, distances, solutions, is_optimal_vec):
    solv = {}
    for solver, max_dist_sol, solution, time, is_optimal in zip(solvers, distances, solutions, times, is_optimal_vec):
        data = {}
        data['time'] = int(time)
        data['optimal']= is_optimal
        data['obj'] = max_dist_sol
        data['sol']= solution
        solv[solver]=data
    #create file and write the dictionary
    with open(filename, 'w') as outfile:
        json.dump(solv, outfile)
        print(f"\nJSON file {filename} created successfully")


