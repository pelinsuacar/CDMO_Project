include "globals.mzn";

int: num_items; % Item number
int: num_couriers; % Vehicle number
array [1..num_couriers] of int: load_size; % Vehicle capacities
array [1..num_items] of int: item_size; % Item sizes (demand)

set of int: NODES = 1..num_items+1;
set of int: CUSTOMER = 1..num_items;
set of int: VEHICLE = 1..num_couriers;

array [NODES,NODES] of int: distances;

array[VEHICLE,NODES] of var 1..num_items+1: succ;

array[CUSTOMER] of var 1..num_items: num_visit; % num_visit[i] = j  ->  Customer i is the j-th node visited in their tour
          
%each customer should be visited only once
constraint forall(i in CUSTOMER) (count_eq(succ[..,i],i,num_couriers-1));

%we need a subtour constraint(single,circular tour)
constraint forall(i in VEHICLE)
                  (forall(j in CUSTOMER) (if j != succ[i,j] /\ succ[i,j] != num_items+1 then num_visit[j] < num_visit[succ[i,j]] endif));

%same vehicle cannot visit the same customer again
constraint forall(i in VEHICLE)(alldifferent(succ[i,..]));

%capacity constraint
constraint forall(i in VEHICLE)
                  (sum(j in NODES where succ[i,j]!=j /\ succ[i,j]!=num_items+1)(item_size[succ[i,j]])<= load_size[i]);
                  

%implied constraint                
%if vehicle i does not leave the depot(meaning that it cannot visit any customer) then 
%the whole row belongs to that vehicle should be equal to "CUSTOMER" array
constraint forall(i in VEHICLE)
                  (if succ[i,num_items+1]==num_items+1 then succ[i,..]=NODES endif);
                              
var int: max_dist = max(j in VEHICLE)(sum(i in NODES)(distances[i, succ[j,i]]));

%search
solve :: seq_search([int_search(succ, first_fail, indomain_random),
                    restart_linear(num_items*num_items)
              ])
              
              minimize max_dist;
               
output [
    "Successor = ", show(succ), "\n",
    "Num_visit = ", show(num_visit), "\n",
    "Maximum Distance = ", show(max_dist), "\n"
];
