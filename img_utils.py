#!/usr/bin/env python3
##########################
#
# Author: Andrej Panicek
#
##########################  
import os
import cv2

def load_img(path, bgra=False):
    if bgra:
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    else:
        image = cv2.imread(path)
    if image is None or image.size == 0:
        raise Exception("Loading image", path, "failed")
    return image


def store_img(path, image):
    cv2.imwrite(path, image)


def show_img(image, desc):
    cv2.namedWindow(desc, cv2.WINDOW_NORMAL)
    cv2.imshow(desc,image)
    cv2.destroyAllWindows()


def draw_points(image, points):
    for edge in points:
        new_image = cv2.circle(image, (edge[0], edge[1]), 3, (0,255,0), 3)
    return new_image