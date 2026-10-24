# 板块三 · 仿真单元测试

## 这一板块在干嘛

亲爱的学弟学妹们，恭喜你们到了第三个板块，仿真单元测试。

在第二个板块中，你在离线图片上把颜色、二维码、AprilTag、OCR、YOLO 都跑过了一遍。

在这个板块中，你就需要开始做一些和无人机相关的事情了

这一板块的目标是：你需要在仿真环境中用无人机的下视摄像头测试你的视觉识别代码。

这个板块依旧是五关，我准备了五张地图，分别对应了上个板块中的五种内容

这五关用的地图都在 `lab_vision_sim_task3` 这个包里，world 放地图，models 放靶标，launch 负责起 PX4、MAVROS 和 Gazebo。

## 动手之前

先看看你是否能够做到下列几点，这是整个视觉仿真能跑起来的前提：

- 板块一的仿真环境能起来，`/mavros/state` 里 `connected: True`
- 下视相机能出图，`rostopic hz /camera/image_raw` 有频率
- launch 默认 spawn 的是 `iris_rplidar`，板块一改的是 `iris.sdf`，记得把下视相机加到 `iris_rplidar.sdf`，或者启动时加 `model:=iris`
- 板块二的五个脚本都能跑出结果
- 会写 launch，会用 `rosrun` 起节点

然后把 `lab_vision_sim_task3` 整个目录拷到你的 catkin 工作空间 `src/` 下，编译：

```bash
cp -r lab_vision_sim_task3 ~/airhust_tutorial_ws/src/
cd ~/airhust_tutorial_ws
catkin_make
source devel/setup.bash
```

起第一关试试：

```bash
roslaunch lab_vision_sim_task3 task1.launch
```

正常情况下 Gazebo 里会出现一块 20×20 的灰色地面，无人机停在原点，机头朝 +x，前面 x=1 的位置摆着三个色块。

注：launch 里已经把 `GAZEBO_MODEL_PATH` 指到 `lab_vision_sim_task3/models`，不用再往 `~/.gazebo/models` 拷靶标。如果你绕过 launch 直接 `gazebo task1.world`，那就得自己拷模型，不然靶标加载不出来。

## 地图和包里有什么

```
lab_vision_sim_task3/
├── launch/
│   ├── task1.launch      第一关：三个色块
│   ├── task2.launch      第二关：二维码
│   ├── task3.launch      第三关：AprilTag
│   ├── task4.launch      第四关：AIRHUST 文字
│   └── task5.launch      第五关：AirHust logo
├── worlds/
│   ├── task1.world
│   ├── task2.world
│   ├── task3.world
│   ├── task4.world
│   └── task5.world
├── models/
│   ├── qr_pad/           0.6×0.6 二维码靶标
│   ├── tag_pad/          0.6×0.6 AprilTag 靶标
│   ├── text_pad/         0.6×0.6 文字靶标
│   └── logo_pad/         0.6×0.6 logo 靶标
└── config/px4_config.yaml
```

每张地图里，无人机都出生在 `(0,0)`，机头朝 `+x`

## 五关一览

| 关卡 | 目标             | 你要交出的结果        | 降落点      |
| -- | -------------- | -------------- | -------- |
| 一  | 红绿蓝三个色块        | 三个颜色分别打印到终端    | 蓝色色块     |
| 二  | 二维码            | 解出来的字符串        | 二维码上     |
| 三  | AprilTag 36h11 | 标签编号           | 标签上      |
| 四  | AIRHUST 文字     | 识别出的文字         | 文字靶标上    |
| 五  | AirHust logo   | 自己训的模型能检出 logo | logo 靶标上 |

每关的“过关”不是看代码写得多漂亮，是看两件事：终端里打印的结果对不对，最后有没有落在靶标上。

## 第一关：三个色块

地图 `task1.world`，三个半径 0.3 米的圆：红色在 `(1,-1)`，绿色在 `(1,0)`，蓝色在 `(1,1)`。

任务流程：

1. 起飞，到 1.5 米左右悬停
2. 依次飞到三个色块上方，用下视相机识别正下方的颜色
3. 每识别到一个，就在终端打印出来，比如 `red`、`green`、`blue`
4. 三个都走完，飞到蓝色色块上方降落

识别部分可以直接用板块二第一关的 `inRange` 加轮廓那套。色块是纯红、纯绿、纯蓝，白底。或者你也可以探究一下hsv在颜色识别这一块的应用。一般来说，实际任务中，我们会更偏向于用hsv而不是RGB

## 第二关：二维码

地图 `task2.world`，`(1,0)` 放了一张 0.6×0.6 的二维码，里面的内容是一个神秘字符串

任务流程：

1. 起飞，飞到二维码上方
2. 用下视相机解码，把字符串打印到终端
3. 降落在二维码上

解码器建议先试 `detectAndDecodeMulti`，没结果再退回 `detectAndDecode`，板块二第二关应该写过。

## 第三关：AprilTag

地图 `task3.world`，`(1,0)` 放了一张 0.6×0.6 的 AprilTag，家族是 36h11（6×6 个格子）

