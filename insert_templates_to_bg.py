#!/usr/bin/env python3
##########################
#
# Author: Andrej Panicek
# Desc  : Takes templates images and background images 
#            and add them together.
##########################  
import numpy as np
import os 
import argparse
import cv2
from PIL import Image, ImageDraw
from copy import deepcopy
from random import shuffle

from templates_utils import load_templates_structure
from img_utils import load_img, show_img
from DatasetGenerator import DatasetGenerator

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bg', required=True, help='Path to directory with backgroun images.')
    parser.add_argument('--template', required=True, help='Path to directory with template sign images.')
    parser.add_argument('--det_dataset', required=True, help='Path where to store images for detection dataset.')
    parser.add_argument('--cls_dataset', required=True, help='Path where to store images for clasification dataset.')
    args = parser.parse_args()
    return args


def list_dir_files(path):
   return [os.path.abspath(path + f) for f in os.listdir(path) if os.path.isfile(path + f)] 


def load_temp(path: str):
    #load templates structure
    template_aug_structure = load_templates_structure(os.path.join(path, "data.json"))
    return template_aug_structure 


def load_bg(path: str):
    #load background structure
    background_imgs = list_dir_files(path)
    shuffle(background_imgs)

    return background_imgs


def insert_template(bg_image, temp_image, coords):
    return bg_image + temp_image


def add_aug_signs(bg_image, temp_img, coords, out_of_img=0):
    """
    Add sign template into image of road background.

    Args:
        bg_image: background image
        temp_img: sign template image 
        coords:
        out_of_img: how big partion of sign can outside of image
            interval <0 = none, 1 = whole sign can be out>
    """

    if out_of_img > 1 or out_of_img < 0:
        raise RuntimeError("Wrong usage of \"out_of_image\" parameter. Valid values are between <0,1>")
    
    temp_width, temp_height = temp_img.size

    out_x = max(0, coords[0] + temp_width - (bg_image.size)[0])
    out_y = max(0, coords[1] + temp_height - (bg_image.size)[1])

    if out_of_img != 0:
        valid_out_x = int(temp_width * out_of_img)
        valid_out_y = int(temp_height * out_of_img)
    else:
        valid_out_x = valid_out_y = 0

    #move inside allowed bounderies
    move_x = min(0, valid_out_x - out_x)
    move_y = min(0, valid_out_y - out_y)

    #if image is inside bounderies, coordinates will be moved by 0 pixels 
    coords[0] += move_x
    coords[1] += move_y

    bg_image.paste(temp_img, coords, temp_img)
    bbox = coords

    return bg_image, bbox


def crop_random_part(image, width, height):
    """
    Crop part of image with size specified by args.
    Coordinates generate randomly.

    It's actually the same implementation as in generate_ran_bg.py
    module. Only here I use Pillow Image object instead of Opencv 
    image object. 
    
    Args:
        image: crop this image
        width: width of crop
        height: height of crop
    Returns:
        Created crop as new image.
    """ 

    x = image.size[0]
    y = image.size[1]
    while (x + width > image.size[0]) or (y + height > image.size[1]): 
        x, y = gen_pos_in_img(image.size, 0.25)
    
    return image.crop((x, y, x + width, y + height))


def gen_pos_in_img(img_shape, top_pos=0.5):
    """
    This function generates random position in image.Thus rand_y 
    represent height index in image and rand_x width index.

    In our real life dataset, signs usually dont appear in the top portion
    of the image. Therefore we take that into count and probability 
    of generating position in top part can be specified by top_pos parameter.

    Args:
        top_pos - can be from interval <0,1> (0 meaning position will be
            in bottom half of the image)
    Returns:
        [rand_x, rand_y] - coordinates of generated point
    """
    
    if np.random.uniform(low=0, high=1) < top_pos:
        rand_y = np.random.randint(low=0, high=img_shape[1]/2)
    else:
        rand_y = np.random.randint(low=img_shape[1]/2, high=img_shape[1])

    rand_x = np.random.randint(low=0, high=img_shape[0])
    return [rand_x, rand_y]


def insert_temp_to_bg():
    """
    Add signs templates to images of road background without 
    signs. The position of each template in background is generated
    randomly. 
    Generates two datasets 1. classification dataset 2. detection dataset. 
    """
    args = parse_arguments()
    class_dataset = DatasetGenerator(args.cls_dataset)
    detection_dataset = DatasetGenerator(args.det_dataset)

    template_aug_structure = load_temp(args.template)
    background_imgs  = load_bg(args.bg)

    for idx, temp in enumerate(template_aug_structure):
        print("Progress: ", idx, "/", len(template_aug_structure))

        # open augmented sign image
        temp_img =  Image.open(os.path.join(args.template, temp["filename"]))
        temp_width, temp_height = temp_img.size
        width_offset = int(temp_width * 0.08)
        height_offset = int(temp_height * 0.08)

        # load background image 
        bg_img = Image.open(background_imgs.pop())
        bg_for_det_dataset = deepcopy(bg_img)
        bg_for_cls_dataset = crop_random_part(deepcopy(bg_img), temp_width + width_offset + 1, temp_height + height_offset + 1)

        # add them together
        rand_pos = gen_pos_in_img(bg_for_det_dataset.size)
        image, bbox = add_aug_signs(bg_for_det_dataset, temp_img, rand_pos)
        detection_dataset.add_image(image, bbox, temp["type"])

        image, bbox = add_aug_signs(bg_for_cls_dataset, temp_img, [int(width_offset/2), int(height_offset/2)])
        class_dataset.add_image(image, bbox, temp["type"])

        del(bg_img)
        del(bg_for_cls_dataset)
        del(bg_for_det_dataset)

if __name__ == "__main__":
    insert_temp_to_bg()