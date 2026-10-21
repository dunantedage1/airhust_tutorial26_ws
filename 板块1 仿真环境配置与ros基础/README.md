# 2026 级梯队培训 · 文档目录

这套材料分成四个板块。前两个在仓库里，后两个由队友补。

## 板块一：环境与工程规范

先把机器搭起来，再知道代码该往哪放。

1. [仿真环境配置](01_simulation_setup.md)：Ubuntu 上从零装 ROS + PX4 + Gazebo，跑通仓库地图，加下视相机
2. [ROS 包的标准结构](02_ros_package_structure.md)：`src`、`include`、`scripts`、`launch` 各放什么，怎么建包
3. [package.xml 和 CMakeLists.txt](03_cmake_and_package_xml.md)：两个文件逐行讲，依赖为什么写三处
4. [用 rosrun 和 roslaunch 跑节点](04_run_your_node.md)：master 是什么，launch 怎么写，出问题怎么看

## 板块二：视觉基础

五个完形填空，全部离线跑，不碰 ROS。代码和环境说明在 [`lab_vision/`](../lab_vision/README.md)。

顺序是颜色、二维码、AprilTag、OCR、YOLO。前四个只依赖 OpenCV，第五个用 ultralytics 做推理。

## 板块三：仿真单元测试

起飞、定点、下视拍照、识别、降落，五关。ROS 相关代码全部自己写，识别部分可以从板块二抄。

这一关开始分方向：视觉、避障、点云。三条线的题目不一样，带的人也不一样。

## 板块四：组队大任务

三人一队，参考去年《AirHust 2025 级梯队计划》的任务二，把地图、评分、答辩流程走一遍。

## 关于这套文档

板块一、二是我写的，有问题直接找我。板块三、四的内容由各自负责人补，补的时候沿用同样的目录结构：一篇文档讲一件事，图放 `image/`，命令能直接复制。

文档里的路径都以仓库根目录为准。`~/airhust_tutorial_ws` 是去年仓库的位置，今年换了名字的话，读到路径自己替换一下。
