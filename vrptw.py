import math
import time
import random
import copy

def load_instance(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File '{filename}' not found.")

    start = next(i for i, line in enumerate(lines) if line.strip().startswith("CUSTOMER"))
    customer_lines = lines[start + 2:]

    customers = []
    for line in customer_lines:
        if line.strip() == "":
            continue
        parts = list(map(float, line.strip().split()))
        cust_id = int(parts[0])
        customers.append({
            "id": cust_id,
            "x": parts[1],
            "y": parts[2],
            "demand": parts[3],
            "ready_time": parts[4],
            "due_date": parts[5],
            "service_time": parts[6]
        })

    return customers

def distance(c1, c2):
    return math.hypot(c1['x'] - c2['x'], c1['y'] - c2['y'])

def check_feasibility(route, customer, pos, vehicle_capacity):
    total_demand = sum(c['demand'] for c in route) + customer['demand']
    if total_demand > vehicle_capacity:
        return False

    new_route = route[:pos] + [customer] + route[pos:]

    time_at_node = 0
    for i in range(1, len(new_route)):
        travel = distance(new_route[i-1], new_route[i])
        arrival = time_at_node + travel
        start_service = max(arrival, new_route[i]['ready_time'])
        if start_service > new_route[i]['due_date']:
            return False
        time_at_node = start_service + new_route[i]['service_time']

    return True

def insertion_cost(route, customer, pos):
    prev = route[pos - 1]
    nex = route[pos]
    cost_removed = distance(prev, nex)
    cost_added = distance(prev, customer) + distance(customer, nex)
    return cost_added - cost_removed

def insertion_heuristic(customers, vehicle_capacity, max_vehicles):
    depot = customers[0]
    unrouted = customers[1:]
    routes = []

    while unrouted and len(routes) < max_vehicles:
        route = [depot, depot]
        while True:
            best_insertion = None
            for cust in unrouted:
                for pos in range(1, len(route)):
                    if check_feasibility(route, cust, pos, vehicle_capacity):
                        cost = insertion_cost(route, cust, pos)
                        if (best_insertion is None) or (cost < best_insertion[0]):
                            best_insertion = (cost, cust, pos)

            if best_insertion is None:
                break

            _, cust_to_insert, position = best_insertion
            route = route[:position] + [cust_to_insert] + route[position:]
            unrouted.remove(cust_to_insert)

        routes.append(route)

    if unrouted:
        print("Warning: Not all customers could be routed due to vehicle constraints.")

    routes = [r for r in routes if len(r) > 2]

    total_distance = sum(
        sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))
        for route in routes
    )

    return routes, total_distance

def print_routes(routes):
    for i, route in enumerate(routes):
        ids = [str(c['id']) for c in route]
        print(f"Route {i + 1}: {' -> '.join(ids)}")

def save_routes_to_file(routes, filename, instance_name=None, total_distance=None, computation_time=None):
    with open(filename, 'w') as f:
        if instance_name:
            f.write(f"Instance: {instance_name}\n")
        for i, route in enumerate(routes):
            ids = [str(c['id']) for c in route]
            f.write(f"Route {i + 1}: {' -> '.join(ids)}\n")
        if total_distance is not None:
            f.write(f"Total Distance: {total_distance:.2f}\n")
        if computation_time is not None:
            f.write(f"Computation Time: {computation_time:.2f} seconds\n")

# Programa principal
try:
    start_time = time.time()
    filename = 'C104.txt'
    customers = load_instance(filename)

    NUM_VEHICLES = 25
    fname = filename.upper()
    if 'C104' in fname:
        BEST_KNOWN_SOLUTION = 824.78
        VEHICLE_CAPACITY = 200
    elif 'C203' in fname:
        BEST_KNOWN_SOLUTION = 588.88
        VEHICLE_CAPACITY = 700
    elif 'C204' in fname:
        BEST_KNOWN_SOLUTION = 591.56
        VEHICLE_CAPACITY = 700
    elif 'C205' in fname:
        BEST_KNOWN_SOLUTION = 586.39
        VEHICLE_CAPACITY = 700
    elif 'C206' in fname:
        BEST_KNOWN_SOLUTION = 586.39
        VEHICLE_CAPACITY = 700
    elif 'C1' in fname:
        BEST_KNOWN_SOLUTION = 828.94
        VEHICLE_CAPACITY = 200
    elif 'C2' in fname:
        BEST_KNOWN_SOLUTION = 591.56
        VEHICLE_CAPACITY = 700
    else:
        raise ValueError("Error: Unknown instance type in filename.")

    # Use only the insertion heuristic 
    routes, total_distance = insertion_heuristic(customers, VEHICLE_CAPACITY, NUM_VEHICLES)

    gap = ((total_distance - BEST_KNOWN_SOLUTION) / BEST_KNOWN_SOLUTION) * 100

    print_routes(routes)
    end_time = time.time()
    computation_time = end_time - start_time
    output_filename = f"output_routes_{filename.split('.')[0]}.txt"
    save_routes_to_file(routes, output_filename, instance_name=filename, total_distance=total_distance, computation_time=computation_time)
    print(f"Instance computed: {filename}")
    print(f"Number of Vehicles Used: {len(routes)}")
    print(f"Vehicle Capacity: {VEHICLE_CAPACITY}")
    print(f"Objective Value (Total Distance): {total_distance:.2f}")
    print(f"Gap (%): {gap:.2f}%")
    print(f"Computation Time: {computation_time:.2f} seconds")

except FileNotFoundError as e:
    print(e)
except Exception as e:
    print(f"An error occurred: {e}")
