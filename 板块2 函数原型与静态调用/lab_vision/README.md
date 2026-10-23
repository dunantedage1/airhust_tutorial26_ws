# 板块二 · 视觉基础：五个完形填空

## 这个板块想让你获得什么

2026级的新生们各位好啊，恭喜你进入了第二个板块，在这个板块里面，/scripts 目录下面有五个脚本，对应了无人机在实际任务中的五种视觉任务，分别是颜色识别，二维码解码，apriltag解码，ocr检测，yolo检测

这五份代码都是缺失的，需要你自学一些计算机视觉相关的东西进行填空

/assets 目录下面有若干张图片，那是五份代码的数据集，你检测的素材都在这里面

填完这五个空，你就应该对基础的计算机视觉有基本了解了

## 环境：Python 3.8

无人机ros开发中，视觉节点基本上都是通过python编写的

队里统一python的版本是3.8

原因是ROS Noetic 自带的就是 Python 3.8，板块三要把这些代码塞进 ROS 节点。

### conda 和 pip 是什么，各管什么

conda是一个python环境管理器，它能很便捷的让你切换到各种不同python虚拟环境。

pip是一个python包管理器，它能让你便捷地从远程下载或卸载特定版本的python库，而且能够便捷的导入这些库

日常用法是：用 conda 建一个干净的 Python 3.8 环境，然后用pip把python包都装进去

下面需要你们通过cd命令进入lab\_vision目录，然后创建一个conda环境，然后在这个conda环境里面下载requirement.txt里面的包（你可以把pip包理解为python的模组，requirement.txt理解为一个整合包）

