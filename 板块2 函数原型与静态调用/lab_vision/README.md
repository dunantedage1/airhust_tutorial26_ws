# 板块二 · 视觉基础：五个完形填空

## 这个板块想让你获得什么

五个脚本，每个都写了一半。函数名、参数、返回值、要做什么都给你了，函数体要你自己填。

素材不是网上扒的，是这个目录里 `tools/make_assets.py` 画出来的。想换颜色、换二维码内容、换标签 id，改那个脚本重跑一遍就行。

做完这五个，你应该对"一张图进来，一个结果出去"这条链路有肌肉记忆。视觉任务看起来花样很多，拆开都是预处理、找目标、做判断、输出坐标这几步。

## 环境：Python 3.8，这条没得商量

队里统一 3.8，理由有三个。

ROS Noetic 自带的就是 Python 3.8，板块三要把这些代码塞进 ROS 节点，版本不一致会很难受。

`opencv`、`numpy`、`ultralytics` 这三个东西在 3.8 上的版本组合我们试过，能跑。换到 3.9 或 3.10，pip 会给你拉一套新版本，numpy 2.x 和某些 opencv 版本不兼容，报错信息还特别难懂。

最后一个理由是省事。全队一个版本，谁跑不通，别人能直接复现。

### conda 和 pip 各管什么

conda 管 Python 解释器本身，顺便管一些带 C 库的包。pip 管纯 Python 包，从 PyPI 装。日常用法是：用 conda 建一个干净的 Python 3.8 环境，然后所有 Python 包都用 pip 装进去。

```bash
conda create -n airhust_vision python=3.8 -y
conda activate airhust_vision
pip install -r requirements.txt
```

装完验证一下，两个版本号都要打出来：

```bash
python -c "import cv2, numpy; print(cv2.__version__, numpy.__version__)"
```

国内网络慢的话加个源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

`requirements.txt` 里前四关只需要 `opencv-contrib-python` 和 `numpy`。`ultralytics` 会顺手把 torch 拉下来，几百 MB，第五关之前可以先注释掉，省点时间和硬盘。

### 几个真会踩的坑

`pip install` 装到了 base 环境。现象是 `conda activate` 之后 `pip list` 里没有你刚装的包，或者 `python` 路径不对。养成习惯，装之前先 `which python`，确认路径里有 `envs/airhust_vision`。

在 Ubuntu 上，pip 装的 opencv 和系统 apt 装的 `python3-opencv` 会打架。ROS 节点 `import cv2` 报 `undefined symbol`，多半是这个原因。所以识别代码一律放在 conda 环境里跑，不要在 ROS 的系统 Python 里 `pip install opencv`。板块三要用图像，我们会用 `cv_bridge` 转，不把 opencv 塞进系统环境。

`ultralytics` 第一次跑会往 `~/Library/Application Support` 或者 `~/.config/Ultralytics` 写配置，权限不对会警告，但不影响用。

## 目录

```
lab_vision/
├── README.md              你正在看的这个
├── requirements.txt       依赖
├── assets/                素材，脚本生成
│   ├── color_targets.png
│   ├── qr_harrypjh.png
│   ├── qr_dunantedage1.png
│   ├── apriltag_25h9_id1.png
│   └── ocr_chars.png
├── scripts/               五个任务
│   ├── 01_color_detect.py
│   ├── 02_qr_decode.py
│   ├── 03_apriltag_detect.py
│   ├── 04_ocr_detect.py
│   └── 05_yolo_detect.py
├── tools/make_assets.py   素材生成
├── output/                运行结果，不提交
└── weights/               放你自己的 best.pt
```

所有脚本都在 `lab_vision` 目录下运行，路径用相对路径就对了。

## 这套材料怎么用

五个脚本的结构是一样的：顶部常量、一组小函数、最后 `main()`。每个函数都有 docstring，写清楚输入是什么、输出是什么、要注意什么。函数体让你自己写，`main()` 已经写好了，里面的调用顺序就是数据流。

写完一个函数就跑一次，别五个都填完再一起跑。错了你分不清是哪一步的输入不对。

命令行参数不用改，怎么传都在 `main()` 里。

## 任务一：颜色识别

