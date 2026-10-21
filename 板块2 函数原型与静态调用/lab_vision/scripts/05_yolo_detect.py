#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务五：YOLO 目标检测框架。

这个脚本只负责"推理 + 画框 + 打印"，模型和图片由你自己补：

    weights/best.pt      你训练好的权重（我暂时不给，第五关才需要）
    assets/yolo_test.jpg  一张待检测的图

    python scripts/05_yolo_detect.py --weights weights/best.pt --source assets/yolo_test.jpg
    python scripts/05_yolo_detect.py --weights yolo11n.pt --source assets/yolo_test.jpg

想先验证环境通不通，可以拿官方小模型顶着用（会自动下载，约 6MB）。
"""

import argparse
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")


def load_model(weights):
    """加载 ultralytics 模型。

    weights 可以是本地 .pt，也可以是模型名（如 yolo11n.pt，会自动下载）。
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        raise ImportError("没装 ultralytics，先执行 pip install ultralytics")

    if os.path.sep in weights and not os.path.exists(weights):
        raise FileNotFoundError(
            "找不到权重文件 %s，确认路径，或者先用 --weights yolo11n.pt 测试" % weights)

    return YOLO(weights)


def detect_objects(model, image, conf=0.25, iou=0.45):
    """跑一次推理，返回检测结果列表。

    每一项是 dict：
        cls_id   类别编号
        cls_name 类别名
        conf     置信度
        xyxy     左上右下像素坐标 (x1, y1, x2, y2)
        center   中心点归一化坐标 (cx, cy)，都在 0 到 1 之间
    """
    results = model.predict(source=image, conf=conf, iou=iou, verbose=False)
    if not results:
        return []

    result = results[0]
    names = result.names
    height, width = image.shape[:2]
    detections = []

    if result.boxes is None:
        return detections

    for box in result.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cls_id = int(box.cls[0].item())
        detections.append({
            "cls_id": cls_id,
            "cls_name": str(names.get(cls_id, cls_id)),
            "conf": float(box.conf[0].item()),
            "xyxy": (x1, y1, x2, y2),
            "center": ((x1 + x2) / 2.0 / width, (y1 + y2) / 2.0 / height),
        })
    detections.sort(key=lambda item: item["conf"], reverse=True)
    return detections


def annotate(image, detections):
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


def main():
    parser = argparse.ArgumentParser(description="YOLO 目标检测")
    parser.add_argument("--weights", default=os.path.join(ROOT, "weights", "best.pt"),
                        help="自己训练的模型，或者官方模型名")
    parser.add_argument("--source", default=os.path.join(ASSETS, "yolo_test.jpg"),
                        help="待检测的图片")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--save", default=os.path.join(OUTPUT, "yolo_result.png"))
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print("找不到图片 %s。把待检测的图放到 assets/yolo_test.jpg，"
              "或者用 --source 指定" % args.source)
        return 1

    image = cv2.imread(args.source)
    if image is None:
        print("图片读不出来，检查格式：" + args.source)
        return 1

    try:
        model = load_model(args.weights)
    except (ImportError, FileNotFoundError) as exc:
        print("加载模型失败：%s" % exc)
        return 1

    detections = detect_objects(model, image, args.conf, args.iou)

    print("检测到 %d 个目标" % len(detections))
    print("%-12s %-6s %-28s %s" % ("类别", "置信度", "框(x1,y1,x2,y2)", "中心归一化"))
    for item in detections:
        print("%-12s %-6.2f %-28s (%.3f, %.3f)" % (
            item["cls_name"], item["conf"],
            str(tuple(int(v) for v in item["xyxy"])),
            item["center"][0], item["center"][1]))

    os.makedirs(os.path.dirname(args.save), exist_ok=True)
    cv2.imwrite(args.save, annotate(image, detections))
    print("标注图已保存到", args.save)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
