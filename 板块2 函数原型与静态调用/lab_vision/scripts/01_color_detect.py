#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务一：颜色识别。

白底上有红、绿、蓝三个圆，另外还有一个灰色方块和一个红色小点。
灰色不该被识别，红色小点面积太小要被过滤掉，所以最终结果必须是三个。

    python scripts/01_color_detect.py
    python scripts/01_color_detect.py --image assets/color_targets.png --min-area 500

思路：BGR 转 HSV，按色调区间做 inRange 得到掩膜，
再找轮廓、算外接圆，最后按面积和形状筛一遍。
"""

import argparse
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")

# HSV 里红色跨了 0 度，所以要两段区间拼起来
COLOR_RANGES = {
    "red": [((0, 100, 80), (10, 255, 255)),
            ((170, 100, 80), (180, 255, 255))],
    "green": [((40, 80, 60), (85, 255, 255))],
    "blue": [((95, 80, 60), (130, 255, 255))],
}


def load_image(path):
    """读图，读不到就抛错，别静默返回 None。"""
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError("读不到图片：" + path)
    return image


def color_masks(hsv):
    """给每种颜色生成一张二值掩膜。

    返回 dict：{"red": mask, "green": mask, "blue": mask}，
    mask 是 0/255 的单通道图，目标处为 255。
    """
    masks = {}
    for name, ranges in COLOR_RANGES.items():
        mask = np.zeros(hsv.shape[:2], np.uint8)
        for lower, upper in ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, np.array(lower), np.array(upper)))

        # 开运算去掉毛刺，闭运算补上圆里的小洞
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        masks[name] = mask
    return masks


def find_blobs(mask, min_area=500):
    """在一张掩膜里找色块，返回 [(cx, cy, radius, area), ...]。

    用外接圆而不是外接矩形，圆和方块都能描述得差不多，
    面积过滤交给调用方给阈值。
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        (cx, cy), radius = cv2.minEnclosingCircle(contour)
        blobs.append((int(cx), int(cy), int(radius), float(area)))
    return blobs


def detect_colors(image, min_area=500):
    """整条链路：BGR -> HSV -> 掩膜 -> 色块，返回检测结果列表。"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    results = []
    for name, mask in color_masks(hsv).items():
        for cx, cy, radius, area in find_blobs(mask, min_area):
            results.append({
                "color": name,
                "center": (cx, cy),
                "radius": radius,
                "area": area,
            })
    results.sort(key=lambda item: item["center"][0])
    return results


def annotate(image, results):
    """把结果画到图上，返回新图，不改原图。"""
    canvas = image.copy()
    for item in results:
        cx, cy = item["center"]
        cv2.circle(canvas, (cx, cy), item["radius"], (0, 0, 0), 2)
        cv2.circle(canvas, (cx, cy), 4, (0, 0, 0), -1)
        label = "%s (%d,%d)" % (item["color"], cx, cy)
        cv2.putText(canvas, label, (cx - 55, cy - item["radius"] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
    return canvas


def main():
    parser = argparse.ArgumentParser(description="颜色识别")
    parser.add_argument("--image", default=os.path.join(ASSETS, "color_targets.png"))
    parser.add_argument("--min-area", type=float, default=500.0,
                        help="小于这个面积当作噪点丢掉")
    parser.add_argument("--save", default=os.path.join(OUTPUT, "color_result.png"))
    args = parser.parse_args()

    image = load_image(args.image)
    results = detect_colors(image, args.min_area)

    print("共检测到 %d 个色块" % len(results))
    print("%-6s %-12s %-8s %s" % ("颜色", "中心", "半径", "面积"))
    for item in results:
        print("%-6s %-12s %-8d %.0f" % (
            item["color"], str(item["center"]), item["radius"], item["area"]))

    os.makedirs(os.path.dirname(args.save), exist_ok=True)
    cv2.imwrite(args.save, annotate(image, results))
    print("标注图已保存到", args.save)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
