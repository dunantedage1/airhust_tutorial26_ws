# 板块一 · 一个标准 ROS 包长什么样

## 包是什么

ROS 不是一个大程序，是一堆互相发消息的小程序。包（package）是这些小程序的最小组织单位。catkin 编译的时候，会在 `src/` 下面逐层扫描，凡是带 `package.xml` 的目录就算一个包。没有这个文件，你的代码放在 `src` 里也编译不了。

一个工作空间可以放很多个包。去年那个仓库就是两个：`sim_task` 放地图和仿真配置，`template` 给你们写代码。今年你至少要自己建一个。

## 建包

```bash
cd ~/airhust_tutorial_ws/src
catkin_create_pkg my_vision roscpp rospy std_msgs sensor_msgs cv_bridge
```

后面跟的是依赖。这个命令会生成一个目录，里面三个东西：`package.xml`、`CMakeLists.txt`、`src/`。依赖会自动写进 `package.xml`。

嫌命令记不住，手拷一个现成的包改也行，但 `package.xml` 里的 `<name>` 必须改，名字重复 catkin 会直接报错。

## 目录职责

| 目录或文件             | 放什么             | 注意                           |
| ----------------- | --------------- | ---------------------------- |
| `src/`            | C++ 源文件 `.cpp`  | 可以再分子目录，比如 `src/perception/` |
| `include/`        | 头文件 `.h` `.hpp` | 一般再套一层包名，见下文                 |
| `scripts/`        | Python 脚本       | 目录名随便叫，但脚本必须有可执行权限           |
| `launch/`         | `.launch` 启动文件  | 名字建议跟功能对应                    |
| `config/`         | `.yaml` 参数文件    | 常被 launch 里的 `rosparam` 加载   |
| `msg/` `srv/`     | 自定义消息和服务定义      | 需要改 CMakeLists，见第三篇          |
| `urdf/` `meshes/` | 机器人模型           | 仿真项目才有                       |
| `rviz/`           | `.rviz` 配置      | 省得每次手动加显示项                   |
| `test/`           | 测试代码            | 可空                           |
| `CMakeLists.txt`  | 编译规则            | 必须有                          |
| `package.xml`     | 包的身份证和依赖声明      | 必须有                          |

两个容易搞混的点。

第一，`include` 和 `scripts` 这些目录名是约定，不是 catkin 强制的。CMake 只认 `CMakeLists.txt` 里写了什么路径。但大家都这么放，你另起名字别人接手会骂人。

第二，`scripts/` 里的 Python 文件默认没有执行权限。`rosrun` 直接跑会报 `Permission denied`，得 `chmod +x scripts/*.py`，而且文件第一行要有：

```python
#!/usr/bin/env python3
```

少了这一行，系统不知道用什么解释器执行它。

## 一个最小的 C++ 包

```
my_vision/
├── package.xml
├── CMakeLists.txt
├── include/my_vision/
│   └── detector.h
└── src/
    └── detector_node.cpp
```

`src/detector_node.cpp`：

```cpp
#include <ros/ros.h>
#include <std_msgs/String.h>
#include "my_vision/detector.h"

int main(int argc, char** argv) {
  ros::init(argc, argv, "detector_node");
  ros::NodeHandle nh;

  ros::Publisher pub = nh.advertise<std_msgs::String>("vision/result", 10);
  ros::Rate rate(10);

  while (ros::ok()) {
    std_msgs::String msg;
    msg.data = detect();
    pub.publish(msg);
    ros::spinOnce();
    rate.sleep();
  }
  return 0;
}
```

`CMakeLists.txt` 里最少要有这几行：

```cmake
find_package(catkin REQUIRED COMPONENTS roscpp std_msgs)
include_directories(include ${catkin_INCLUDE_DIRS})
add_executable(detector_node src/detector_node.cpp)
target_link_libraries(detector_node ${catkin_LIBRARIES})
```

`add_executable` 的第一个参数就是节点名。这个名字要和 launch 文件里 `<node type="...">` 对得上，很多人第一次跑 launch 失败就是这里写岔了。

## 头文件为什么放 `include/包名/`

`include_directories(include)` 会把 `include/` 整个加进头文件搜索路径。如果你直接放 `include/detector.h`，代码里写 `#include "detector.h"` 能过。但工作空间里包一多，两个包都有 `detector.h`，谁先被搜到就看运气了。

放进子目录就没这个问题：

```cpp
#include "my_vision/detector.h"
```

一看就知道是哪个包的。去年的 `template` 包是 `include/template.h`，单包单文件时能用，多人协作时建议改成 `include/template/template.h`。

## 一个最小的 Python 包

Python 不需要编译，目录更简单：

```
my_vision_py/
├── package.xml
├── CMakeLists.txt
└── scripts/
    └── color_detect.py
```

`scripts/color_detect.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import rospy
from std_msgs.msg import String


def main():
    rospy.init_node("color_detect")
    pub = rospy.Publisher("vision/color", String, queue_size=10)
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        pub.publish("red")
        rate.sleep()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
```

`CMakeLists.txt` 里只要一行，把脚本装进 `devel`：

```cmake
catkin_install_python(PROGRAMS scripts/color_detect.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
```

不写这行也能用 `rosrun` 跑，但 `roslaunch` 或者安装到系统的时候会找不到。养成写的习惯。

另外，Python 包同样需要 `package.xml`，而且 `rospy` 要写进依赖。别以为脚本不用编译就不用声明。

## 命名建议

包名小写，用下划线，别用大写和横杠。ROS 的包名规范是只允许小写字母、数字、下划线，横杠在某些工具里会被当成参数分隔符。

节点名、话题名同理。话题用 `/vision/color` 这种带命名空间的写法，比 `color_result_final_v2` 好维护。

节点名在一个 master 里不能重复。两个同名节点起来，后起的会把先起的顶掉，而且不一定报错，现象是某个话题突然没数据了。

## 哪些东西不要提交

`build/`、`devel/`、`install/` 是编译产物，每个人的机器上都不一样，提交上去只会制造冲突。

`__pycache__/`、`*.pyc` 同理。

模型权重（`.pt`、`.onnx`）动辄几十上百 MB，别直接塞进 git。GitHub 单文件超过 100MB 会被拒收。用 Git LFS，或者放到 release 里下载。

工作空间根目录建一个 `.gitignore`：

```gitignore
build/
devel/
install/
__pycache__/
*.pyc
*.pt
```

## 对照去年的包

去年的 `template` 包结构是这样：

```
template/
├── CMakeLists.txt
├── package.xml
├── config/template.yaml
├── include/template.h
├── launch/template.launch
└── src/template.cpp
```

该有的都有，能跑。两个可以改进的地方：头文件没套子目录；`CMakeLists.txt` 里 `find_package` 列了 `message_generation`，但 `package.xml` 里没写对应依赖，这种不一致在别人机器上编译时容易出问题。

你自己建包的时候，把它当成反面教材看一眼就够了。

## 检查包有没有被 ROS 认到

```bash
rospack find my_vision
```

能打印出绝对路径，说明包在 `ROS_PACKAGE_PATH` 里。打印 `[rospack] Error: package 'my_vision' not found`，八成是没 `source devel/setup.bash`，或者没重新 `catkin_make`。

想看当前工作空间里有哪些包：

```bash
rospack list | grep airhust
```
