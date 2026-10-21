#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""任务三：AprilTag 识别。

assets 里有一张 25h9 家族、编号为 1 的标签。
25h9 表示内部是 5x5 个格子，其中 9 个 bit 校验。
它比二维码耐遮挡、算位姿方便，无人机降落和对接常用这个。

    python scripts/03_apriltag_detect.py
    python scripts/03_apriltag_detect.py --image assets/apriltag_25h9_id1.png --family 25h9

注意：家族选错了就一个都检测不到，这是最常见的坑。
"""

import argparse
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, "assets")
OUTPUT = os.path.join(ROOT, "output")

FAMILIES = {
    "16h5": cv2.aruco.DICT_APRILTAG_16H5,
    "25h9": cv2.aruco.DICT_APRILTAG_25H9,
    "36h11": cv2.aruco.DICT_APRILTAG_36H11,
}


def load_image(path):
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError("读不到图片：" + path)
    return image


def make_detector(family="25h9"):
    """按家族建检测器。

    返回 (dictionary, detector)。OpenCV 4.7 以前没有 ArucoDetector 类，
    这时 detector 给 None，后面用老接口。
    """
    if family not in FAMILIES:
        raise ValueError("不支持的家族 %s，可选 %s" % (family, list(FAMILIES)))

    dictionary = cv2.aruco.getPredefinedDictionary(FAMILIES[family])
    if hasattr(cv2.aruco, "ArucoDetector"):
        parameters = cv2.aruco.DetectorParameters()
        return dictionary, cv2.aruco.ArucoDetector(dictionary, parameters)
    return dictionary, None


def detect_tags(image, dictionary, detector):
    """检测图里所有标签。

    返回 [{"id": int, "center": (cx, cy), "corners": np.ndarray(4, 2)}, ...]，
    corners 的顺序是左上、右上、右下、左下。
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if detector is None:
        corners, ids, _ = cv2.aruco.detectMarkers(gray, dictionary)
    else:
        corners, ids, _ = detector.detectMarkers(gray)

    results = []
    if ids is None:
        return results

    for marker_corners, marker_id in zip(corners, ids.flatten()):
        points = np.array(marker_corners, dtype=np.float32).reshape(4, 2)
        cx, cy = points.mean(axis=0)
        results.append({
            "id": int(marker_id),
            "center": (float(cx), float(cy)),
            "corners": points,
        })
    results.sort(key=lambda item: item["id"])
    return results


def annotate(image, results):
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


def main():
    parser = argparse.ArgumentParser(description="AprilTag 识别")
    parser.add_argument("--image", default=os.path.join(ASSETS, "apriltag_25h9_id1.png"))
    parser.add_argument("--family", default="25h9", choices=list(FAMILIES),
                        help="标签家族，和生成时保持一致")
    parser.add_argument("--save", default=os.path.join(OUTPUT, "apriltag_result.png"))
    args = parser.parse_args()

    image = load_image(args.image)
    dictionary, detector = make_detector(args.family)
    results = detect_tags(image, dictionary, detector)

    print("家族 %s，检测到 %d 个标签" % (args.family, len(results)))
    for item in results:
        cx, cy = item["center"]
        print("  id=%d  中心=(%.1f, %.1f)" % (item["id"], cx, cy))
        print("  四角：%s" % np.array2string(item["corners"], precision=1,
                                            separator=", ", suppress_small=True))

    if not results:
        print("  检查两件事：家族对不对；图里的白边（quiet zone）有没有被裁掉")

    os.makedirs(os.path.dirname(args.save), exist_ok=True)
    cv2.imwrite(args.save, annotate(image, results))
    print("标注图已保存到", args.save)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
