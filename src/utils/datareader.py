import json
import os

def main():
    pass
def test_data_extractor(split):
    data = test_data_reader(split)
    return data

def test_data_reader(split):
    
    if split == "static":
        data_file_path = get_data_file_path('Beagle-web-static.json')
    elif split == "blog":
        data_file_path = get_data_file_path('Beagle-blog.json')
    elif split == "life":
        data_file_path = get_data_file_path('Beagle-life.json')
    else :
        data_file_path = get_data_file_path('Beagle-web-app.json')
    
    data = read_json_file(data_file_path)
    return data
def env_data_extractor(env):
    data = env_reader()
    return data[env]

def env_reader():
    data_file_path = get_env_file_path('Env.json')
    data = read_json_file(data_file_path)
    return data

def read_json_file(file_path):
    """Read a JSON file and return its content."""
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_env_file_path(filename):
    """Construct the absolute path to a data file in the data directory."""
    current_dir = os.path.dirname(__file__)
    data_file_path = os.path.join(current_dir, '..', '..', 'config', 'Env.json')
    return os.path.abspath(data_file_path)

def get_data_file_path(filename):
    """Construct the absolute path to a data file in the data directory."""
    current_dir = os.path.dirname(__file__)
    data_file_path = os.path.join(current_dir, '..', '..', 'data', filename)
    return os.path.abspath(data_file_path)

if __name__ == "__main__":

    main()