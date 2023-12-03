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

constraint used_couriers = sum(i in CUSTOMER)(last[i]);

constraint global_cardinality(pred, NODES, is_pred ++ [used_couriers]);

constraint forall(i in CUSTOMER)
                 (if pred[i] != num_items+1 then vehicle[i] == vehicle[pred[i]] endif);

%Requires that the number of distinct values in vehicle should be the number of used couriers
constraint nvalue(used_couriers, vehicle);

constraint max(vehicle) = used_couriers;

%constraint num_couriers = used_couriers;

constraint forall(i in CUSTOMER)(is_pred[i] + last[i] = 1);

constraint redundant_constraint(forall(i in CUSTOMER)(pred[i] != i));

%we need a subtour constraint(single,circular tour)
constraint forall(i in CUSTOMER)(if pred[i] != num_items+1 then num_visit[i] > num_visit[pred[i]] endif);


%capacity constraint
constraint forall(j in 1..used_couriers)((sum(i in CUSTOMER where vehicle[i]==j)(item_size[i])) <= load_size[j]);


%Symmetry-breaking constraint
constraint symmetry_breaking_constraint(forall(i, j in VEHICLE where i < j) (
    if load_size[i] == load_size[j] then
        lex_less([vehicle[k] = i| k in CUSTOMER],[vehicle[k] = j| k in CUSTOMER])          
    endif));
 
    
var int: max_dist = max(j in 1..used_couriers)(sum(i in CUSTOMER where vehicle[i]==j)(distances[pred[i],i] + distances[i,num_items+1]*last[i]));


solve   ::  seq_search([
                int_search(vehicle, input_order, indomain_split),
                int_search(pred, first_fail, indomain_split),
                int_search(num_visit, input_order, indomain_min),
                int_search(last, input_order, indomain_split),
                int_search(is_pred, input_order, indomain_split), 
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


