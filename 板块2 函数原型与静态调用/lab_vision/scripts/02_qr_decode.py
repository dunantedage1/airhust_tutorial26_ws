#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务二：二维码识别。

assets 里有两张二维码，各编码了一个神秘字符串，这一关需要你们编写程序对这两个二维码进行解码

运行方式：

    cd lab_vision
    python scripts/02_qr_decode.py

思路：先BGR图转灰度，先试多码接口，没结果再退回单码接口，最后把四个角画出来。
要点：白边不能裁，解码器靠它找边界。
"""

import os

import cv2
import numpy as np

"""这个部分在找目录"""
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")

IMAGE_PATHS = [
    os.path.join(ASSETS, "qr_1.png"),
    os.path.join(ASSETS, "qr_2.png"),
]

os.makedirs(OUTPUT, exist_ok=True)


def load_image(path):
    """读图，读不到就报错，不静默返回 None。"""
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError("读不到图片：" + path)
    return image


def decode_qr(image):
    """解一张图里的所有二维码。

    返回 [{"text": str, "points": np.ndarray(4, 2)}, ...]。
    points 是二维码四个角的像素坐标，顺序是左上、右上、右下、左下。
    """
    detector = cv2.QRCodeDetector()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    results = []

    """ ————————————————————————————填空—————————————————————————————————





        ————————————————————————————填空————————————————————————————————— """
   
    return results


def annotate(image, results):
    """把二维码的四个角和内容画到图上，返回新图。"""
    canvas = image.copy()
    if len(canvas.shape) == 2:
        canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

    for item in results:
        points = item["points"].astype(np.int32)
        cv2.polylines(canvas, [points], True, (0, 0, 255), 2)

        x, y = points[0]
        cv2.putText(canvas, item["text"], (int(x), max(int(y) - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
    return canvas


for path in IMAGE_PATHS:
    image = load_image(path)
    results = decode_qr(image)

    print("\n图片 %s" % os.path.basename(path))
    if not results:
        print("  没解出二维码")
    for item in results:
        x, y = item["points"].mean(axis=0)
        print("  内容：%s" % item["text"])
        print("  中心：(%.0f, %.0f)" % (x, y))

    name = os.path.splitext(os.path.basename(path))[0]
    save_path = os.path.join(OUTPUT, name + "_result.png")
    cv2.imwrite(save_path, annotate(image, results))
    print("  标注图已保存到 %s" % save_path)