素材 `assets/color_targets.png`：白底，红绿蓝三个圆，另外有一个灰色方块和一个红色小点。

灰色方块是干扰，红色小点是噪点。结果应该是三个，多一个少一个都不对。

```bash
python scripts/01_color_detect.py
```

要实现的函数：

| 函数                               | 输入      | 输出                                           | 要点                      |
| -------------------------------- | ------- | -------------------------------------------- | ----------------------- |
| `color_masks(hsv)`               | HSV 图   | `{"red": mask, "green": mask, "blue": mask}` | 每种颜色一张 0/255 掩膜，红色要两段区间 |
| `find_blobs(mask, min_area)`     | 掩膜、最小面积 | `[(cx, cy, r, area), ...]`                   | 找轮廓，算外接圆，小于面积的丢掉        |
| `detect_colors(image, min_area)` | BGR 图   | 检测结果列表                                       | 串流程，不用改                 |
| `annotate(image, results)`       | 原图、结果   | 画好框的图                                        | 只影响好看程度                 |

几个提示。

OpenCV 读进来是 BGR，不是 RGB。画图的时候 `(255, 0, 0)` 是蓝色，别搞反了。

用 HSV 不用 RGB。RGB 三个通道都随光照变化，HSV 里色相 H 基本不受亮度影响，做颜色阈值稳得多。

红色的 H 在 0 附近，同时也在 180 附近，因为它跨了首尾。只写一段区间会漏掉一半的红色。

形态学开运算能去掉毛刺，闭运算能补小洞。这一步不做也能跑，做了结果更干净。

`min_area` 用 500。小红点面积只有一百多，会被过滤掉；三个圆的面积在一万一左右。

预期输出：

```
共检测到 3 个色块
red    (120, 170)   60       11390
green  (320, 170)   60       11414
blue   (520, 170)   60       11414
```

重点在 `color_masks` 和 `find_blobs`。阈值怎么定，基本都在这两个函数里。

常见错误：直接把 RGB 阈值抄进来；忘了红色要两段；`min_area` 设成 0，噪点全进来了。

## 任务二：二维码识别

素材两张，分别编码了 `harrypjh` 和 `dunantedage1`。

```bash
python scripts/02_qr_decode.py
```

要实现的函数：

| 函数                         | 输入    | 输出                                         | 要点                |
| -------------------------- | ----- | ------------------------------------------ | ----------------- |
| `decode_qr(image)`         | BGR 图 | `[{"text": str, "points": (4,2) 数组}, ...]` | 转灰度，先试多码接口，不行退回单码 |
| `annotate(image, results)` | 原图、结果 | 画了框的图                                      | 四个角连起来，文字标在左上角    |

先记住这几点。

OpenCV 自带 `QRCodeDetector`，不需要 zbar，也不需要装新东西。做 ROS 的时候少一个依赖就少一堆麻烦。

喂灰度图。彩色图也能过，但没必要多算一遍。

`detectAndDecodeMulti` 是 4.3 之后才有的接口，一张图里多个码时用它。单个码用 `detectAndDecode` 也一样。两个都写，兼容性好一点。

返回的 `points` 是四个角，顺序是左上、右上、右下、左下。画图的时候按这个顺序连，不然框会打结。

预期输出：

```
图片 qr_harrypjh.png
  内容：harrypjh
  中心：(132, 132)

图片 qr_dunantedage1.png
  内容：dunantedage1
  中心：(132, 132)
```

`decode_qr` 把读图、转灰度、调接口、整理返回值串在一起，是这一关唯一需要自己组织的函数。

常见错误：把图片的白边裁掉了。二维码四周的白边（quiet zone）是编码的一部分，裁掉就解不出来。我们的素材留了 4 个模块宽的白边。

## 任务三：AprilTag 识别

素材一张，25h9 家族，编号 1。

```bash
python scripts/03_apriltag_detect.py
```

要实现的函数：

