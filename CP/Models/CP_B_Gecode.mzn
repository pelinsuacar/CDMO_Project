include "globals.mzn";

int: num_items; % Item number
int: num_couriers; % Vehicle number
array [1..num_couriers] of int: load_size; % Vehicle capacities
array [1..num_items] of int: item_size; % Item sizes (demand)

set of int: NODES = 1..num_items+1;
set of int: CUSTOMER = 1..num_items;
set of int: VEHICLE = 1..num_couriers;

array [NODES,NODES] of int: distances;

array [CUSTOMER] of var NODES: pred;
array [CUSTOMER] of var 0..1: last;
array [CUSTOMER] of var 0..1: is_pred;
array [CUSTOMER] of var VEHICLE: vehicle;
array [CUSTOMER] of var CUSTOMER: num_visit;
var VEHICLE: used_couriers;

%Number of used vehicles should be equal to the number of vehicles returning to the depot
constraint used_couriers = sum(i in CUSTOMER)(last[i]);

constraint global_cardinality(pred, NODES, is_pred ++ [used_couriers]);

%assign vehicles to the customers according to their predecessors
constraint forall(i in CUSTOMER)
                 (if pred[i] != num_items+1 then vehicle[i] == vehicle[pred[i]] endif);

%Requires that the number of distinct values in vehicle should be the number of used couriers
constraint nvalue(used_couriers, vehicle);

%max number in the vehicle array should be equal to the number of used vehicles
constraint max(vehicle) = used_couriers;

%a node cannot be both a predecessor and a last node
constraint forall(i in CUSTOMER)(is_pred[i] + last[i] = 1);

%a customer cannot be its own predecessor
constraint redundant_constraint(forall(i in CUSTOMER)(pred[i] != i));

%we need a subtour constraint(single,circular tour)
constraint forall(i in CUSTOMER)(if pred[i] != num_items+1 then num_visit[i] > num_visit[pred[i]] endif);

%capacity constraint
constraint forall(j in 1..used_couriers)((sum(i in CUSTOMER where vehicle[i]==j)(item_size[i])) <= load_size[j]);

%Objective function
var int: max_dist = max(j in 1..used_couriers)(sum(i in CUSTOMER where vehicle[i]==j)(distances[pred[i],i] + distances[i,num_items+1]*last[i]));


solve :: seq_search([int_search(vehicle, dom_w_deg, indomain_random),
                int_search(pred, dom_w_deg, indomain_random),   
                int_search(last, dom_w_deg, indomain_random),
                int_search(num_visit, dom_w_deg, indomain_random), 
                int_search(is_pred, dom_w_deg, indomain_random),           
                relax_and_reconstruct(pred, 88),
                restart_linear(num_items*num_items)
              ])
              
              minimize max_dist;

 
output [
    "predecessor = ", show(pred), "\n",
    "last = ", show(last), "\n",
    "is_pred = ", show(is_pred), "\n",
    "vehicle = ", show(vehicle), "\n",
    "used_couriers = ", show(used_couriers), "\n",
    "Maximum Distance = ", show(max_dist), "\n"
];


