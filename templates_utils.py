##########################
#
# Author: Andrej Panicek
# Desc  : Create augmented copies of templates.
#
##########################
import json
import os
import sys

def load_templates_structure(str):
    with open(path, 'r') as temp_file:
        struct = json.load(temp_file)
    return struct

def store_templates_structure(str, list):
    if not os.path.exists(path):
        open(path, 'a').close()
    with open(path, 'w') as temp_file:
        temp_file.write("[\n")
        last_one_stamp = data[-1]

        for image in data:
            json.dump(image, temp_file)
            #in case of last dont print comma
            if image == last_one_stamp:
                temp_file.write("\n")
            else:
                temp_file.write(",\n")
        temp_file.write("]")
    
def gen_template_dir(root_path, name):
    path = os.path.abspath(os.path.join(root_path, name))
    try:
        os.mkdir(path)
    except FileExistsError as err:
        pass
    except OSError as err:
        raise OSError("Not possible to create dir \" ", path, "\"" , file=sys.stderr)
    return path

    
