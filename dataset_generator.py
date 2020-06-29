#!/usr/bin/env python3
##########################
#
# Author: Andrej Panicek
# Desc  : Single class for generating datasets structure.
#
##########################  
import os
import sys
from PIL import Image

class DatasetGenerator():
    """
    Generate structure of simple dataset in filesystem.
    Store images in it with proper ground truth.
    """
    
    def __init__(self, dataset_root_path):
        self._gt_path = None
        self._img_path = None
        self._curr_index = None
        self._root_path = dataset_root_path
        self._init_dataset_dirs()
        
    def _init_dataset_dirs(self):
        """
        Check proper structure of dataset dirs.
        """
        self._gt_path =  self._create_dir("gt")
        self._img_path = self._create_dir("images")
        img_count = self._current_count()

    def _create_dir(self, path):
        path = os.path.abspath(os.path.join(self._root_path, path))
        try:
            os.mkdir(path)
        except FileExistsError as err:
            pass
        except OSError as err:
            raise OSError("Not possible to create dir \" ", path, "\"" , file=sys.stderr)
        return path

    def _current_count(self):
        """
        Set index for how many images dataset already contains, so we wont overwritte any of them. 
        """
        self._curr_index = len([image for image in os.listdir(self._img_path) if os.path.isfile(os.path.join(self._img_path, image))])

    def _gen_new_index(self):
        self._curr_index += 1
        return self._curr_index
    
    def add_image(self, image: Image, coords: list, sign_type: str):
        index = str(self._gen_new_index()) 

        bbox = self._transform_coords(coords)
        self._store_image(index, image)
        self._store_data(index, bbox, sign_type)

    def _store_image(self, name, image):
        image_name = name + ".jpg"
        path = os.path.join(self._img_path, image_name)
        image.save(path)
    
    def _store_data(self, name, bbox, sign_type):
        data_name = name + ".txt"
        path = os.path.join(self._gt_path, data_name)

        with open(path, "w") as gt_data:        
            for point in bbox:
                gt_data.write(str(int(point)))
                gt_data.write(" ")

            gt_data.write(sign_type)
        
    def _transform_coords(self, coords: list):
        """
        Transform coordinates from x_start, y_start, x_end, y_end 
        to x_start, y_start, width, height.
        """
        return [coords[0], coords[1],
                coords[2] - coords[0],
                coords[3] - coords[1]]

  