| 函数                                         | 输入       | 输出                                                    | 要点                                          |
| ------------------------------------------ | -------- | ----------------------------------------------------- | ------------------------------------------- |
| `make_detector(family)`                    | 家族名      | `(dictionary, detector)`                              | 家族选错就一个都测不到，老版本 OpenCV 没有 `ArucoDetector` 类 |
| `detect_tags(image, dictionary, detector)` | 图、字典、检测器 | `[{"id": int, "center": (x,y), "corners": ...}, ...]` | 转灰度，检测，把 id 和角点取出来                          |
| `annotate(image, results)`                 | 原图、结果    | 画了框的图                                                 | 四角连线，中心打个点，标 id                             |

几个容易搞错的地方。

25h9 的意思是内部 5×5 个格子，一共 25 个 bit，其中 9 个是校验位。16h5 是 4×4，36h11 是 6×6。家族就是个字典，生成和检测必须用同一个。

AprilTag 比二维码抗遮挡，而且角点稳定，算相对位姿很方便。无人机降落、对接这类任务基本都用它。

`corners` 的顺序也是左上、右上、右下、左下。想算位姿的话，这个顺序不能乱。

预期输出：

```
家族 25h9，检测到 1 个标签
  id=1  中心=(239.5, 239.5)
  四角：[[ 40.,  40.],
 [439.,  40.],
 [439., 439.],
 [ 40., 439.]]
```

`make_detector` 和 `detect_tags` 要你自己接 OpenCV 的 aruco 接口。家族选错的话，这里会卡很久。

常见错误：生成用的 16h5，检测用的 25h9，结果永远是"检测到 0 个"；白边被裁掉；把图片转成了 RGB 再传进去。

## 任务四：印刷体 OCR

素材是两行黑字，第一行 ABC，第二行 123。字体的选择和模板库里的不完全一样，这是故意的。

```bash
python scripts/04_ocr_detect.py
```

OpenCV 没有现成的 OCR 引擎。`cv2.text` 需要编译 contrib 并且装 tesseract，我们这套环境里没有。所以这里用最朴素的办法：二值化、切字、把每个字缩到一样大、和模板算相关系数。

要实现的函数：

| 函数                                  | 输入      | 输出                    | 要点                         |
| ----------------------------------- | ------- | --------------------- | -------------------------- |
| `binarize(gray)`                    | 灰度图     | 黑底白字的二值图              | 高斯模糊，Otsu，注意是 `BINARY_INV` |
| `find_char_boxes(binary)`           | 二值图     | `[(x, y, w, h), ...]` | 找外接矩形，按高度和面积过滤             |
| `normalize_glyph(glyph, size)`      | 单个字的图   | `size×size` 的黑底白字     | 保住长宽比，居中，四周补零              |
| `recognize_char(roi, bank)`         | 字的图、模板库 | `(字符, 分数)`            | 逐模板 `matchTemplate`，取最高分   |
| `group_lines(chars)`                | 字符列表    | 按行分好组的二维列表            | 竖直中心差小于半个行高就算同一行           |
| `build_template_bank(chars, fonts)` | 字符集、字体  | `{字符: [模板...]}`       | 每种字体画一张，扩大覆盖面              |
| `read_text(gray, bank, min_score)`  | 灰度图、模板库 | `(字符列表, 行列表)`         | 串流程                        |

这一关的细节比前几关多。

`THRESH_BINARY_INV` 是为了让字变成白色前景、背景变黑。找轮廓默认找的是白色区域，前景背景搞反了，`findContours` 找到的就是背景。

归一化必须保住长宽比，否则 A 和 1 会被拉成一样宽，匹配分数全乱。

模板库用三种字体（SIMPLEX、DUPLEX、TRIPLEX）各画一遍，测试图用的是 DUPLEX。这算是最低限度的"泛化"，比拿同一张图和自己比强。

`matchTemplate` 用 `TM_CCOEFF_NORMED`，结果在 -1 到 1 之间，越接近 1 越像。分数低于 `min_score` 输出问号，比硬猜一个字符诚实。

预期输出：

```
共切出 6 个字符
A    (71, 76, 66, 64) 0.972
B    (286, 76, 57, 64) 0.993
C    (494, 75, 59, 66) 0.981
1    (75, 256, 54, 64) 0.960
2    (284, 254, 55, 66) 0.990
3    (493, 256, 56, 65) 0.979

按行读取的结果：
  第 1 行：ABC
  第 2 行：123
```

