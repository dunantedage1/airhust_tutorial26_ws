#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务一：颜色识别。

白底上有红、绿、蓝三个圆，还有一个灰色方块和一个红色小点。
不要识别灰色，红色小点要被过滤掉，所以最终结果是三个。

环境准备：

    pip install numpy opencv-python

启动方式：

    cd lab_vision
    python scripts/01_color_detect.py

思路：OpenCV 读图是 BGR，直接对 BGR 三个通道卡范围得到掩膜，
再找轮廓、算外接圆，最后按面积筛一遍。
"""

import os

import cv2
import numpy as np


"""这个部分在找目录"""
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")
IMAGE_PATH = os.path.join(ASSETS, "color_targets.png")
SAVE_PATH = os.path.join(OUTPUT, "color_result.png")
MIN_AREA = 500

os.makedirs(OUTPUT, exist_ok=True)

# BGR 顺序：蓝、绿、红。每个颜色给一个下界和一个上界。
COLOR_RANGES = {
    "red": ((0, 0, 150), (90, 90, 255)),
    "green": ((0, 150, 0), (90, 255, 90)),
    "blue": ((150, 0, 0), (255, 90, 90)),
}


def color_mask(image, lower, upper):
    """把某一种颜色抠出来，返回 0/255 的单通道掩膜。

    image 是 BGR 图，lower / upper 是这种颜色的 BGR 下界和上界。
    cv2.inRange 会把落在范围内的像素置 255，其余置 0。
    开运算去掉毛刺，闭运算补上圆里的小洞。
    """
    mask = cv2.inRange(image, np.array(lower), np.array(upper))

    """ ————————————————————————————填空—————————————————————————————————




        ————————————————————————————填空————————————————————————————————— """
    return mask


def find_blobs(mask, min_area=MIN_AREA):
    """在一张掩膜里找色块，返回 [(cx, cy, radius, area), ...]。

    用外接圆而不是外接矩形，圆和方块都能描述得差不多。
    面积小于 min_area 的当噪点丢掉。
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    """ ————————————————————————————填空—————————————————————————————————
    

    
        ————————————————————————————填空————————————————————————————————— """
    return blobs


def annotate(image, results):
    """把结果画到图上，返回新图，不改原图"""
    canvas = image.copy()
    for item in results:
        cx, cy = item["center"]
        cv2.circle(canvas, (cx, cy), item["radius"], (0, 0, 0), 2)
        cv2.circle(canvas, (cx, cy), 4, (0, 0, 0), -1)
        label = "%s (%d,%d)" % (item["color"], cx, cy)
        cv2.putText(canvas, label, (cx - 55, cy - item["radius"] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
    return canvas

# 主程序：读图，逐个颜色抠掩膜、找色块，最后画图保存
image = cv2.imread(IMAGE_PATH)
results = []

for name, (lower, upper) in COLOR_RANGES.items():
    mask = color_mask(image, lower, upper)
    """ ————————————————————————————填空—————————————————————————————————
    

    
        ————————————————————————————填空————————————————————————————————— """
    

print("共检测到 %d 个色块" % len(results))

canvas = annotate(image, results)
cv2.imwrite(SAVE_PATH, canvas)
print("标注图已保存到", SAVE_PATH)