```bash
cd lab_vision
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

`requirements.txt` 里前三关只需要 `opencv-contrib-python` 和 `numpy`。第四关的 `pytesseract` 也在里面，但它还要求系统里先装 `tesseract` 可执行文件，安装方法见任务四。`ultralytics` 会顺手把 torch 拉下来，几百 MB，还是蛮大的，需要点时间

# 这个lab\_vision的目录

```
lab_vision/
├── README.md              你正在看的这个
├── requirements.txt       依赖
├── assets/                素材
│   ├── color_targets.png
│   ├── qr_1.png
│   ├── qr_2.png
│   ├── apriltag_25h9.png
│   └── ocr_chars.png
├── scripts/               五个任务
│   ├── 01_color_detect.py
│   ├── 02_qr_decode.py
│   ├── 03_apriltag_detect.py
│   ├── 04_ocr_detect.py
│   └── 05_yolo_detect.py
├── output/                运行结果（自己跑出来的）
└── models/                训练好的 best.pt
```

注：所有脚本都在 `lab_vision` 目录下运行

## 这套材料怎么用

你需要在五个脚本挖空的地方填入正确的程序段

五个脚本的结构一样：文件开头是常量（路径、阈值、开关），中间一组小函数，最后是主流程。

你在填写的过程中肯定会遇到各种问题，如果你不了解一些pip包的常用函数，你可以翻到文末的《每关可能用到的函数》，按你做到的那一关找签名和用法

## 任务一：颜色识别

在这一关里，你需要实现颜色识别的功能，这是一个在无人机比赛中非常常见的场景，一般在最后精准降落的时候会用到，你需要识别目标颜色的圆，然后降落在对应的颜色圆内。

本关素材 `assets/color_targets.png` 是白底，红绿蓝三个圆，另外有一个灰色方块和一个红色小点。

你需要编写python代码，实现颜色识别的功能。

这一关要用到的函数，文末[第一关可能要用到的函数](#第一关可能要用到的函数)里都列出来了。

灰色方块是干扰，红色小点是噪点。最终结果应该是三个圆，每个圆有一个中心坐标和半径。

### 小课堂

各位都知道，图片是由像素点组成的，每个像素点都有一个 RGB 值

在8bit色深图像中，每个像素点的 R，G，B 值都是一个0-255的整数，分别表示红、绿、蓝三通道的强度。

每一个像素点都是一个3维的向量，分别表示红、绿、蓝三通道的强度。

而我们依据这个3维向量的数值，就能判断对应像素点的颜色。

你已经知道了颜色识别的基本流程了，下面开始任务吧，祝你好运

注：RGB是人类的视觉系统，opencv中其实用的是BGR。

```bash
python scripts/01_color_detect.py
```

要实现的函数：

| 函数                                    | 输入                  | 输出                              | 要点                         |
| ------------------------------------- | ------------------- | ------------------------------- | -------------------------- |
| `color_mask(image, lower, upper)`     | BGR 图、BGR 下界、BGR 上界 | 0/255 单通道掩膜                     | 用 `cv2.inRange` 直接卡 BGR 范围 |
| `find_blobs(mask, min_area=MIN_AREA)` | 掩膜、最小面积             | `[(cx, cy, radius, area), ...]` | 找轮廓、算外接圆，小于面积的丢掉           |
| `annotate(image, results)`            | 原图、结果               | 画好框的图                           | 只影响好看程度，代码已给出              |

预期输出：

```
共检测到 3 个色块
red    (120, 170)   60       11342
green  (320, 170)   60       11342
blue   (520, 170)   60       11342
```

常见错误：BGR 顺序写反，把 R 和 B 搞混；`min_area` 设成 0，导致识别到噪点；忘了红色小点要靠面积过滤。

## 任务二：二维码识别

在这一关里，你需要实现二维码识别的功能，这是一个在无人机比赛中非常常见的场景，一般会让你在二维码中提取一些信息，从而指导无人机的行动。

本关素材 `assets/qr_1.png`和`assets/qr_2.png`是二维码图片，分别编码了一个神秘字符串。

你需要编写python代码，实现二维码识别的功能。

这一关要用到的函数，文末[第二关可能要用到的函数](#第二关可能要用到的函数)里都列出来了。

最终你应该从两个二维码中解码出两个字符串

### 小课堂

从这一关开始，你后面编写的代码会越来越让你像一个“调包侠”

这是无可避免的，cv界已经发展了数十年了，已经有了非常多的工程化函数

欧阳由老师曾经和我们说过要有工程师思维

工程师思维就是：“够用就行”

所以各位不必太拘泥于“这代码都不是我自己写出来的！”

只需关注有没有实现功能即可

如果感兴趣，你可以自己去opencv的文档中查找解码器的实现细节

<br />

```bash
python scripts/02_qr_decode.py
```

要实现的函数：

| 函数                         | 输入    | 输出                                         | 要点             |
| -------------------------- | ----- | ------------------------------------------ | -------------- |
| `decode_qr(image)`         | BGR 图 | `[{"text": str, "points": (4,2) 数组}, ...]` | 转灰度            |
| `annotate(image, results)` | 原图、结果 | 画了框的图                                      | 四个角连起来，文字标在左上角 |

预期输出：

```
图片 qr_1.png
  内容：harrypjh
  中心：(132, 132)

图片 qr_2.png
  内容：dunantedage1
  中心：(132, 132)
