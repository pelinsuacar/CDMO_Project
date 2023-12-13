from sat_utils import *
import time
import sys

''' RETRIEVE INSTANCE '''
if len(sys.argv) > 1:
    instance_filename = sys.argv[1]
    instance=instance_filename.removeprefix("inst").removesuffix(".dat") #remove prefix and suffix
else:
    print("No instance provided.\nUsage: python sat_model.py inst<num>.dat")
    sys.exit(1)    
m, n, l, S, D, n_int_encoding = read_instance(f"../Instances/inst{instance}.dat", instance)
encodings=["heule", "bitwise"]
solvers=[ "cdcl", "wsat"] 
approaches=["cdcl_he", "wsat_he", "cdcl_bin", "wsat_bin"]
times=[]
solutions=[]
distances=[]
is_optimal_vec=[]

for enc in encodings: #2 loops to try 2 encodings
    print("trying encoding:", enc)
    ''' SET ENCODINGS '''
    if enc=="heule":
        at_least_one=at_least_one_he
        at_most_one=at_most_one_he
        exactly_one=exactly_one_he
    elif enc=="bitwise":
        at_least_one=at_least_one_bw
        at_most_one=at_most_one_bw
        exactly_one=exactly_one_bw


    ''' DECISION VARIABLES '''
    # for each item j, the value is the index of the item that precedes it in the tour [one-hot encoding] (rows=locations(n+1), columns=items (n))
    pred=[[Bool(f"pred_{i}_{j}") for j in range(n)] for i in range(n+1)] 
    # associates items to couriers [one-hot encoding] (i=couriers, j=items)
    courier=[[Bool(f"veichle_{i}_{j}") for j in range(n)] for i in range(m)]
    # an array that stores the order of apparition of any item (i=item, j=value)
    # e.g. if num_visit_bool[0][3] is true, then item 0 is the 4th item in the tour
    num_visit_bool=[[Bool(f"num_visit_bool_{i}_{j}") for j in range(n_int_encoding)] for i in range(n)]
    #last matrix: 1 if item j is the last item in the tour (I.E. next item is depot)
    last=[Bool(f"last_{j}") for j in range(n)] 

    ''' INITIALIZE SOLVER '''
    s=Solver()
    start_time = time.time() #start timer for constraint generation

    ''' ADD CONSTRAINTS '''
    # 1) each item must be assigned to only one courier
    # i.e. for each colum j (item), there must be exactly one element in the row set to 1
    for j in range(n): #for each item
        s.add(exactly_one([courier[i][j] for i in range(m)], name=f"c_{j}"))

    # 2) Each courier must have a total load size $\le$ max load  
    for i in range(m): #for each courier
        s.add(Sum([If(courier[i][j],1,0)*S[j] for j in range(n)]) <= l[i])

    # 3) Predecessor matrix
    # 3.1) in each column, there must be exactly one row element set to 1 (one-hot encoding)
    for j in range(n): #for each column (item)
        s.add(exactly_one([pred[i][j] for i in range(n+1)], name=f"p_{j}"))
    # 3.2) An item can't have itself as predecessor (main diagonal is false)
    for i in range(n):
        for j in range(n):
            if(i==j):
                s.add(Not(pred[i][j]))
    # 3.3) except for last row, in each row there must be at most one 1 
    # (can't have same predecessor, but can be without predecessor in the case last[i]=true)
    for i in range (n): #for all rows (range n since we want to skip the last depot column)
        s.add(at_most_one([pred[i][j] for j in range(n)], name=f"p2_{i}")) 
    # 4) link pred with courier 
    for k in range(m): #for each courier
        for i in range (n): #for each item (column)
            for j in range (n): #for each location (except depot)
                #if item j has predecessor i, and j is carried by courier k, then k also delivers i
                s.add(Implies(And(pred[i][j], courier[k][j]),courier[k][i]==courier[k][j])) 
    # 5) define "last" vector constraints: if the row has all 0s in the columns, then it's the last to be shipped, since its last of no one (last[i]=True), else it's set to false
    for i in range(n):
        #if the row has all 0s in the columns, then it's the last to be shipped, since its last of no one (last[i]=True), else it's set to false
            s.add(last[i] == (If(And([pred[i][j] == False for j in range(n)]), True, False))) #true if row i is empty (all 0s), false otherwise """
    # 5.1) exactly one item in a courier (route) has last=True
    for i in range(m): #for each courier
        #for all items in the courier (which are all the elements of courier[i][j] that are true for each item j) we check that there is exactly one item of those with last=True
        s.add(exactly_one([If(courier[i][j],last[j], False) for j in range(n) ], name=f"last_{i}"))
    # 6) Avoid internal loops (Miller-Tucker-Zemlin subtour elimination constraints)
    for i in range(n):
        for j in range(n):
            if( i!=j ):
                s.add(Implies(pred[i][j],
                            bool_to_int_constraint([num_visit_bool[j][k] for k in range(n_int_encoding)], #1st < 2nd
                                                    [num_visit_bool[i][k] for k in range(n_int_encoding)], 
                                                    n_int_encoding))) 

    print("Total umber of assertions in the model: ", len(s.assertions()))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Time to generate constraints: %.4f" % elapsed_time)
    print("-"*30, "\n")

    ''' SOLVE AND PRINT SOLUTION '''
    timeout=300000 #timeout of 5 minutes = 300 seconds = 300000 milliseconds
    remaining_time=timeout


    for solver in solvers:
        print("\nSOLVING WITH", str.upper(solver), "SOLVER,", enc,"encoding\n")
        if solver!="cdcl":
            s.set(local_search=True, local_search_mode=solver, local_search_threads=12) #wsat and qsat are both variants of local search
        else:
            s.set(threads=12)
        #initialization
        total_tries=0
        start_time = time.time()
        max_bad_tries=250
        num_bad_tries=0
        elapsed_time=0
        best_sol=sys.maxsize
        is_timeout=False
        is_sat=False
        is_optimal=False
        full_exploration=False
        s.push()
        while elapsed_time<300:
            remaining_time=(timeout/1000)-elapsed_time 
            s.set("timeout", int(remaining_time)*1000)
            if s.check() == sat:
                end_time = time.time()
                is_sat=True #if any solution has been found
                elapsed_time = end_time - start_time
                remaining_time=timeout-elapsed_time
                # add the constraint that the solution must be different from the previous one (for the pred matrix)
                model = s.model()
                total_tries+=1

                ''' PROCESS OUTPUT '''
                num_visit=num_visit_bool_to_int([[model[num_visit_bool[i][j]] for j in range(n_int_encoding)] for i in range(n)], n_int_encoding, n)
                #convert one-hot encoding to int for courier matrix
                courier_matrix=[]
                for i in range(m):
                    courier_matrix.append([])
                    for j in range(n):
                        if model[courier[i][j]]:
                            courier_matrix[i].append(j)
                solution=[]
                distance_vect=[]
                for i in range(m): #for couriers
                    succ_vector=[]
                    for j in courier_matrix[i]: #items carried by courier i
                        for k in range(n+1): #for all locations
                            if (model[pred[k][j]] == True): 
                                if(j != k ):
                                    succ_vector.append(j)
                    #order succ vector based on the ordinal values of the num_visit vector
                    succ_vector.sort(key=lambda x: num_visit[x])
                    succ_vector.reverse()
                    sum=0
                    prev=n
                    for k in succ_vector:
                        sum+=D[prev][k]
                        prev=k
                    sum+=D[prev][n]
                    distance_vect.append(sum)
                    solution.append(succ_vector) 
                # add 1 to each value of final_succ_vector (necessary since the checker.py assumes that the first location is 1)
                solution = [[(lambda x: x + 1)(i) for i in vec] for vec in solution]

                ''' OPTIMAL SEARCH '''
                if(max(distance_vect)<best_sol): #"good try" case
                    # save best performing model when found
                    best_sol=max(distance_vect)
                    opt_sol_vect=solution
                    num_bad_tries=0
                else: #"bad try" case
                    num_bad_tries+=1
                
                if(num_bad_tries>=max_bad_tries):
                    print("ending search: no improvement in", max_bad_tries, "tries. total tries=", total_tries, "best=", best_sol)
                    is_optimal=True #assuming this means it's optimal
                    break

                # add constraint to avoid the current solution    
                block_pred=Or([pred[i][j] != model[pred[i][j]] for i in range(n+1) for j in range(n)])
                s.add(block_pred)
            
                print(f"tries: {num_bad_tries}/{max_bad_tries}. best={best_sol}", end="")
                print("\r", end="")

            else:
                if is_sat: #if all solutions have been explored, the best one is surely optimal
                    print("premature exit (all solutions explored). total tries=", total_tries, "best=", best_sol)
                    full_exploration=True
                    is_optimal=True
                    break
                if not is_sat: #if no solution has been found in the time limit, the output is empty
                    print("timeout")
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                    is_timeout=True
                    opt_sol_vect=[]
                    best_sol=0
                    is_optimal=False
                    break

        end_time = time.time()
        elapsed_time = end_time - start_time
        #if at least a solution has been found, but not in 250 good tries, then we assume it's not optimal
        if num_bad_tries<max_bad_tries and elapsed_time>=timeout/1000 and is_sat:
            print("\nSAT but not optimal. Elapsed time: %.4f, tries: %i" % (elapsed_time, total_tries))
            print("Best solution found: ", best_sol)
            is_optimal=False
            elapsed_time=timeout/1000


        solutions.append(opt_sol_vect)
        times.append(elapsed_time)
        distances.append(best_sol)
        is_optimal_vec.append(is_optimal)

        s.pop() #remove all the block constraints added for this solver, before trying the next one
        #print_output(model, num_visit, m, n, D, pred, courier_matrix, solution, distance_vect)       

        
''' CREATE JSON FILE '''
filename="../res/SAT/"+str(instance)+".json"
make_json(filename, approaches, times, distances, solutions, is_optimal_vec)
