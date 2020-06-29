#!/usr/bin/env python3
##########################
#
# Author: Andrej Panicek
# Desc  : Create augmented copies of templates.
#
##########################
import sys
import os
import cv2
import copy
import argparse
import imgaug as ia
import imgaug.augmenters as iaa
from imgaug.augmentables import Keypoint, KeypointsOnImage

from templates_utils import load_templates_structure, store_templates_structure, gen_template_dir
from img_utils import *
import numpy as np

# We need to prevent augmentation of ALPHA channel, 
# therefore we define two separate augmentation functions.
#
# seq_affine - affine transformation should be used on every channel (BGRA)
# seq_other -  other transformations which should be used only on color (BGR) channels
seq_affine = iaa.Sequential([
    iaa.Affine(fit_output=True,
               rotate=(-15, 15),
               scale=(0.10, 1),
               shear=(-25, 25)
               ),
    ])
seq_other = iaa.Sequential([
    iaa.Sometimes(0.5, iaa.GammaContrast((0.25, 1.75))),
    iaa.Sometimes(0.5, iaa.MotionBlur((3,5)))
    ])

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', required=True, help='Path to sign templates directory.')
    parser.add_argument('--temp_data', required=True, help='Path to json file which contains description about each sign.')
    parser.add_argument('--dest', required=True, help='Path to directory where augmented images will be stored.')
    parser.add_argument('--count', type=int, required=True, help='How many augmented images create from each sign.')
    parser.add_argument('--max_w', type=int, required=True, help='Maximum width of sign.')
    parser.add_argument('--max_h', type=int, required=True, help='Maximum height of sign.')
    args = parser.parse_args()
    return args


def generate_keypoints(points, img_shape):
    """
    From point stored in [[x coordinate],[y coordinate]] (e.g [[20],[70]]) create 
    Keypoint objects. Keypoint object is needed for imgaug library. 
    """
    key_points = []
    for point in points:
        key_points.append(Keypoint(x=point[0], y=point[1]))
    return KeypointsOnImage(key_points, img_shape)


def lower_values(list_of_values, threshold):
    """
    Count how many values in list are smaler than some threshold.
    """
    lower = 0
    for x in list_of_values:
        if x < threshold:
            lower += 1
    return lower


def fix_points(points, deleted_rows, delete_columns):
    """
    Move points coordinates based on how many columns or rows
    were deleted.
    """
    new_points = []
    for point in points:
        new_x = point[0] - lower_values(delete_columns, point[0])
        new_y = point[1] - lower_values(deleted_rows, point[1])
        new_points.append([new_x, new_y])
    return new_points


def remove_empty_space(image):
    """
    Remove rows and columns from image where values in
    alpha channel equals to zero on every position. 
    """

    alpha = image[:,:,3]
    empty_row = np.zeros(alpha.shape[1], dtype=int)
    empty_column = np.zeros(alpha.shape[0], dtype=int)

    idx_rows = np.argwhere(np.all(alpha[:, ...] == 0, axis=1))
    idx_colm = np.argwhere(np.all(alpha[..., :] == 0, axis=0))
    
    image = np.delete(image, idx_rows, axis=0)
    image = np.delete(image, idx_colm, axis=1)
    
    return image, idx_rows, idx_colm


def augment(image, aug_obj, points_to_keep=[]):
    """
    Augmentation of image. The result is new image with 
    new coordiantes of points.
    """
    if len(points_to_keep) > 0:
        k_points = generate_keypoints(points_to_keep, image.shape)

    img_aug, point_aug = aug_obj(image=image, keypoints=k_points)

    new_points = []
    for i in range(len(point_aug.keypoints)):
        point = point_aug.keypoints[i]
        new_points.append([int(point.x), int(point.y)])

    return img_aug, new_points


def augment_img(image, keypoints):
    """
    Augment input image with two globaly defined transformation
    seq_affine and seq_others.

    Args:
        image: image to be augmented
        keypoints: important points to be recalculated

    Returns:
        Augmented image and new positions of keypoints. 
    """

    #Affine transformation has to applied to every channel.
    #Color variations apply only to color channels.
    #1. Augmentation of every channel in image
    img_aug, points = augment(image, aug_obj=seq_affine, points_to_keep=keypoints)

    #2. Augmentation without alpha channel
    if img_aug.shape[2] == 4:
        b, g, r, alpha = cv2.split(img_aug)
        bgr_image = cv2.merge((b,g,r))

        bgr_aug, points = augment(bgr_image, aug_obj=seq_other, points_to_keep=points)
        fully_aug = cv2.merge((bgr_aug, alpha))

        fully_aug, deleted_rows, deleted_columns = remove_empty_space(fully_aug)
        points = fix_points(points, deleted_rows, deleted_columns)
        
        return fully_aug, points
    else:
        return augment(img_aug, aug_obj=seq_other, points_to_keep=points)


def normalize_size(image, points, max_w, max_h):
    """
   Normalize size of the image and based on that calculate
   new position of important points. The ratio of image sides 
   is preserved.

    Args:
        image: image to be resized
        points: list of points (e.g [[x coordinates, y coordinates], ...])
            for which we calculate coordinates in resized image
        max_w: maximum width of new image
        max_h: maximum height of new image
    
    Returns:
        image: new resized image
        new_points: list of points, with correct coordinates in new image
    """
    origin_w = image.shape[1]
    origin_h = image.shape[0]
    ratio = origin_w / origin_h

    if image.shape[1] > max_w:
        img_w = image.shape[1]
        img_h = image.shape[0]

        dif = img_w - max_w
        new_h =  img_h - int(dif / ratio)
        image = cv2.resize(image, (max_w, new_h), interpolation=cv2.INTER_CUBIC)

    if image.shape[0] > max_h:
        img_w = image.shape[1]
        img_h = image.shape[0]
        
        dif = img_h - max_h
        new_w = img_w - int(dif * ratio)
        image = cv2.resize(image, (new_w, max_h), interpolation=cv2.INTER_CUBIC)

    #calculate correct points position in new image
    res_w = image.shape[1]
    res_h = image.shape[0]
    new_points = []
    
    for point in points:
        new_x = (point[0] / origin_w) * res_w
        new_y = (point[1] / origin_h) * res_h
        new_points.append([int(new_x), int(new_y)])
    
    return image, new_points


def main():
    """
    Create proper directory structure for augmented images of sign templates.
    For each sign template generates number (specified by script argument "count")
    of uniqly augmented images.
    """

    args = parse_arguments()
    root_path = args.dest
    templates_data = load_templates_structure(args.temp_data)
    template_folder = args.src
    aug_count = args.count
    aug_structure = []
    max_width = args.max_w
    max_height = args.max_h

    for temp_index, image_data in enumerate(templates_data):
        
        #generate directory and load template image
        type_dir_path = gen_template_dir(root_path, image_data["type"])
        temp_img = load_img(os.path.join(template_folder, image_data["filename"]), bgra=True)
        norm_img, image_data["points"] = normalize_size(temp_img, image_data["points"], max_width, max_height)

        print("Augmentation of ", temp_index+1, "\\", len(templates_data))
        for idx in range(aug_count):
            #aug_count = number of create augmentations for single sign template
            data = copy.deepcopy(image_data)
            img_aug, data["points"] = augment_img(norm_img, data["points"])

            #store image in new file along with augmented points
            data["filename"] = os.path.join(data["type"], str(idx + 1) + ".png")
            store_img(os.path.join(root_path, data["filename"]), img_aug)
            aug_structure.append(data)

    #store structure 
    store_templates_structure(os.path.join(root_path + "data.json"), aug_structure)


if __name__ == "__main__":
    main()