```

常见错误：把图片的白边裁掉了。二维码四周的白边（quiet zone）是编码的一部分，裁掉就解不出来。我们的素材留了 4 个模块宽的白边。

## 任务三：AprilTag 识别

在这一关里，你需要实现 AprilTag 识别的功能。这个在无人机比赛里较为常见，一般和二维码的功能差不多，有一些比赛可能会拿它来定位无人机的位置。

本关素材 `assets/apriltag_25h9.png` 是一张 25h9 家族的标签，你需要把它的编号读出来。

你需要编写python代码，实现 AprilTag 识别的功能。

最终你应该得到标签的编号，以及它在图像里的中心和四个角点。

### 小课堂

AprilTag 你可以理解成一种专门给机器看的二维码。

它也是黑白格子，但格子排布和校验方式跟二维码不一样。

好处是离得远、有点斜、被挡住一点点的时候也能认出来，而且四个角点的位置比较准，方便算相对位姿。

25h9 是家族名，意思是内部 5×5 个格子，一共 25 个 bit，其中 9 个是校验位。除了 25h9，常见的还有 16h5（4×4）和 36h11（6×6）。

我们的标签是 5×5 的，所以这一关用 25h9。

<br />

```bash
python scripts/03_apriltag_detect.py
```

要实现的函数：

| 函数                                         | 输入       | 输出                                                    | 要点                                          |
| ------------------------------------------ | -------- | ----------------------------------------------------- | ------------------------------------------- |
| `make_detector(family)`                    | 家族名      | `(dictionary, detector)`                              | 家族选错就一个都测不到，老版本 OpenCV 没有 `ArucoDetector` 类 |
| `detect_tags(image, dictionary, detector)` | 图、字典、检测器 | `[{"id": int, "center": (x,y), "corners": ...}, ...]` | 转灰度，检测，把 id 和角点取出来                          |
| `annotate(image, results)`                 | 原图、结果    | 画了框的图                                                 | 四角连线，中心打个点，标 id                             |

<br />

预期输出：

```
家族 25h9，检测到 1 个标签
  id=1  中心=(239.5, 239.5)
  四角：[[ 40.,  40.],
 [439.,  40.],
 [439., 439.],
 [ 40., 439.]]
```

`make_detector` 和 `detect_tags` 要你自己接 OpenCV 的 aruco 接口。卡住了就看文末[第三关可能要用到的函数](#第三关可能要用到的函数)，签名和返回结构都在里面。

常见错误：家族选错；把标签四周的白边裁掉；把图片转成 RGB 再传进去；没检测到的时候直接取 `ids[0]`，报 `NoneType` 的错。

## 任务四：印刷体 OCR

在这一关里，你需要实现 OCR 的功能，也就是把图片里的字读出来。无人机比赛里一般用来看地面上的数字、字母或者手写标记。

本关素材 `assets/ocr_chars.png` 是两行黑字，第一行 ABC，第二行 123。

你需要编写python代码，把这两行字识别出来。

这一关要用到的函数，文末[第四关可能要用到的函数](#第四关可能要用到的函数)里都列出来了。

最终你应该得到两行字符串。

### 小课堂

OCR 全称是 Optical Character Recognition，光学字符识别。听起来挺唬人，其实你天天在用：手机拍文档转文字、截图提取文字，背后都是这玩意。

这一关我们不自己写识别算法，直接调 tesseract。它是老牌的 OCR 引擎，印刷体识别得很稳，Python 里用 `pytesseract` 这个包调它。

有同学可能会问，那我自己写行不行？行，但没必要。OCR 背后是几十年的工程积累，你自己写一个能认印刷体的，工作量够你把板块三做完两遍。还是那句话，够用就行。

不过调包也有调包的讲究。tesseract 对输入有要求：字要大一点、对比度清楚一点、最好是黑字白底。所以我们要先做一轮预处理，再把图喂给它。

<br />

先装东西。tesseract 是系统里的程序，pytesseract 是 Python 的封装，两个都要装：

```bash
sudo apt install tesseract-ocr
pip install pytesseract
```

装完确认一下：

```bash
tesseract --version
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

第一条打出版本号、第二条打出同一个版本号，就说明装对了。`tesseract-ocr` 这个包只带英文（`eng`）和方向检测（`osd`）语言包，这一关够用。要识别中文得另装 `chi_sim` 语言包：`sudo apt install tesseract-ocr-chi-sim`。

```bash
python scripts/04_ocr_detect.py
```

要实现的函数：

| 函数                 | 输入    | 输出    | 要点                                                     |
| ------------------ | ----- | ----- | ------------------------------------------------------ |
| `load_image(path)` | 路径    | 灰度图   | 用 `cv2.IMREAD_GRAYSCALE` 读                             |
| `preprocess(gray)` | 灰度图   | 处理后的图 | 放大、模糊、Otsu 二值化；tesseract 对字太小、对比度低的图不友好                |
| `read_text(image)` | 处理后的图 | 字符串   | `pytesseract.image_to_string`，`lang` 和 `config` 两个参数别漏 |

<br />

