#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务四：印刷体 OCR。

图里是两行黑字：ABC 和 123，字体和我们做模板用的字体不完全一样。
OpenCV 没有现成的 OCR 引擎（cv2.text 需要额外编译 contrib + tesseract），
所以这里用最朴素也最能学到东西的办法：切字 + 模板匹配。

    python scripts/04_ocr_detect.py

流程：灰度 -> 高斯模糊 -> Otsu 二值化（黑字变白前景）-> 找外接矩形 ->
按行分组 -> 每个字缩放到 64x64 -> 和模板库算相关系数 -> 取最高分。

局限要提前说清楚：它只认识模板里有的字符，字体差异一大就掉分，
手写体基本没戏。板块三的手写识别要换 tesseract 或 PaddleOCR。
"""

import argparse
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")

DEFAULT_CHARS = "ABC123"
DEFAULT_FONTS = (
    cv2.FONT_HERSHEY_SIMPLEX,
    cv2.FONT_HERSHEY_DUPLEX,
    cv2.FONT_HERSHEY_TRIPLEX,
)
GLYPH_SIZE = 64


def load_gray(path):
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError("读不到图片：" + path)
    return image


def binarize(gray):
    """把黑字变成白前景、白底变成黑背景。

    先轻微模糊压掉噪点，再用 Otsu 自动找阈值。
    返回单通道 0/255 图，字是 255。
    """
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255,
                              cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary


def find_char_boxes(binary, min_height=20, min_area=200):
    """找出每个字符的外接矩形。

    返回 [(x, y, w, h), ...]，按从上到下、从左到右排好。
    面积太小的（噪点、标点）直接丢，太扁的（横线）也丢。
    """
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h < min_height or w * h < min_area:
            continue
        if w / float(h) > 2.5:          # 太扁，多半是线不是字
            continue
        boxes.append((x, y, w, h))
    return boxes


def normalize_glyph(glyph, size=GLYPH_SIZE):
    """把任意大小的字缩放到 size x size 的黑底白字图。

    长宽比要保住，缩放后居中摆放，四周补零。
    """
    if glyph.ndim == 3:
        glyph = cv2.cvtColor(glyph, cv2.COLOR_BGR2GRAY)

    rows, cols = np.where(glyph > 0)
    if len(rows) == 0:
        return np.zeros((size, size), np.uint8)

    glyph = glyph[rows.min():rows.max() + 1, cols.min():cols.max() + 1]
    height, width = glyph.shape
    scale = float(size - 8) / max(height, width)
    new_w = max(1, int(round(width * scale)))
    new_h = max(1, int(round(height * scale)))
    resized = cv2.resize(glyph, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((size, size), np.uint8)
    top = (size - new_h) // 2
    left = (size - new_w) // 2
    canvas[top:top + new_h, left:left + new_w] = resized
    return canvas


def build_template_bank(chars=DEFAULT_CHARS, fonts=DEFAULT_FONTS):
    """预先渲染模板，返回 {字符: [模板图, ...]}。

    同一个字用几种字体各画一张，字体差异大时还有得选。
    """
    bank = {}
    for char in chars:
        bank[char] = []
        for font in fonts:
            canvas = np.zeros((320, 260), np.uint8)
            cv2.putText(canvas, char, (40, 250), font, 4.0, 255, 8, cv2.LINE_AA)
            bank[char].append(normalize_glyph(canvas))
    return bank


def recognize_char(roi, bank):
    """认一个字，返回 (字符, 分数)。

    roi 是从二值图里抠出来的字（白字黑底）。
    分数用归一化相关系数，越接近 1 越像。
    """
    probe = normalize_glyph(roi)
    best_char, best_score = "?", -1.0
    for char, templates in bank.items():
        for template in templates:
            score = float(cv2.matchTemplate(probe, template,
                                            cv2.TM_CCOEFF_NORMED)[0][0])
            if score > best_score:
                best_char, best_score = char, score
    return best_char, best_score


def group_lines(chars):
    """把字符按行分组，返回 [[字符, ...], ...]。

    判断依据是竖直方向中心：两个字的中心差不到行高的一半，就算同一行。
    """
    if not chars:
        return []

    chars = sorted(chars, key=lambda item: item["box"][1])
    lines = []
    for item in chars:
        x, y, w, h = item["box"]
        cy = y + h / 2.0
        placed = False
        for line in lines:
            line_cy = np.mean([c["box"][1] + c["box"][3] / 2.0 for c in line])
            line_h = np.mean([c["box"][3] for c in line])
            if abs(cy - line_cy) < 0.6 * line_h:
                line.append(item)
                placed = True
                break
        if not placed:
            lines.append([item])

    for line in lines:
        line.sort(key=lambda item: item["box"][0])
    return lines


def read_text(gray, bank, min_score=0.45):
    """整条链路：二值化 -> 切字 -> 匹配 -> 分行。"""
    binary = binarize(gray)
    results = []
    for x, y, w, h in find_char_boxes(binary):
        label, score = recognize_char(binary[y:y + h, x:x + w], bank)
        if score < min_score:
            label = "?"
        results.append({"char": label, "box": (x, y, w, h), "score": score})

    # findContours 给的顺序不保证，按行列排一下，打印才好看
    results.sort(key=lambda item: (item["box"][1] // 40, item["box"][0]))
    return results, group_lines(results)


def annotate(gray, chars):
    canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for item in chars:
        x, y, w, h = item["box"]
        cv2.rectangle(canvas, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(canvas, item["char"], (x, max(y - 8, 16)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
    return canvas


def main():
    parser = argparse.ArgumentParser(description="印刷体 OCR")
    parser.add_argument("--image", default=os.path.join(ASSETS, "ocr_chars.png"))
    parser.add_argument("--save", default=os.path.join(OUTPUT, "ocr_result.png"))
    parser.add_argument("--min-score", type=float, default=0.45,
                        help="低于这个分数就当认不出来，输出问号")
    args = parser.parse_args()

    gray = load_gray(args.image)
    bank = build_template_bank()
    chars, lines = read_text(gray, bank, args.min_score)

    print("共切出 %d 个字符" % len(chars))
    print("%-4s %-16s %s" % ("字符", "位置(x,y,w,h)", "分数"))
    for item in chars:
        print("%-4s %-16s %.3f" % (item["char"], str(item["box"]), item["score"]))

    print("\n按行读取的结果：")
    for index, line in enumerate(lines):
        print("  第 %d 行：%s" % (index + 1, "".join(item["char"] for item in line)))

    os.makedirs(os.path.dirname(args.save), exist_ok=True)
    cv2.imwrite(args.save, annotate(gray, chars))
    print("\n标注图已保存到", args.save)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
