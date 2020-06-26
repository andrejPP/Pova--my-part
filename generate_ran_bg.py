#!/usr/bin/env python3
##########################
#
# Author: Andrej Panicek
# Desc  : From road images generate multiple random crops and save them.
#
##########################
import sys
import os
import cv2
import numpy as np
import argparse

from img_utils import load_img, show_img, store_img

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True, help='Path to directory with backgroun images.')
    parser.add_argument('--dest', required=True, help='Path to directory where generated background images will be stored.')
    parser.add_argument('--amount', type=int, required=True, help='Total amount of generated images.')
    parser.add_argument('--width', type=int, required=True, help='Width of new images.')
    parser.add_argument('--height', type=int, required=True, help="Height of new images.")
    args = parser.parse_args()
    return args


def list_dir_files(path):
   return [os.path.abspath(path + f) for f in os.listdir(path) if os.path.isfile(path + f)] 


def generate_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError as err:
        pass
    except OSError as err:
        raise OSError("Not possible to create dir \" ", path, "\"" , file=sys.stderr)
    return path


def gen_pos_in_img(img_shape, top_pos=0.5):
    
    if np.random.uniform(low=0, high=1) < top_pos:
        rand_y = np.random.randint(low=0, high=img_shape[1]/2)
    else:
        rand_y = np.random.randint(low=img_shape[1]/2, high=img_shape[1])

    rand_x = np.random.randint(low=0, high=img_shape[0])
    return [rand_x, rand_y]

    
def crop_random_part(image, width, height):
    x = image.shape[1]
    y = image.shape[0]
    while (x + width > image.shape[1]) or (y + height > image.shape[0]): 
        x, y = gen_pos_in_img([image.shape[1], image.shape[0]], 0.25)
    
    return image[y:y + height, x:x + width]


def generate_rand_bg():
    """
    Generate random crops from 
    """
    #generate random crops from detesa
    args = parse_arguments()

    background_path = args.src
    background_imgs = list_dir_files(background_path)

    new_bg_dir = args.dest
    generate_dir(new_bg_dir)

    gen_count = len(list_dir_files(new_bg_dir))
    gen_count += 1

    new_size_w = args.width
    new_size_h = args.height

    desired_number_of_samples = args.amount
    per_bg = int(desired_number_of_samples/len(background_imgs))

    for idx, bg_path in enumerate(background_imgs):
        # Iterates over dataset of road background images without signs
        # and from each one of them create multiple random crops.
        bg_img = load_img(bg_path)

        #get rid of black part 
        bg_img = bg_img[0:bg_img.shape[0] - 1000, 0:bg_img.shape[1]]
        
        for x in range(per_bg):
            curr = per_bg * (idx) + x
            total = per_bg * len(background_imgs)
            print("Working on", curr, "/", total)
            cropped = crop_random_part(bg_img, new_size_w, new_size_h)

            name = str(gen_count) + ".jpg"
            path = os.path.join(new_bg_dir, name)
            store_img(path, cropped)
            gen_count += 1
            

if __name__ == "__main__":
    generate_rand_bg()


        





