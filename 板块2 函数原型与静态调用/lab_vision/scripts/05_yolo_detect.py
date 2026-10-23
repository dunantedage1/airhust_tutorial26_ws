#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务五：YOLO 目标检测框架。

模型已经训好，认的是奶龙：

    models/best.pt         训练好的权重，直接用
    assets/nailong.jpg     目标原图，也是默认测试图

环境准备：

    pip install ultralytics

运行方式：

    cd lab_vision
    python scripts/05_yolo_detect.py
"""

import os

import cv2

"""这个部分在找目录"""
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")

WEIGHTS = os.path.join(ROOT, "models", "best.pt")
SOURCE = os.path.join(ASSETS, "nailong.jpg")
SAVE_PATH = os.path.join(OUTPUT, "yolo_result.png")
CONF = 0.25
IOU = 0.45

os.makedirs(OUTPUT, exist_ok=True)


def load_model(weights):
    """加载 ultralytics 模型

    """
    try:
        from ultralytics import YOLO
    except ImportError:
        raise ImportError("没装 ultralytics，先执行 pip install ultralytics")

    if os.path.sep in weights and not os.path.exists(weights):
        raise FileNotFoundError(
            "找不到权重文件 %s，确认路径，或者把 WEIGHTS 改成 yolo11n.pt 先测链路" % weights)

    return YOLO(weights)


def detect_objects(model, image, conf=CONF, iou=IOU):
    """跑一次推理，返回检测结果列表。

    每一项是 dict：
        cls_id   类别编号
        cls_name 类别名
        conf     置信度
        xyxy     左上右下像素坐标 (x1, y1, x2, y2)
        center   中心点归一化坐标 (cx, cy)，都在 0 到 1 之间
    """

    detections = []
    """————————————————————————————填空—————————————————————————————————
    



    
       ————————————————————————————填空———————————————————————————————— """

    return detections


def annotate(image, detections):
    """把检测框、类别和置信度画到图上，返回新图。"""
    canvas = image.copy()
    for item in detections:
        x1, y1, x2, y2 = [int(v) for v in item["xyxy"]]
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 200, 0), 2)

        label = "%s %.2f" % (item["cls_name"], item["conf"])
        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(canvas, (x1, y1 - text_h - 6), (x1 + text_w, y1), (0, 200, 0), -1)
        cv2.putText(canvas, label, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 1, cv2.LINE_AA)
    return canvas


if not os.path.exists(SOURCE):
    raise SystemExit("找不到图片：" + SOURCE + "，把图放到 assets/ 下，或者改 SOURCE")

image = cv2.imread(SOURCE)
if image is None:
    raise SystemExit("图片读不出来：" + SOURCE)

model = load_model(WEIGHTS)
detections = detect_objects(model, image, CONF, IOU)

print("检测到 %d 个目标" % len(detections))
print("%-12s %-6s %-28s %s" % ("类别", "置信度", "框(x1,y1,x2,y2)", "中心归一化"))
for item in detections:
    print("%-12s %-6.2f %-28s (%.3f, %.3f)" % (
        item["cls_name"], item["conf"],
        str(tuple(int(v) for v in item["xyxy"])),
        item["center"][0], item["center"][1]))

cv2.imwrite(SAVE_PATH, annotate(image, detections))
print("标注图已保存到", SAVE_PATH)