任务流程和第二关一样：起飞、到标签上方、解码、把编号打印到终端、降落在标签上。

注意家族别选错。36h11 是 `cv2.aruco.DICT_APRILTAG_36H11`，用成 25h9 的话一个都检测不到，而且不报错。

## 第四关：AIRHUST 文字

地图 `task4.world`，`(1,0)` 放了一张 0.6×0.6 的图，白底黑字，内容是 `AIRHUST`。

任务流程还是起飞、到上方、识别、打印、降落。这关不用训练模型，直接调 tesseract 就行，板块二第四关已经装过、也写过一遍。

如果读出来是空的，先检查二值化有没有搞反，再试试 `--psm 6` 或 `--psm 7`。文字是横排的一行，`--psm 7` 有时候更好。

## 第五关：AirHust logo，精准降落

地图 `task5.world`，`(1,0)` 贴了一张 0.6×0.6 的 AirHust logo。

这一关和前面几关不一样，没有现成模型，你要自己训一个：

1. 拿 `newlogo.png` 做数据增强，造训练集。旋转、缩放、透视、亮度对比度、换背景、加噪声，能想到的都往上加。
2. 标注成 YOLO 格式，训一个检测模型。底座用任何yolo的nano模型都行。
3. 把模型接进节点，飞到 logo 上方检测。
4. 在靶标上面实现精准降落

数据增强可以看这个仓库：<https://github.com/FirmamentumX/Realscene-Yolo>。

yolo如何训练可以在b站看看这个视频：<https://www.bilibili.com/video/BV1d1W9z9E2G/?spm_id_from=333.337.search-card.all.click>

精准降落的思路：

- 检测框中心记作 `(cx, cy)`，画面中心是 `(W/2, H/2)`
- 误差 `ex = cx - W/2`，`ey = cy - H/2`，归一化之后乘一个系数当速度
- 误差大就飞快点，误差小就慢一点，接近中心时加个死区
- 连续若干帧误差都在死区里，就认为对准了，锁定当前坐标，停掉水平修正
- 锁定之后只往下降低高度，落到 logo 上

注意像素坐标和机体坐标的对应关系。下视相机装的时候可能转了角度，图像里的 +x、+y 不一定对应机体的前后左右，符号错了会越修越偏。先手动给一个小速度，看目标在画面里往哪边移动，把符号试出来。

## 图像怎么进来

和板块二不一样，仿真里没有 `cv2.imread`，图像是话题发过来的。Python 节点里大概长这样：

```python
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

bridge = CvBridge()


def image_callback(msg):
    frame = bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
    # frame 就是 numpy 数组，直接喂给板块二的函数


rospy.init_node("vision_node")
rospy.Subscriber("/camera/image_raw", Image, image_callback, queue_size=1)
rospy.spin()
```

`imgmsg_to_cv2` 要指定 `bgr8`，不然通道顺序可能不对。处理完的结果用 `rospy.loginfo` 打印，或者发到话题上，具体看关卡要求

## 贴图朝向

四张靶标贴图默认是“上边朝 +x”放的，也就是无人机从原点朝 +x 看过去，文字是正的。

但下视相机的安装角度、Gazebo 的贴图 UV 都可能让画面转 90 度或者 180 度。如果你起飞后发现文字是歪的，去 `worlds/taskN.world` 里找 `<include>` 的 `<pose>`，最后一个数是 yaw，改成 `0`、`1.57`、`3.14`、`-1.57` 试试，四个方向总有一个是正的。

## 常见问题

| 现象                     | 大概原因               | 怎么办                                                       |
| ---------------------- | ------------------ | --------------------------------------------------------- |
| Gazebo 里只有地面，没有靶标      | 模型路径没生效            | 用 launch 启动，别直接 `gazebo xxx.world`                        |
| 靶标是白块或黑块               | 贴图没加载              | 检查 `GAZEBO_MODEL_PATH`，确认 `models/*/materials/textures` 在 |
| 没有 `/camera/image_raw` | 下视相机没加到 spawn 的模型上 | 默认 spawn `iris_rplidar`，把相机加到这个模型，或者 `model:=iris`        |
| 二维码解不出来                | 白边被裁、图太小、对焦不清      | 飞低一点，确认整张码在画面里                                            |
| AprilTag 检测不到          | 家族选错               | 36h11 用 `DICT_APRILTAG_36H11`                             |
| OCR 读出空串               | 二值化反了、psm 不对       | 用 `THRESH_BINARY`，试 `--psm 6/7`                           |
| YOLO 检测不到 logo         | 训练集太单一             | 多做数据增强，换背景、换角度                                            |
| 降落时冲过头                 | 速度环系数太大            | 把比例系数调小，加死区                                               |

## 最后

这五关没有标准答案，同一关可以有很多种写法。验收看两件事：结果打印对不对，降落落没落在靶标上。

卡住的时候先做减法：把图像存下来离线跑通，再接回节点；把飞行单独跑通，先不管识别；两边都行了再合。比一上来就调整个闭环快得多。
