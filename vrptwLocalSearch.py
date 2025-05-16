import math
import time
import random
import copy

def distance(c1, c2):
    return math.hypot(c1['x'] - c2['x'], c1['y'] - c2['y'])

def load_instance(filename):
    # Loads customer data from the original instance file
    with open(filename, 'r') as f:
        lines = f.readlines()
    start = next(i for i, line in enumerate(lines) if line.strip().startswith("CUSTOMER"))
    customer_lines = lines[start + 2:]
    customers = {}
    for line in customer_lines:
        if line.strip() == "":
            continue
        parts = list(map(float, line.strip().split()))
        cust_id = int(parts[0])
        customers[cust_id] = {
            "id": cust_id,
            "x": parts[1],
            "y": parts[2],
            "demand": parts[3],
            "ready_time": parts[4],
            "due_date": parts[5],
            "service_time": parts[6]
        }
    return customers

def load_routes_and_instance_from_file(filename):
    routes = []
    instance_name = None
    with open(filename, 'r') as f:
        for line in f:
            if line.strip().startswith("Instance:"):
                instance_name = line.strip().split("Instance:")[1].strip()
            elif line.strip().startswith("Route"):
                parts = line.strip().split(':')[1].strip().split('->')
                route = [int(x.strip()) for x in parts]
                routes.append(route)
    return instance_name, routes

def route_distance(route, customers_dict):
    return sum(distance(customers_dict[route[i]], customers_dict[route[i+1]]) for i in range(len(route)-1))

def print_routes(routes):
    for i, route in enumerate(routes):
        print(f"Route {i+1}: {' -> '.join(str(cid) for cid in route)}")

def save_routes_to_file(routes, filename, instance_name=None, total_distance=None, computation_time=None):
    with open(filename, 'w') as f:
        if instance_name:
            f.write(f"Instance: {instance_name}\n")
        for i, route in enumerate(routes):
            f.write(f"Route {i+1}: {' -> '.join(str(cid) for cid in route)}\n")
        if total_distance is not None:
            f.write(f"Total Distance: {total_distance:.2f}\n")
        if computation_time is not None:
            f.write(f"Computation Time: {computation_time:.2f} seconds\n")

def flatten_routes(routes):
    # Returns a flat list of customer IDs (excluding depot 0)
    return [cid for route in routes for cid in route if cid != 0]

def is_time_feasible(route, customers_dict):
    time = 0
    for i in range(1, len(route)):
        prev = customers_dict[route[i-1]]
        curr = customers_dict[route[i]]
        travel = distance(prev, curr)
        arrival = time + travel
        start_service = max(arrival, curr['ready_time'])
        if start_service > curr['due_date']:
            return False
        time = start_service + curr['service_time']
    return True

def lns_local_search(routes, customers_dict, vehicle_capacity, max_no_improve=50, removal_fraction=0.2):
    current_routes = copy.deepcopy(routes)
    best_routes = copy.deepcopy(routes)
    best_cost = sum(route_distance(route, customers_dict) for route in routes)
    no_improve_count = 0

    depot_id = 0

    while no_improve_count < max_no_improve:
        # 1. Destroy: remove a fraction of customers
        all_customers = flatten_routes(current_routes)
        num_remove = max(1, int(removal_fraction * len(all_customers)))
        to_remove = random.sample(all_customers, num_remove)

        # Remove customers from routes
        new_routes = []
        for route in current_routes:
            new_route = [cid for cid in route if cid not in to_remove]
            # Ensure depot at start and end
            if new_route[0] != depot_id:
                new_route = [depot_id] + new_route
            if new_route[-1] != depot_id:
                new_route = new_route + [depot_id]
            new_routes.append(new_route)

        # 2. Repair: re-insert removed customers greedily
        unrouted = to_remove[:]
        while unrouted:
            best_insertion = None
            for cust_id in unrouted:
                for r_idx, route in enumerate(new_routes):
                    for pos in range(1, len(route)):
                        # Check capacity constraint
                        demand = sum(customers_dict[cid]['demand'] for cid in route if cid != depot_id) + customers_dict[cust_id]['demand']
                        if demand > vehicle_capacity:
                            continue
                        # Insert and check time window feasibility
                        new_route = route[:pos] + [cust_id] + route[pos:]
                        if not is_time_feasible(new_route, customers_dict):
                            continue
                        cost = route_distance(new_route, customers_dict)
                        if (best_insertion is None) or (cost < best_insertion[0]):
                            best_insertion = (cost, r_idx, pos, cust_id)
            if best_insertion is None:
                # If no feasible insertion, create a new route
                new_routes.append([depot_id, unrouted[0], depot_id])
                unrouted.pop(0)
            else:
                _, r_idx, pos, cust_id = best_insertion
                new_routes[r_idx] = new_routes[r_idx][:pos] + [cust_id] + new_routes[r_idx][pos:]
                unrouted.remove(cust_id)

        # Remove empty routes
        new_routes = [route for route in new_routes if len(route) > 2]

        # 3. Evaluate
        new_cost = sum(route_distance(route, customers_dict) for route in new_routes)
        if new_cost < best_cost:
            best_routes = copy.deepcopy(new_routes)
            best_cost = new_cost
            current_routes = copy.deepcopy(new_routes)
            no_improve_count = 0
        else:
            no_improve_count += 1

    return best_routes, best_cost

# Programa principal
try:
    start_time = time.time()
    routes_filename = 'output_routes_C106.txt'
    instance_name, routes = load_routes_and_instance_from_file(routes_filename)
    if instance_name is None:
        raise ValueError("Instance name not found in routes file.")

    customers_dict = load_instance(instance_name)

    # Set vehicle capacity according to instance
    fname = instance_name.upper()
    if 'C104' in fname:
        VEHICLE_CAPACITY = 200
    elif 'C203' in fname:
        VEHICLE_CAPACITY = 700
    elif 'C204' in fname:
        VEHICLE_CAPACITY = 700
    elif 'C205' in fname:
        VEHICLE_CAPACITY = 700
    elif 'C206' in fname:
        VEHICLE_CAPACITY = 700
    elif 'C1' in fname:
        VEHICLE_CAPACITY = 200
    elif 'C2' in fname:
        VEHICLE_CAPACITY = 700
    else:
        raise ValueError("Error: Unknown instance type in filename.")

    improved_routes, total_distance = lns_local_search(routes, customers_dict, VEHICLE_CAPACITY)

    print_routes(improved_routes)
    end_time = time.time()
    computation_time = end_time - start_time
    output_filename = f"output_routes_lns_{instance_name.split('.')[0]}.txt"
    save_routes_to_file(
        improved_routes,
        output_filename,
        instance_name=instance_name,
        total_distance=total_distance,
        computation_time=computation_time
    )
    print(f"Instance computed: {instance_name}")
    print(f"Number of Vehicles Used: {len(improved_routes)}")
    print(f"Objective Value (Total Distance): {total_distance:.2f}")
    print(f"Computation Time: {computation_time:.2f} seconds")

except FileNotFoundError as e:
    print(e)
except Exception as e:
    print(f"An error occurred: {e}")
