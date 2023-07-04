import os
import importlib

prohibit_load = ['__init__']

for endpoint in os.listdir(os.path.dirname(__file__)):
    module_name, ext = os.path.splitext(endpoint)
    if module_name in prohibit_load or ext != '.py':
        continue

    try:
        # Import the module and add it to the global symbol table
        globals()[module_name] = importlib.import_module('.' + module_name, package=__name__)
    except ImportError as e:
        print(f"Failed to import module '{module_name}': {e}")