实际上，预处理不是必须的，同一张图不处理也可能读对。但放大加二值化之后更稳，字占画面比例小的时候差别明显。跑完把 `output/ocr_preprocessed.png` 打开看看，能明白 tesseract 到底看到了什么。

预期输出：

```
识别结果：
ABC
123

按行整理：
  第 1 行：ABC
  第 2 行：123
```

`preprocess` 我已经写好了，`read_text` 是空的，你只要把里面那一行补上。想多探究一点，就改改放大倍数、模糊核、二值化方式，看看输出怎么变。

常见错误：`tesseract` 没装或者不在 `PATH` 里，报 `TesseractNotFoundError`；二值化用了 `INV`；`psm` 没设，读出空串；图片路径写错，`imread` 返回 `None`。

## 任务五：YOLO 检测框架

在这一关里，你需要实现目标检测的功能。前四关都是“识别特定的东西“，这一关之后，无论什么东西，只要你会训练一个神经网络，就可以检测出来。

模型我已经训好了，识别的是大家都喜欢的奶龙：

- `models/best.pt`：训练好的权重，直接用
- `assets/nailong.jpg`：目标原图，也是默认的测试图

这一关要用到的函数，文末[第五关可能要用到的函数](#第五关可能要用到的函数)里都列出来了。

在这一关里，你只需要体验一下yolo的识别功能，具体如何训练模型，你会在板块三中学习。至于yolo的内部机制，你可学可不学，这个东西牵扯到了太多的内容。

包括：机器学习、深度学习、卷积神经网络、pytorch框架等等等等

### 小课堂

YOLO 是 You Only Look Once 的缩写，一个目标检测的卷积神经网络模型。在无人机的应用中，你不需要知道它内部怎么卷积、怎么回归，只需要知道它的输入是一张图片，输出是一个框，一个类别和一个置信度

置信度可以理解成“模型有多确定这个框里是奶龙”，取值 0 到 1。0.45 的意思就是，模型觉得有 45% 以上的把握，才算一次有效检测。阈值调低，框会变多，误检也多；调高，漏检会变多。这个数没有绝对标准，看你的任务能容忍多少误检。

<br />

```bash
python scripts/05_yolo_detect.py
```

脚本开头的 `WEIGHTS` 和 `SOURCE` 已经指向上面两个文件。想用自己的图测，改 `SOURCE` 就行。

要实现的函数：

| 函数                                        | 输入       | 输出        | 要点                                 |
| ----------------------------------------- | -------- | --------- | ---------------------------------- |
| `load_model(weights)`                     | 权重路径或模型名 | `YOLO` 对象 | 本地路径要先判断文件在不在                      |
| `detect_objects(model, image, conf, iou)` | 模型、图、阈值  | 检测结果列表    | 取 `boxes.xyxy`、`cls`、`conf`，算归一化中心 |
| `annotate(image, detections)`             | 原图、结果    | 画了框的图     | 框加类别和置信度                           |

`ultralytics` 的 `predict` 返回的是结果对象列表，取第一个，里面 `boxes` 是检测框。`boxes.xyxy` 是左上右下像素坐标，`boxes.cls` 是类别编号，`boxes.conf` 是置信度。

归一化中心点 = `(x1+x2)/2/宽`，`(y1+y2)/2/高`。板块三要用这个值算像素误差，再转成速度指令，所以这一关的代码里可以先把它算出来打印着看。

预期输出（默认，跑奶龙）：

```
检测到 1 个目标
nailong      0.74   (56, 44, 1266, 1508)         (0.522, 0.515)
```

`detect_objects` 是这一关唯一需要动脑的地方。它把 ultralytics 的返回值翻译成自己的格式。

常见错误：`models/best.pt` 路径写错；图片是 `BGR` 却手动转成 `RGB` 再传（ultralytics 接受 numpy 的 BGR，不用多此一举）；把 `conf` 设成 0.01，框会多到看不清。

不要在这一关重新训练模型。板块三第五关会带你走一遍数据增强和训练，那才是训练的地方。这里只做推理。

## 附录：每关可能用到的函数

在这个附录里面，有你们可能用得到的函数，如果对无人机常用python库不熟悉，可以看看

签名里的 `[]` 表示这个参数可以省，`->` 后面是返回值。Python 里图像都是 numpy 数组（`np.ndarray`），彩色的默认 BGR，形状是 `(高, 宽, 通道)`。

有两点提醒：

- 坐标是 `(x, y)`，x 是列、y 是行；取像素要写 `img[y, x]`，别写反。
- 画图、阈值、掩膜这些操作都要求数据类型是 `uint8`，范围 0 到 255。

### 第一关可能要用到的函数

这一关是颜色识别，用到的都是最基础的东西：读图、卡颜色范围、形态学、找轮廓、画图。

#### 读图和存图

| 调用                                 | 怎么用                                                |
| ---------------------------------- | -------------------------------------------------- |
| `cv2.imread(path[, flags]) -> img` | 读图。`flags` 一般不用填，默认读成三通道 BGR。读不到返回 `None`。         |
| `cv2.imwrite(path, img) -> bool`   | 存图。路径里的目录要存在，脚本开头已经用 `os.makedirs` 建好 `output/` 了。 |

#### 颜色阈值

| 调用                                         | 怎么用                                               |
| ------------------------------------------ | ------------------------------------------------- |
| `cv2.inRange(src, lowerb, upperb) -> mask` | 把落在 `[lowerb, upperb]` 里的像素置 255，其余置 0，返回一张单通道掩膜。 |

BGR 顺序是蓝、绿、红。红色是 R 高、G/B 低，绿色是 G 高，蓝色是 B 高。三个通道分别限制，就能把对应颜色抠出来。

#### 形态学：kernel、开运算、闭运算

<br />

`cv2.getStructuringElement(shape, ksize[, anchor]) -> kernel`

生成结构元素，也就是卷积核。`shape` 取 `cv2.MORPH_RECT`（矩形）、`cv2.MORPH_ELLIPSE`（椭圆）、`cv2.MORPH_CROSS`（十字）。`ksize` 是 `(宽, 高)`，给 3、5、7 这种奇数。处理圆形的色块用椭圆核，边缘不会变成方块。

<br />

`cv2.morphologyEx(src, op, kernel[, iterations]) -> dst` 

这个函数把腐蚀和膨胀组合好了，一般就用这个。`op` 的取值：

| op                   | 效果     | 什么时候用           |
| -------------------- | ------ | --------------- |
| `cv2.MORPH_OPEN`     | 先腐蚀后膨胀 | 去掉孤立的小噪点、毛刺     |
| `cv2.MORPH_CLOSE`    | 先膨胀后腐蚀 | 补上目标内部的小洞、断开的地方 |
| `cv2.MORPH_GRADIENT` | 膨胀减腐蚀  | 取轮廓边缘           |
| `cv2.MORPH_TOPHAT`   | 原图减开运算 | 抠出比背景亮的小块       |
| `cv2.MORPH_BLACKHAT` | 闭运算减原图 | 抠出比背景暗的小块       |

`iterations` 是重复次数，默认 1。核越大、次数越多，效果越强，5×5 做一次通常够用。

想单独用腐蚀或者膨胀也行：`cv2.erode(src, kernel[, iterations])` 让白色区域变瘦，`cv2.dilate(src, kernel[, iterations])` 让白色区域变胖。

#### 找轮廓、算几何量、筛选

`cv2.findContours(image, mode, method) -> contours, hierarchy`

输入必须是单通道二值图，白色是要找的前景。`mode` 决定层级关系：

| mode                | 含义              |
| ------------------- | --------------- |
| `cv2.RETR_EXTERNAL` | 只要最外层轮廓，色块检测用这个 |
| `cv2.RETR_LIST`     | 所有轮廓，不建层级       |
| `cv2.RETR_TREE`     | 所有轮廓，建完整层级      |

`method` 决定轮廓点怎么存：`cv2.CHAIN_APPROX_SIMPLE` 只存拐点，省内存；`cv2.CHAIN_APPROX_NONE` 存每一个点。

OpenCV 4.x 返回两个值，3.x 返回三个（多一个 `image`）。网上老教程写 `_, contours, _ = cv2.findContours(...)`，在这套环境里会报解包错误。

拿到轮廓之后，用这两个函数：

| 调用                                                  | 返回     | 怎么用                |
| --------------------------------------------------- | ------ | ------------------ |
| `cv2.contourArea(cnt) -> area`                      | 面积，浮点数 | 轮廓围起来的像素面积，按它筛掉小噪点 |
| `cv2.minEnclosingCircle(cnt) -> ((cx, cy), radius)` | 圆心和半径  | 圆心是浮点数，画图前转 `int`  |

#### 画图

| 调用                                                                                 | 怎么用                                                                                      |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `cv2.circle(img, center, radius, color[, thickness])`                              | 画圆。`thickness=-1` 是实心，正数是线宽。                                                             |
| `cv2.putText(img, text, org, fontFace, fontScale, color[, thickness[, lineType]])` | 写字。`org` 是文字左下角，不是左上角。字体用 `cv2.FONT_HERSHEY_SIMPLEX`，`lineType` 给 `cv2.LINE_AA` 抗锯齿好看很多。 |

颜色是 BGR 元组，红色写 `(0, 0, 255)`，绿色 `(0, 255, 0)`，蓝色 `(255, 0, 0)`。

#### numpy 基础

| 调用                           | 怎么用                         |
| ---------------------------- | --------------------------- |
| `np.array([...])`            | 造阈值上下界，注意给 `dtype=np.uint8` |
| `np.uint8`                   | OpenCV 图像的数据类型，0 到 255      |
| `np.ones((5, 5), np.uint8)`  | 方形卷积核                       |
| `np.zeros((h, w), np.uint8)` | 空掩膜                         |

### 第二关可能要用到的函数

这一关是二维码识别，主要用灰度转换、二维码解码器和画框。

#### 读图、转灰度、存图

| 调用                                             | 怎么用                                               |
| ---------------------------------------------- | ------------------------------------------------- |
| `cv2.imread(path) -> img`                      | 读图，读不到返回 `None`。                                  |
| `cv2.cvtColor(src, code) -> dst`               | 转颜色空间。这一关用 `cv2.COLOR_BGR2GRAY`，把 BGR 图转成灰度图。     |
| `cv2.cvtColor(src, cv2.COLOR_GRAY2BGR) -> dst` | 反过来把单通道灰度图转回三通道。`annotate` 里如果画布是灰度的，画彩色框之前要先转一下。 |
| `cv2.imwrite(path, img) -> bool`               | 存标注图。                                             |

二维码解码器喂灰度图就行，彩色图也能过，但没必要多算一遍。

#### 二维码解码

OpenCV 自带 `cv2.QRCodeDetector`

| 调用                                                                  | 怎么用                            |
| ------------------------------------------------------------------- | ------------------------------ |
| `detector.detectAndDecode(img) -> text, points, straight`           | 解一个码。`text` 是字符串，解不出是空串。       |
| `detector.detectAndDecodeMulti(img) -> ok, texts, points, straight` | 解多个码。`ok` 是布尔值，`texts` 是字符串元组。 |

`detectAndDecode` 的 `points` 形状是 `(1, 4, 2)`，用之前 `reshape(4, 2)`。`detectAndDecodeMulti` 的 `points` 形状是 `(N, 4, 2)`。四个角的顺序是左上、右上、右下、左下。

#### 画框和写字

| 调用                                                                     | 怎么用                                                                   |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `cv2.polylines(img, [pts], isClosed, color, thickness)`                | 把四个角连起来。`pts` 要是 `(N, 1, 2)` 或 `(N, 2)` 的整型数组，所以先 `astype(np.int32)`。 |
| `cv2.putText(img, text, org, fontFace, fontScale, color[, thickness])` | 把解出来的内容写在框的左上角。                                                       |

#### numpy 基础

| 调用                     | 怎么用                 |
| ---------------------- | ------------------- |
| `np.array(points)`     | 把解码器返回的角点转成数组       |
| `arr.reshape(4, 2)`    | 把 `(1, 4, 2)` 压成四个点 |
| `arr.astype(np.int32)` | 画图之前转成整数，浮点数不能直接画   |
| `arr.mean(axis=0)`     | 四个角求平均，就是二维码中心      |

### 第三关可能要用到的函数

这一关是 AprilTag 识别，和二维码那关很像，区别在检测器的建法和返回格式。

#### 读图、转灰度、存图

| 调用                                             | 怎么用                |
| ---------------------------------------------- | ------------------ |
| `cv2.imread(path) -> img`                      | 读图，读不到返回 `None`。   |
| `cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) -> dst` | 转灰度。检测器在灰度图上跑更稳。   |
| `cv2.cvtColor(src, cv2.COLOR_GRAY2BGR) -> dst` | 把灰度图转回三通道，画彩色框之前用。 |
| `cv2.imwrite(path, img) -> bool`               | 存标注图。              |

#### 建字典和检测器

| 调用                                                         | 怎么用                                         |
| ---------------------------------------------------------- | ------------------------------------------- |
| `cv2.aruco.getPredefinedDictionary(dict_id) -> dictionary` | 按家族取字典。这一关用 `cv2.aruco.DICT_APRILTAG_25H9`。 |
| `cv2.aruco.DetectorParameters() -> params`                 | 检测参数，默认的就行。                                 |
| `cv2.aruco.ArucoDetector(dictionary, params) -> detector`  | 建检测器。OpenCV 4.7 以前没有这个类。                    |
| `detector.detectMarkers(gray) -> corners, ids, rejected`   | 检测。`rejected` 是被拒绝的候选，调试时可以画出来看。            |

老版本 OpenCV（4.7 以前）用模块级函数：`corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary)`。

#### 整理结果

| 调用                                  | 怎么用                                            |
| ----------------------------------- | ---------------------------------------------- |
| `ids.flatten()`                     | 不同版本 `ids` 形状不一样，有的 `(N, 1)` 有的 `(N,)`，压平再用最稳。 |
| `np.array(corners).reshape(4, 2)`   | 每个标签的四个角，形状 `(1, 4, 2)`。                       |
| `points.mean(axis=0)`               | 四个角求平均，得到中心。                                   |
| `np.float32`                        | 存角点用这个精度。                                      |
| `np.array2string(arr, precision=1)` | 打印四角坐标时用，省得自己格式化。                              |

没检测到时 `ids` 是 `None`，用之前要判空。

#### 画图

| 调用                                                                 | 怎么用                                 |
| ------------------------------------------------------------------ | ----------------------------------- |
| `cv2.polylines(img, [pts], True, color, 2)`                        | 把四个角连起来。`pts` 要 `astype(np.int32)`。 |
| `cv2.circle(img, center, radius, color, -1)`                       | 在中心点画个实心圆。                          |
| `cv2.putText(img, "id=%d" % tag_id, org, fontFace, 0.7, color, 2)` | 把编号写在框的左上角。                         |

### 第四关可能要用到的函数

这一关是 OCR，用到的 OpenCV 函数不多，主要工作在预处理和 tesseract 上。

#### 读灰度图、存图

| 调用                                              | 怎么用                                |
| ----------------------------------------------- | ---------------------------------- |
| `cv2.imread(path, cv2.IMREAD_GRAYSCALE) -> img` | 直接读成单通道灰度图，省得再转。                   |
| `cv2.imwrite(path, img) -> bool`                | 把预处理后的图存下来，方便你看 tesseract 到底看到了什么。 |

#### 预处理

| 调用                                                          | 怎么用                                                                         |
| ----------------------------------------------------------- | --------------------------------------------------------------------------- |
| `cv2.resize(src, dsize[, fx, fy, interpolation]) -> dst`    | 放大。这一关用 `fx=2, fy=2`，`interpolation=cv2.INTER_CUBIC`。也可以直接给 `dsize=(宽, 高)`。 |
| `cv2.GaussianBlur(src, ksize, sigmaX) -> dst`               | 高斯模糊，压掉噪点。`ksize` 必须是正奇数，`(3, 3)` 或 `(5, 5)`。                               |
| `cv2.threshold(src, thresh, maxval, type) -> (retval, dst)` | 二值化。这一关用 `cv2.THRESH_BINARY + cv2.THRESH_OTSU`，阈值让 OpenCV 自己算。              |

tesseract 认的是黑字白底，所以二值化用 `THRESH_BINARY`

`threshold` 的 `thresh` 在 Otsu 模式下随便填，`retval` 会返回实际用的阈值。

#### 调 tesseract

| 调用                                                 | 怎么用                            |
| -------------------------------------------------- | ------------------------------ |
| `pytesseract.get_tesseract_version()`              | 装没装好，跑一下这个就知道。                 |
| `pytesseract.get_languages()`                      | 列出语言包，英文是 `eng`，中文是 `chi_sim`。 |
| `pytesseract.image_to_string(image, lang, config)` | 把图里的字读成字符串，行之间是 `\n`。          |

`--psm` 是页面分割模式，常见取值：

| psm | 含义                   |
| --- | -------------------- |
| 3   | 自动分页，默认值，小图容易猜错      |
| 6   | 整张图当成一块文本            |
| 7   | 当成一行文本               |
| 8   | 当成一个词                |
| 10  | 当成一个字符               |
| 11  | 稀疏文本，让 tesseract 自己找 |

### 第五关可能要用到的函数

这一关是 YOLO 推理，OpenCV 只负责读图和画框，识别本身交给 ultralytics。

#### 读图、存图

| 调用                               | 怎么用              |
| -------------------------------- | ---------------- |
| `cv2.imread(path) -> img`        | 读图，读不到返回 `None`。 |
| `cv2.imwrite(path, img) -> bool` | 存画好框的图。          |

#### 加载模型和推理

| 调用                                                     | 怎么用                                       |
| ------------------------------------------------------ | ----------------------------------------- |
| `YOLO(weights) -> model`                               | 加载权重。参数可以是本地 `.pt` 路径，也可以是模型名（会自动下载）。     |
| `model.predict(source, conf, iou, verbose) -> results` | 推理。`source` 可以是路径、numpy 数组（BGR）或者 PIL 图像。 |
| `results[0]`                                           | 一张图的结果。                                   |
| `result.boxes`                                         | 检测框，没检测到的时候可能是 `None`。                    |
| `result.boxes.xyxy`                                    | `(N, 4)`，左上、右下像素坐标。                       |
| `result.boxes.cls`                                     | `(N,)`，类别编号。                              |
| `result.boxes.conf`                                    | `(N,)`，置信度。                               |
| `result.names`                                         | `{编号: 类别名}` 的字典。                          |

`boxes` 里的每一项都是 tensor。取单个数值用 `.item()`，取四个坐标用 `.tolist()`，别直接当 Python 数字用。

归一化中心点 = `(x1+x2)/2/宽`，`(y1+y2)/2/高`。板块三要用这个值算像素误差。

#### 画框

| 调用                                                                            | 怎么用                     |
| ----------------------------------------------------------------------------- | ----------------------- |
| `cv2.rectangle(img, pt1, pt2, color, thickness)`                              | 画检测框，`pt1` 左上、`pt2` 右下。 |
| `cv2.getTextSize(text, fontFace, fontScale, thickness) -> ((w, h), baseline)` | 量一下类别标签占多大，给标签画底色块用。    |
| `cv2.putText(img, text, org, fontFace, fontScale, color[, thickness])`        | 把类别和置信度写在框旁边。           |

## 下一步

恭喜你现在已经完成了板块二的所有任务，现在你已经学会了无人机常用的视觉识别技术。

在板块三里，你需要开始把你上面写的这些东西接入仿真

你需要操控无人机起飞、定点、下视拍照、识别、降落，每一关都要自己写 ROS 相关的代码。

板块二里的函数可以复制粘贴，但 `rospy` 才是无人机的灵魂

有关rospy和一些视觉的进阶，你会在板块三里遇到并学习。
