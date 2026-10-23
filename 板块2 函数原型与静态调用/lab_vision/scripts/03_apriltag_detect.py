#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务三：AprilTag 识别。

assets 里有一张 25h9 家族的标签。
25h9 表示内部是 5x5 个格子，其中 9 个 bit 校验。
它比二维码耐遮挡、算位姿方便，无人机降落和对接常用这个。
你需要解码出这是apriltag5x5家族的哪一个标签。

运行方式：

    cd lab_vision
    python scripts/03_apriltag_detect.py

要点：这玩意太太太简单了没啥要点，调包吧孩子
"""

import os

import cv2
import numpy as np

"""这个部分在找目录"""
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")

IMAGE_PATH = os.path.join(ASSETS, "apriltag_25h9.png")
SAVE_PATH = os.path.join(OUTPUT, "apriltag_result.png")
FAMILY = "25h9"

os.makedirs(OUTPUT, exist_ok=True)

FAMILIES = {
    "16h5": cv2.aruco.DICT_APRILTAG_16H5,
    "25h9": cv2.aruco.DICT_APRILTAG_25H9,
    "36h11": cv2.aruco.DICT_APRILTAG_36H11,
}


def load_image(path):
    """读图，读不到就报错"""
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError("读不到图片：" + path)
    return image


def make_detector(family="25h9"):
    """按家族建检测器。

    返回 (dictionary, detector)。
    """

    dictionary = None
    detector = None

    """ ————————————————————————————填空—————————————————————————————————



    
        ————————————————————————————填空————————————————————————————————— """
    return dictionary, detector


def detect_tags(image, dictionary, detector):
    """检测图里所有标签。

    返回 [{"id": int, "center": (cx, cy), "corners": np.ndarray(4, 2)}, ...]，
    corners 的顺序是左上、右上、右下、左下。
    """
    results = []
    """ ————————————————————————————填空—————————————————————————————————
    




        ————————————————————————————填空————————————————————————————————— """
    return results


def annotate(image, results):
    """把标签的四个角、中心和编号画到图上，返回新图。"""
    canvas = image.copy()
    if len(canvas.shape) == 2:
        canvas = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)

    for item in results:
        points = item["corners"].astype(np.int32)
        cv2.polylines(canvas, [points], True, (0, 255, 0), 2)

        cx, cy = item["center"]
        cv2.circle(canvas, (int(cx), int(cy)), 4, (0, 0, 255), -1)
        cv2.putText(canvas, "id=%d" % item["id"],
                    (int(points[0][0]), max(int(points[0][1]) - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
    return canvas


image = load_image(IMAGE_PATH)
dictionary, detector = make_detector(FAMILY)
results = detect_tags(image, dictionary, detector)

print("家族 %s，检测到 %d 个标签" % (FAMILY, len(results)))
for item in results:
    cx, cy = item["center"]
    print("  id=%d  中心=(%.1f, %.1f)" % (item["id"], cx, cy))
    print("  四角：%s" % np.array2string(item["corners"], precision=1,
                                        separator=", ", suppress_small=True))

if not results:
    print("没有检测到标签")

cv2.imwrite(SAVE_PATH, annotate(image, results))
print("标注图已保存到", SAVE_PATH)
