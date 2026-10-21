# 板块一 · 仿真环境配置

## 这篇看完你能做到什么

在一台 Ubuntu 机器上从零起一套 PX4 + Gazebo 仿真。地图是仓库里的 `task.world`，无人机底下挂一个摄像头，你能用 `rqt_image_view` 看到地面画面。

后面板块三的所有任务都在这个环境里跑，所以这一步别糊弄过去。跑不通就先别往下看。

## 需要准备什么

Ubuntu 20.04，物理机、双系统、VMware 虚拟机都行。虚拟机的显卡设置里要把 3D 加速打开，不然 Gazebo 会卡成幻灯片。

ROS Noetic，Gazebo 11，PX4。这三个版本要配套：Noetic 对应 Ubuntu 20.04，自带 Gazebo 11 和 Python 3.8。

macOS 跑不了。PX4 的构建脚本是给 Linux 写的，Apple Silicon 上连 Gazebo Classic 都没有原生包。手上只有 Mac 的，装个 Ubuntu 虚拟机，或者直接用实验室的机器。

## 第一步：装 ROS Noetic

照着官方文档做，别用第三方一键脚本：

```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu focal main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt install curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo apt update
sudo apt install ros-noetic-desktop-full
```

装完初始化一次：

```bash
sudo rosdep init
rosdep update
```

`rosdep` 是 ROS 的依赖管理，装包和编包的时候会用到。这两条命令报错多半是网络问题，挂代理重试。

## 第二步：把仓库拉下来编译

```bash
cd ~
git clone https://github.com/hus-king/airhust_tutorial_ws.git
cd airhust_tutorial_ws
catkin_make
echo "source ~/airhust_tutorial_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

`catkin_make` 做三件事：在 `src` 下把每个包找出来，把编译中间文件扔进 `build/`，把可执行文件和库扔进 `devel/`。第一次跑的时候它还会在 `src` 里生成一个 `CMakeLists.txt` 软链接，要是报找不到这个文件，手动执行 `catkin_init_workspace src` 再编译。

`setup.bash` 的作用是把 `devel/` 里的路径塞进 `ROS_PACKAGE_PATH`、`LD_LIBRARY_PATH` 这些环境变量。不 source 它，`rosrun` 和 `roslaunch` 就找不到你自己写的包。写进 `~/.bashrc` 是为了每个新终端都自动带上。

改完代码记得重新 `catkin_make`。只改 Python 脚本不用编译，改 C++ 必须编译。

## 第三步：装 PX4 和 MAVROS

```bash
cd ~
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot
bash ./Tools/setup/ubuntu.sh
```

`--recursive` 不能省。子模块没拉全，编译时会报一堆找不到头文件和 CMake 文件，而且报错信息完全不提子模块，很难查。

装完依赖先单独编一次，确认 SITL 本身是好的：

```bash
make px4_sitl gazebo
```

第一次会编译十几分钟。看到 PX4 控制台出现 `pxh>` 提示符，Gazebo 窗口里有一架 iris，说明飞控仿真通了。按 `Ctrl+C` 退出。

接着装 MAVROS，它是 ROS 和 PX4 之间的桥：

```bash
sudo apt install ros-noetic-mavros ros-noetic-mavros-extras
sudo /opt/ros/noetic/lib/mavros/install_geographiclib_datasets.sh
```

第二条必须跑。不跑的话 mavros 启动会报 GeographicLib 数据集缺失，`/mavros/local_position` 一直没数据，你会以为是自己代码的问题，其实是数据文件没装。

## 第四步：让 ROS 找到 PX4

```bash
echo "source ~/PX4-Autopilot/Tools/setup_gazebo.bash ~/PX4-Autopilot ~/PX4-Autopilot/build/px4_sitl_default" >> ~/.bashrc
echo "export ROS_PACKAGE_PATH=\$ROS_PACKAGE_PATH:~/PX4-Autopilot" >> ~/.bashrc
echo "export ROS_PACKAGE_PATH=\$ROS_PACKAGE_PATH:~/PX4-Autopilot/Tools/sitl_gazebo" >> ~/.bashrc
source ~/.bashrc
```

仓库的 `task.launch` 里有一行 `$(find px4)/launch/px4.launch`，靠的就是这里加的路径。

新版 PX4 把 gazebo 相关文件挪到了 `Tools/simulation/gazebo-classic/sitl_gazebo`。上面第三行路径不存在的话换成新的。先确认两件事：

```bash
ls ~/PX4-Autopilot/Tools/sitl_gazebo
ls ~/PX4-Autopilot/launch/px4.launch
```

第二个文件存在是关键。PX4 1.14 之后有些分支删了 ROS1 的 launch，你这里要是没有，有两条路：切到还能用的版本 `git checkout v1.13.3 && git submodule update --init --recursive`，或者把 `task.launch` 里 include px4 的那段注释掉，自己开终端 `make px4_sitl gazebo`，再另外起 `roslaunch mavros px4.launch fcu_url:=udp://:14540@localhost:14557`。前者省事，后者更接近真机调试的流程。

## 第五步：把地图模型拷进 Gazebo

```bash
cd ~/airhust_tutorial_ws/src/sim_task
mkdir -p ~/.gazebo/models
cp -r models/* ~/.gazebo/models/
```

Gazebo 加载模型有自己的搜索路径，默认是 `~/.gazebo/models`。`task.world` 里的字母、数字、二维码牌子是用 `model://` 引用的，Gazebo 就按名字去这个路径找。门、柱子、圆环没有走外部模型，是直接写在 world 里的几何体。不拷的话，场地大致还在，但那几块牌子会加载不出来，Gazebo 终端里会刷 `Unable to find model` 之类的警告。`spawn_model` 生成无人机时用 `-database` 参数，走的也是这条路径。

