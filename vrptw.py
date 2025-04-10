import math
import time  

# Load data from the file
def load_instance(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Find start of customer section
    start = next(i for i, line in enumerate(lines) if line.strip().startswith("CUSTOMER"))
    customer_lines = lines[start + 2:]  # Skip header

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

# Euclidean distance
def distance(c1, c2):
    return math.hypot(c1['x'] - c2['x'], c1['y'] - c2['y'])

# Insert customer into route if feasible
def is_feasible(route, customer, capacity, current_time):
    if not route:
        return False  # Route cannot be empty

    last = route[-1]
    travel_time = distance(last, customer)
    arrival = current_time + travel_time
    start_service = max(arrival, customer['ready_time'])

    if start_service > customer['due_date']:
        return False
    if sum(c['demand'] for c in route) + customer['demand'] > capacity:
        return False
    return True

def InsertionI1(customers, vehicle_capacity):
    depot = customers[0]
    unrouted = customers[1:]  # Exclude depot
    routes = []
    total_distance = 0  # Initialize total distance

    while unrouted:
        route = [depot]
        current_time = 0
        capacity = 0
        while True:
            feasible_customers = []
            for cust in unrouted:
                if is_feasible(route, cust, vehicle_capacity, current_time):
                    last = route[-1]
                    travel = distance(last, cust)
                    begin_service = max(current_time + travel, cust['ready_time'])
                    cost = travel
                    feasible_customers.append((cost, cust, begin_service))

            if not feasible_customers:
                break

            # Select best (lowest cost)
            feasible_customers.sort(key=lambda x: x[0])
            _, next_cust, start_service = feasible_customers[0]
            route.append(next_cust)
            current_time = start_service + next_cust['service_time']
            capacity += next_cust['demand']
            unrouted.remove(next_cust)

        # Add distance for returning to depot
        route_distance = sum(distance(route[i], route[i + 1]) for i in range(len(route) - 1))
        total_distance += route_distance

        route.append(depot)  # Return to depot
        routes.append(route)

    return routes, total_distance

# Display routes
def print_routes(routes):
    for i, route in enumerate(routes):
        ids = [str(c['id']) for c in route]
        print(f"Route {i + 1}: {' -> '.join(ids)}")

# Run
try:
    start_time = time.time()  # Start timer
    filename = 'C101.txt'  # Replace with your filename
    customers = load_instance(filename)
    NUM_VEHICLES = 25  # Number of vehicles

    # Determine the best-known solution, number of vehicles, and vehicle capacity based on the file
    if 'C1' in filename.upper():
        BEST_KNOWN_SOLUTION = 828.94
        VEHICLE_CAPACITY = 200
    elif 'C2' in filename.upper():
        BEST_KNOWN_SOLUTION = 591.56
        VEHICLE_CAPACITY = 700


    # Calculate vehicle capacity based on the total demand and number of vehicles
    total_demand = sum(c['demand'] for c in customers[1:])  # Exclude depot
    vehicle_capacity = VEHICLE_CAPACITY

    routes, total_distance = InsertionI1(customers, vehicle_capacity)
    end_time = time.time()  # End timer

    # Calculate Gap (%)
    gap = ((total_distance - BEST_KNOWN_SOLUTION) / BEST_KNOWN_SOLUTION) * 100

    # Print results
    print_routes(routes)
    print(f"Instance computed: {filename}")
    print(f"Number of Vehicles: {NUM_VEHICLES}")
    print(f"Vehicle Capacity: {VEHICLE_CAPACITY}")
    print(f"Objective Value (Total Distance): {total_distance:.2f}")
    print(f"Gap (%): {gap:.2f}%")
    print(f"Computation Time: {end_time - start_time:.2f} seconds")
except FileNotFoundError:
    print("Error: File not found. Please check the filename and path.")
except Exception as e:
    print(f"An error occurred: {e}")