`binarize`、`normalize_glyph`、`recognize_char` 三个是重点。`read_text` 是主流程，看不懂某个函数的输入时回去看它。

说清楚局限。这套东西只认识模板里有的字符，字体差别一大就掉分，手写体基本没戏。板块三第四关会专门考手写识别，到那时候 tesseract 的处理能力也不够，得上 PaddleOCR。这里先用模板匹配，是想让你明白 OCR 的底层在干什么，不是让你觉得模板匹配能包打天下。

常见错误：二值化没反向，切出来全是背景；忘了模糊，边缘毛刺被切成两个字；归一化的时候直接 `resize` 到正方形，长宽比丢了。

## 任务五：YOLO 检测框架

这一关没有素材，也没有模型。图片和 `best.pt` 要你自己补：

- `assets/yolo_test.jpg`：一张待检测的图
- `weights/best.pt`：你训练出来的权重

仓库的 `.gitignore` 默认不跟踪 `.pt`，模型大了会被 GitHub 拒收。要提交的话用 Git LFS，或者把权重放到 release 里给个下载链接。

```bash
python scripts/05_yolo_detect.py --weights weights/best.pt --source assets/yolo_test.jpg
```

要实现的函数：

| 函数                                        | 输入       | 输出        | 要点                                 |
| ----------------------------------------- | -------- | --------- | ---------------------------------- |
| `load_model(weights)`                     | 权重路径或模型名 | `YOLO` 对象 | 本地路径要先判断文件在不在                      |
| `detect_objects(model, image, conf, iou)` | 模型、图、阈值  | 检测结果列表    | 取 `boxes.xyxy`、`cls`、`conf`，算归一化中心 |
| `annotate(image, detections)`             | 原图、结果    | 画了框的图     | 框加类别和置信度                           |

几个注意点。

`ultralytics` 的 `predict` 返回的是结果对象列表，取第一个，里面 `boxes` 是检测框。`boxes.xyxy` 是左上右下像素坐标，`boxes.cls` 是类别编号，`boxes.conf` 是置信度。

归一化中心点 = `(x1+x2)/2/宽`，`(y1+y2)/2/高`。板块三要用这个值算像素误差，再转成速度指令，所以第 5 关的代码里可以先把它算出来打印着看。

先别用 `best.pt` 调试。拿官方小模型验证链路：

```bash
python scripts/05_yolo_detect.py --weights yolo11n.pt --source assets/color_targets.png
```

会下载一个 6MB 的模型，然后在色块图上检测出三个 `frisbee`（COCO 里没有圆这个类别，它只能瞎猜）。能出框、能打印，说明环境是对的。换成你自己的模型才能认你自己训练的目标。

预期输出（用官方模型跑色块图）：

```
检测到 3 个目标
frisbee      0.60   (58, 109, 181, 232)          (0.187, 0.356)
...
```

`detect_objects` 是这一关唯一需要动脑的地方。它把 ultralytics 的返回值翻译成自己的格式。

常见错误：`weights` 路径写成了相对路径但工作目录不对；图片是 `BGR` 却手动转成 `RGB` 再传（ultralytics 接受 numpy 的 BGR，别多此一举）；把 `conf` 设成 0.01，框会多到看不清。

不要在这一关训练模型。板块三第五关会带你走一遍数据增强和训练，那才是训练的地方。这里只做推理。

## 自检清单

五个任务都能跑出上面那些输出，就算过了。除此之外，你应该能不查资料回答这几个问题：

为什么颜色阈值用 HSV 不用 RGB？二维码和 AprilTag 各自适合什么场景？模板匹配的 OCR 为什么怕换字体？YOLO 的框为什么最好转成归一化坐标？

答不上来就回头看代码，别急着进板块三。板块三不会给你任何识别代码，只会给你一个空节点，你要把这里写过的东西搬进去，再套上 ROS 的收发。

## 下一步

板块三开始接仿真。起飞、定点、下视拍照、识别、降落，五个单元测试，每一关都要自己写 ROS 相关的代码。板块二里的函数可以复制粘贴，但 `rospy` 那部分没人替你写。