顺手提一句：`task.launch` 默认 spawn 的机型是 `iris_rplidar`，这个模型不在仓库里。Gazebo 会去官方模型库下载，第一次要联网。离线机器要么提前把模型放进 `~/.gazebo/models`，要么把这个参数换成 `iris`：

```bash
roslaunch sim_task task.launch model:=iris
```

换成 `iris` 就没有雷达了，但下视相机和飞控都在，够板块三用。

## 第六步：起仿真

```bash
roslaunch sim_task task.launch
```

这一个 launch 干了四件事：起 PX4 SITL、起 MAVROS、加载 `task.world`、把无人机 spawn 到 `(0,0)` 上方。

起来以后另开终端验证：

```bash
rosnode list
rostopic echo -n1 /mavros/state
```

`connected: True` 说明飞控和 ROS 通了。Gazebo 里应该能看到 38×8 的场地：左边几根柱子，中间是门和圆环，右边是识别区和降落靶标。

## 第七步：加下视摄像头

默认的 iris 模型没有下视相机，要改 PX4 的模型文件。先找到它：

```bash
find ~/PX4-Autopilot -path "*models/iris/iris.sdf"
```

打开这个文件，在 `<model name='iris'>` 里面、和已有的 `<sensor>` 同级的位置插入下面这段：

```xml
      
      <sensor name="downward_camera" type="camera">
        <pose>0 0 -0.1 0 1.57 0</pose>
        <always_on>1</always_on>
        <camera>
          <horizontal_fov>1.386</horizontal_fov>
          <image>
            <width>640</width>
            <height>480</height>
            <format>R8G8B8</format>
          </image>
          <clip>
            <near>0.1</near>
            <far>30</far>
          </clip>
        </camera>
        <plugin name="camera_plugin" filename="libgazebo_ros_camera.so">
          <topicName>camera/image_raw</topicName>
          <frameName>camera_frame</frameName>
          <distortionK1>0.01401476</distortionK1>
          <distortionK2>0.01596416</distortionK2>
          <distortionK3>0.25648364</distortionK3>
          <distortionT1>-0.00489736</distortionT1>
          <distortionT2>0.00298071</distortionT2>
        </plugin>
      </sensor>
```

几个地方解释一下。

`<pose>0 0 -0.1 0 1.57 0</pose>` 是相对机体系的位置和姿态：往下挪 10cm，绕 y 轴转 90 度。1.57 是弧度，写成 90 相机就横着了。

`horizontal_fov` 是水平视场角，单位弧度。1.386 大约 79 度，焦距越短视场越大，但边缘畸变也越厉害。

`<always_on>1</always_on>` 让传感器一直出图。不加这一行，有些情况下相机要等到有可视化窗口才开始工作，表现为话题存在但没有数据。

话题名由 `<topicName>` 决定，这里是 `camera/image_raw`。老版本的 `gazebo_ros_camera` 不认这个标签，会用 `<cameraName>` 拼出 `/<cameraName>/image_raw`。所以改完先别猜名字，直接查：

```bash
rostopic list | grep -i image
```

改完 `iris.sdf` 必须重启 `gzserver` 才生效，只重启自己的节点没用。

看画面：

```bash
rqt_image_view
```

下拉框里选摄像头话题。或者用 `rosrun image_view image_view image:=/camera/image_raw`，省事。

## 验收清单

- Gazebo 里场地完整，有柱子、门、圆环、字母数字牌，不是一片白
- `rostopic echo -n1 /mavros/state` 里 `connected: True`
- `rostopic hz /camera/image_raw` 稳定在 30Hz 左右
- `rqt_image_view` 能看到地面，不是全黑也不是全白

四条都对上，仿真环境就算配好了。

## 常见故障

| 现象                                                              | 原因                       | 处理                                         |
| --------------------------------------------------------------- | ------------------------ | ------------------------------------------ |
| Gazebo 里没有字母、数字、二维码牌子                                           | 模型没拷到 `~/.gazebo/models` | 回第五步重新拷，重启 `gzserver`                      |
| `spawn_model` 报找不到 `iris_rplidar`                               | 模型库没下下来                  | 联网重试，或 `model:=iris`                       |
| `Could not find a package configuration file provided by "px4"` | PX4 没 source，或路径写错       | 检查第四步的三行 export                            |
| `RLException: [task.launch] is neither a launch file...`        | 没 source 工作空间            | `source devel/setup.bash`                  |
| `/mavros/state` 一直 `connected: False`                           | PX4 没起、端口被占、`fcu_url` 不对 | 先看 PX4 终端有没有报错；`lsof -i:14540` 查占用         |
| 摄像头话题存在但没数据                                                     | 缺 `always_on`，或模型没重启     | 加 `<always_on>1</always_on>`，重启 `gzserver` |
| Gazebo 启动直接崩                                                    | 显卡驱动或虚拟机 3D 加速           | 关掉虚拟机 3D 试试，或换物理机                          |
| 编译报找不到 mavros_msgs                                              | 没装 mavros，或装到了别的 ROS 版本  | `apt list --installed \| grep mavros` 确认   |

## 下一步

环境好了先别急着写飞行代码。板块二全是离线图片处理，在你自己电脑上就能跑，不依赖这套仿真。等五个识别任务都写顺了，再回仿真里跟飞控打交道会轻松很多。
