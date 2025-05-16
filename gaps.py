import os
import re

def read_total_distance(filename):
    with open(filename, 'r') as f:
        for line in f:
            if "Total Distance" in line:
                return float(re.findall(r"[\d.]+", line)[0])
    raise ValueError(f"Total Distance not found in file {filename}.")

def get_best_known_solution(instance_name):
    fname = instance_name.upper()
    if 'C104' in fname:
        return 824.78
    elif 'C203' in fname:
        return 588.88
    elif 'C204' in fname:
        return 591.56
    elif 'C205' in fname:
        return 586.39
    elif 'C206' in fname:
        return 586.39
    elif 'C1' in fname:
        return 828.94
    elif 'C2' in fname:
        return 591.56
    else:
        raise ValueError(f"Unknown instance for best known solution: {instance_name}")

def read_instance_name(filename):
    with open(filename, 'r') as f:
        for line in f:
            if line.strip().startswith("Instance:"):
                return line.strip().split("Instance:")[1].strip()
    raise ValueError(f"Instance name not found in file {filename}.")

# Busca todos los archivos output_routes_lns_*.txt en el directorio actual
output_files = [f for f in os.listdir('.') if f.startswith('output_routes_lns_') and f.endswith('.txt')]

results = []
for output_file in output_files:
    try:
        instance_name = read_instance_name(output_file)
        total_distance = read_total_distance(output_file)
        best_known = get_best_known_solution(instance_name)
        gap = ((total_distance - best_known) / best_known) * 100
        results.append((output_file, instance_name, total_distance, best_known, gap))
    except Exception as e:
        results.append((output_file, "ERROR", "-", "-", str(e)))

# Escribe los resultados en un archivo
with open('gaps_summary.txt', 'w') as f:
    f.write("Archivo\tInstancia\tTotalDistance\tBestKnown\tGap (%)\n")
    for row in results:
        f.write(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]}\n")

print("Archivo gaps_summary.txt generado.")