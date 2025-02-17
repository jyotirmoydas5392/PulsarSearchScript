import os

def load_parameters(file_path):
    parameters = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):  # Ignore comments and empty lines
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                try:
                    parameters[key] = eval(value)  # Convert numbers automatically
                except:
                    parameters[key] = value  # Keep as string if eval fails
    return parameters
