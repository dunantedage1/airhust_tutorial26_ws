#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务二：二维码识别。

assets 里有两张二维码，分别编码了 harrypjh 和 dunantedage1。
OpenCV 自带 QRCodeDetector，不用装 zbar，也不用联网。

    python scripts/02_qr_decode.py
    python scripts/02_qr_decode.py --image assets/qr_harrypjh.png

要点：喂灰度图、先把多码接口试一遍、失败了再退到单码接口。
"""

import argparse
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")


def load_image(path):
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

    # 4.3 以后才有 detectAndDecodeMulti，一张图里有多码时用它更稳
    if hasattr(detector, "detectAndDecodeMulti"):
        ok, texts, points, _ = detector.detectAndDecodeMulti(gray)
        if ok and points is not None:
            for text, corner in zip(texts, points):
                if not text:
                    continue
                results.append({
                    "text": text,
                    "points": np.array(corner, dtype=np.float32).reshape(4, 2),
                })

    # 多码接口没结果（或老版本 OpenCV）时，退回单码接口
    if not results:
        text, points, _ = detector.detectAndDecode(gray)
        if text and points is not None:
            results.append({
                "text": text,
                "points": np.array(points, dtype=np.float32).reshape(4, 2),
            })
    return results


def annotate(image, results):
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


def main():
    parser = argparse.ArgumentParser(description="二维码识别")
    parser.add_argument("--image", nargs="+",
                        default=[os.path.join(ASSETS, "qr_harrypjh.png"),
                                 os.path.join(ASSETS, "qr_dunantedage1.png")])
    parser.add_argument("--save", default=os.path.join(OUTPUT, "qr_result.png"))
    args = parser.parse_args()

    all_results = []
    for path in args.image:
        image = load_image(path)
        results = decode_qr(image)
        print("\n图片 %s" % os.path.basename(path))
        if not results:
            print("  没解出二维码，检查图片是否完整、白边够不够")
        for item in results:
            x, y = item["points"].mean(axis=0)
            print("  内容：%s" % item["text"])
            print("  中心：(%.0f, %.0f)" % (x, y))
        all_results.append((image, results))

    # 多张图拼成一张长图保存，方便检查
    if all_results:
        os.makedirs(os.path.dirname(args.save), exist_ok=True)
        width = max(img.shape[1] for img, _ in all_results)
        canvas = np.full((sum(img.shape[0] for img, _ in all_results), width, 3), 255, np.uint8)
        y = 0
        for image, results in all_results:
            drawn = annotate(image, results)
            canvas[y:y + drawn.shape[0], :drawn.shape[1]] = drawn
            y += drawn.shape[0]
        cv2.imwrite(args.save, canvas)
        print("\n标注图已保存到", args.save)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
