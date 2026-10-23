#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务四：印刷体 OCR。

图里是两行黑字：ABC 和 123。这一关不自己写识别算法，直接调 Tesseract。

Tesseract 是独立的 OCR 引擎，pytesseract 是它的 Python 封装，两个都要装：

环境准备：

    sudo apt install tesseract-ocr && pip install pytesseract

装完用 `tesseract --version` 确认能打印版本号。

运行方式：

    cd lab_vision
    python scripts/04_ocr_detect.py

思路：灰度 -> 放大 -> 模糊 -> Otsu 二值化 -> pytesseract.image_to_string。
tesseract 喜欢黑字白底、字大一点、对比度清楚的图。
"""

import os

import cv2
import pytesseract

"""这个部分在找目录"""
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")

IMAGE_PATH = os.path.join(ASSETS, "ocr_chars.png")
SAVE_PATH = os.path.join(OUTPUT, "ocr_preprocessed.png")
LANG = "eng"
PSM = 6
SCALE = 2.0

os.makedirs(OUTPUT, exist_ok=True)


def load_image(path):
    """按灰度读图，读不到就抛错。"""
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError("读不到图片：" + path)
    return image


def preprocess(gray):
    """把图处理成 tesseract 喜欢的样子。

    放大让字占更多像素，模糊压掉噪点，Otsu 找出黑白分界。
    """
    resized = cv2.resize(gray, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_CUBIC)
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def read_text(image):
    """调 tesseract 读出图里的文字，返回字符串。

    image 最好是预处理过的灰度图或二值图。
    --psm 6 表示整张图当成一块文本，适合这种几行字的图。
    """
    config = "--psm %d" % PSM
    text = ""
    """ ————————————————————————————填空—————————————————————————————————

                这里只要填一行，cv简单吧孩子，和我一起，成为调包侠吧

        ————————————————————————————填空————————————————————————————————— """
    return text


try:
    pytesseract.get_tesseract_version()
except pytesseract.TesseractNotFoundError:
    raise SystemExit("找不到 tesseract。请先安装：sudo apt install tesseract-ocr")

gray = load_image(IMAGE_PATH)
processed = preprocess(gray)
text = read_text(processed)

print("识别结果：")
print(text.strip())

lines = [line.strip() for line in text.splitlines() if line.strip()]
print("\n按行整理：")
for index, line in enumerate(lines):
    print("  第 %d 行：%s" % (index + 1, line))

cv2.imwrite(SAVE_PATH, processed)
print("\n预处理图已保存到", SAVE_PATH)
