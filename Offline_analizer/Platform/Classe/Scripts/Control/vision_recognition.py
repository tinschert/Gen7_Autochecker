# -*- coding: utf-8 -*-
# @file vision_recognition.py
# @author ADAS_HIL_TEAM
# @date 08-21-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import pyautogui
from PIL import ImageGrab,Image
import cv2
import numpy as np
import time
from logging_config import logger
from win32api import GetSystemMetrics
import win32con

pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True

template = Image.open(r'D:\_RBS\_dev\Plamen\1.jpg')


def get_template_size(template):
    """
    

    Args:
      template: 

    Returns:

    """
    w_template, h_template = template.size
    return w_template, h_template


def get_screenshot():
    """ """
    #size = (GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN), GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN))
    size = (1920, 1080)
    im = ImageGrab.grab()
    width, height = im.size
    width_factor = width / size[0]
    height_factor = height / size[1]
    image = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    im.save(r"D:\screenshot.jpg")
    return image, width_factor, height_factor


def resize_template(template, w, h, width_factor,  height_factor):
    """
    

    Args:
      template: 
      w: 
      h: 
      width_factor: 
      height_factor: 

    Returns:

    """
    width_fixed = int(w/width_factor)
    height_fixed = int(h/height_factor)
    size_fixed = (width_fixed, height_fixed)
    template_resized = template.resize(size_fixed, Image.LANCZOS)
    template_resized.save(r"D:\fixed.jpg", quality=100)
    return template_resized, width_fixed, height_fixed


def button_recognition(image, template_fixed, fixed_width, fixed_height):
    """
    

    Args:
      image: 
      template_fixed: 
      fixed_width: 
      fixed_height: 

    Returns:

    """

    template_bgr = cv2.cvtColor(np.array(template_fixed), cv2.COLOR_RGB2BGR)
    template_gray = cv2.cvtColor(template_bgr, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.6
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):
        cv2.rectangle(image, pt, (pt[0] + fixed_width, pt[1] + fixed_height), (0, 255, 255), 2)

    if np.amax(res) > threshold:
        cv2.imwrite(r"D:\detected.jpg", image)
        #print(loc[0])
        #print(loc[1])
        x_coordinate = int(loc[1][0])
        y_coordinate = int(loc[0][0])
        return x_coordinate, y_coordinate
    else:
        x_coordinate = 0
        y_coordinate = 0
        return x_coordinate, y_coordinate


def click_button(x, y):
    """
    

    Args:
      x: 
      y: 

    Returns:

    """
    offset = 15 #offset in pixel to match button center
    pyautogui.click(x+offset, y+offset, button='left')


def start_vision_recognition(wait_before_start):
    """
    

    Args:
      wait_before_start: 

    Returns:

    """
    time.sleep(wait_before_start)
    wait_cycles = 0
    max_wait_cycles = 8
    logger.info("Start Canape vision recognition thread")
    while wait_cycles < max_wait_cycles:
        logger.info(f"Vision recognition attempt --> {wait_cycles}")
        screenshot, x_factor, y_factor = get_screenshot()
        w_template, h_template = get_template_size(template)
        template_fixed, fixed_width, fixed_height = resize_template(template, w_template, h_template, x_factor, y_factor)
        x, y = button_recognition(screenshot, template_fixed, fixed_width, fixed_height)
        if x != 0 and y != 0:
            click_button(x, y)
            click_button(x, y)
            click_button(x, y)
            click_button(x, y)
            exit(0)
        else:
            time.sleep(10)
            wait_cycles += 1
    if wait_cycles >= max_wait_cycles:
        logger.error("Button not recognised")
        raise Exception("Button not recognised")


if __name__ == "__main__":
    start_vision_recognition()





