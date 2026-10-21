# 板块一 · 用 rosrun 和 roslaunch 跑自己的节点

## 先把节点和 master 的关系理清楚

ROS 里的程序叫节点（node）。节点之间不直接连接，都挂到一个叫 master 的进程上，由 master 帮忙牵线。master 就是 `roscore`。

所以顺序是：先有 master，再有节点。`rosrun` 不会帮你起 master，`roslaunch` 会。这是初学者最容易懵的一点：直接 `rosrun` 一个节点，终端里刷 `Unable to communicate with master!`，不是代码写错了，是没起 `roscore`。

## rosrun：跑单个节点

```bash
rosrun 包名 可执行文件名
```

注意第二个参数是可执行文件名，不一定等于节点在代码里 `ros::init` 的那个名字。C++ 里就是 `add_executable` 的第一个参数，Python 里就是脚本文件名。

去年的包：

```bash
rosrun template template
```

对应 `devel/lib/template/template`。

Python 脚本：

```bash
rosrun my_vision color_detect.py
```

带参数的话直接跟在后面：

```bash
rosrun my_vision color_detect.py --image test.png
```

这些参数会原样传进 `sys.argv`，用 `argparse` 接就行。

跑之前确认三件事：`roscore` 起着、`source devel/setup.bash` 过、Python 脚本有执行权限。三件事缺一件，报错信息都不一样：

| 缺什么    | 报错                                                                            |
| ------ | ----------------------------------------------------------------------------- |
| master | `Unable to communicate with master!`                                          |
| source | `[rosrun] Couldn't find executable named xxx below /opt/ros/noetic/share/...` |
| 执行权限   | `permission denied`                                                           |

## roslaunch：一次起一堆

launch 文件是 XML，放在包的 `launch/` 目录里，用包名加文件名调用：

```bash
roslaunch sim_task task.launch
```

它比 `rosrun` 多做了这些事：自动起 master（如果还没有）、按顺序启动多个节点、传参数、改话题名、设命名空间。仿真这种要同时起飞控、MAVROS、Gazebo 的场景，只能用它。

### 最小例子

```xml
<launch>
  <node pkg="my_vision" type="color_detect.py" name="color_detect" output="screen"/>
</launch>
```

`pkg` 是包名，`type` 是可执行文件名，`name` 是节点名。三个都得写对。

`output="screen"` 让节点的标准输出打到当前终端。不写的话，`ROS_INFO` 和 `print` 都看不到，你会以为程序没跑。

`name` 建议填上。去年 `template.launch` 里是 `name=""`，有些版本能起，但 `rosnode list` 里认不出是谁，也没法单独 kill。

### 传参数

launch 里用 `<arg>` 定义参数，节点里用 `$(arg 名字)` 取：

```xml
<launch>
  <arg name="image" default="$(find my_vision)/config/test.png"/>
  <arg name="min_area" default="500"/>

  <node pkg="my_vision" type="color_detect.py" name="color_detect" output="screen"
        args="--image $(arg image) --min-area $(arg min_area)"/>
</launch>
```

命令行覆盖：

```bash
roslaunch my_vision detect.launch min_area:=800
```

`<arg>` 是 launch 内部的变量，只在 launch 文件里有效。要给节点传 ROS 参数（那种能在代码里 `nh.param` 读到的），用 `<param>`：

```xml
<node pkg="template" type="template" name="template" output="screen">
  <param name="err_max" value="0.15"/>
  <param name="if_debug" value="1"/>
</node>
```

参数多了就写进 yaml，用 `<rosparam>` 加载。去年就是这么干的：

```xml
<node pkg="template" type="template" name="template" output="screen">
  <rosparam command="load" file="$(find template)/config/template.yaml"/>
</node>
```

`template.yaml` 里就两行：

```yaml
err_max : 0.15
if_debug : 1
```

### 改话题名

两个节点默认的话题对不上时，用 `<remap>`，不用改代码：

```xml
<node pkg="my_vision" type="image_view" name="viewer">
  <remap from="image" to="/camera/image_raw"/>
</node>
```

`from` 是代码里写的话题名，`to` 是你想接的实际话题。

### 组合启动

把仿真和自己的节点写进一个 launch，省得开三个终端：

```xml
<launch>
  <include file="$(find sim_task)/launch/task.launch"/>

  <node pkg="my_vision" type="color_detect.py" name="color_detect"
        output="screen"/>
</launch>
```

`<include>` 就是把别人的 launch 内容抄进来。注意被 include 的那个 launch 里如果有同名节点，会冲突。

多机或者多实例的时候用 `<group ns="...">` 加命名空间，话题会自动变成 `/ns/xxx`。单人开发用不上。

## 看节点有没有跑起来

```bash
rosnode list
```

列出所有节点。看到你的节点名就说明起来了。

```bash
rosnode info /color_detect
```

能看到它发了哪些话题、收了哪些、跟谁连着。排查"代码跑了但没数据"的时候很管用。

想单独杀掉某个节点：

```bash
rosnode kill /color_detect
```

比 `Ctrl+C` 整个 launch 温和。

## 看数据

```bash
rostopic list
rostopic echo /mavros/state
rostopic hz /camera/image_raw
rostopic info /camera/image_raw
```

`hz` 这个特别有用。话题存在不等于有数据，`hz` 打不出频率就是没人发。

```bash
rosmsg show mavros_msgs/State
```

看消息里有哪些字段，比自己猜快。

```bash
rqt_graph
```

一张图看所有节点和话题的连接关系。节点名、话题名都在上面，接错线一眼就能看出来。

```bash
rosbag record -O flight.bag /mavros/local_position/odom /camera/image_raw
```

录下来，出问题可以反复回放，不用每次都重新飞一遍。回放用 `rosbag play flight.bag`。

## 收尾

`Ctrl+C` 一般能干净退出。Gazebo 有时候会留下僵尸进程，端口被占着，下次起不来：

```bash
killall gzserver gzclient
```

顽固的再补一刀：

```bash
pkill -9 -f px4
```

## 常见错误

| 现象                                            | 原因                   | 处理                                              |
| --------------------------------------------- | -------------------- | ----------------------------------------------- |
| `Unable to communicate with master!`          | 没起 roscore           | `roscore`，或改用 `roslaunch`                       |
| `Couldn't find executable named xxx`          | 没 source，或名字写错       | `source devel/setup.bash`，`ls devel/lib/包名/` 确认 |
| `INFO: cannot launch node of type [pkg/node]` | `type` 和实际可执行文件对不上   | 改 launch，或改 `add_executable`                    |
| 节点起来了但终端没输出                                   | 没写 `output="screen"` | 加上                                              |
| 两个节点同名，一个莫名消失                                 | 节点名重复                | 改名，或加 `ns`                                      |
| `ROS_INFO` 看不到，`printf` 能看到                   | 输出级别或缓冲              | 确认 `output="screen"`，必要时 `stdbuf -o0`           |
| 端口 11311 被占                                   | 上次的 master 没退干净      | `killall roscore rosmaster`                     |
| `roslaunch` 报 XML 解析错                         | 标签没闭合、`$(find)` 拼错   | `xmllint --noout xxx.launch`                    |

## 什么时候用哪个

单个节点调试用 `rosrun`，一套流程用 `roslaunch`。仿真这种一次要起四五个进程的，别硬用 `rosrun`。
