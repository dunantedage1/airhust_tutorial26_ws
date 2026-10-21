# 板块一 · package.xml 和 CMakeLists.txt 怎么写

## 两个文件各管什么

`package.xml` 是包的说明书：这个包叫什么、谁维护、依赖哪些别的包。catkin 和 rosdep 靠它识别包、装依赖。

`CMakeLists.txt` 是施工图：哪些源文件编成哪个可执行文件、链接哪些库、头文件在哪。

写得不全，症状不一样。`package.xml` 漏了依赖，编译可能照样过，运行的时候才崩。`CMakeLists.txt` 写错，通常直接编不过。

## package.xml 完整示例

```xml
<?xml version="1.0"?>
<package format="2">
  <name>my_vision</name>
  <version>0.1.0</version>
  <description>颜色和二维码识别节点</description>

  <maintainer email="you@example.com">Your Name</maintainer>
  <license>MIT</license>

  <buildtool_depend>catkin</buildtool_depend>

  <depend>roscpp</depend>
  <depend>rospy</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>cv_bridge</depend>

  <export>
  </export>
</package>
```

下面逐项说。

`<package format="2">` 写 2，别写 1。format 1 用 `<run_depend>`，format 2 改成 `<exec_depend>`，Noetic 已经全面 format 2 了。

`<name>` 必须和目录名一致。不一致的话 catkin 能用，但 `rospack find` 会按 `<name>` 找，你自己会晕。

`<maintainer>` 和 `<license>` 是必填项。catkin 检查很严，缺了直接报错。`<maintainer>` 的 `email` 属性也不能空着，随便填个能收件的地址。

`<buildtool_depend>catkin</buildtool_depend>` 每个包都要有，这东西不能少。

`<depend>` 是快捷写法，等价于同时写 `build_depend`、`build_export_depend`、`exec_depend`。绝大多数情况用这个就够了。

只有一种情况需要拆开写：消息包。`message_generation` 只在编译时用，`message_runtime` 只在运行时用，拆开能少一点依赖：

```xml
<build_depend>message_generation</build_depend>
<exec_depend>message_runtime</exec_depend>
```

自己写的 C++ 库被别的包引用时，被引用的包需要 `build_export_depend`，让下游能拿到头文件路径。

`<export>` 一般空着，除非你要在别的工具里注册插件。

## 依赖要写三处，缺一不可

这是新手最容易掉进去的坑。加一个依赖，三个地方都要动：

1. `package.xml` 里声明，否则 rosdep 不知道要装
2. `CMakeLists.txt` 的 `find_package(catkin REQUIRED COMPONENTS ...)` 里列出来，否则 CMake 找不到头文件
3. 用到库的话，`target_link_libraries` 里带上 `${catkin_LIBRARIES}`

漏第 2 处，报 `fatal error: mavros_msgs/State.h: No such file or directory`。漏第 3 处，报 `undefined reference to ...`。

`cv_bridge` 比较特殊，它依赖 OpenCV。你系统里装了 `python3-opencv` 和 `libopencv-dev` 才能编过。Ubuntu 20.04 上：

```bash
sudo apt install libopencv-dev python3-opencv
```

## CMakeLists.txt 逐段看

下面是一个带自定义消息、C++ 节点和 Python 脚本的完整例子。大部分人用不到这么多，按需删。

```cmake
cmake_minimum_required(VERSION 3.0.2)
project(my_vision)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(catkin REQUIRED COMPONENTS
  roscpp
  rospy
  std_msgs
  sensor_msgs
  geometry_msgs
  cv_bridge
  message_generation
)

add_message_files(
  FILES
  Target.msg
)

generate_messages(
  DEPENDENCIES
  std_msgs
  geometry_msgs
)

catkin_package(
  INCLUDE_DIRS include
  CATKIN_DEPENDS roscpp rospy std_msgs sensor_msgs geometry_msgs message_runtime
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)

add_executable(vision_node src/vision_node.cpp src/detector.cpp)
target_link_libraries(vision_node ${catkin_LIBRARIES})

add_dependencies(vision_node ${${PROJECT_NAME}_EXPORTED_TARGETS} ${catkin_EXPORTED_TARGETS})

catkin_install_python(PROGRAMS scripts/tool.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

install(TARGETS vision_node
  ARCHIVE DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  LIBRARY DESTINATION ${CATKIN_PACKAGE_LIB_DESTINATION}
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
```

`cmake_minimum_required` 和 `project` 是 CMake 的固定开头。`project` 里的名字要和 `package.xml` 的 `<name>` 一样，后面的 `${PROJECT_NAME}` 就靠它。

`set(CMAKE_CXX_STANDARD 14)` 指定 C++ 版本。PX4 和 mavros 的头文件用 C++14 比较稳，写到 17 一般也没事。去年的 `template` 用的 17。

`find_package` 里列的是编译时要找到的包。列多了不影响编译速度，列少了就报找不到头文件。名字和 `package.xml` 里的 `<depend>` 对得上，别自己造。

`add_message_files` 和 `generate_messages` 只在你要发自定义消息时写。消息定义放 `msg/Target.msg`，`generate_messages` 的 `DEPENDENCIES` 里要写消息里用到的其他消息包，比如用了 `geometry_msgs/Point` 就得写 `geometry_msgs`。

`catkin_package` 是给下游用的，说明这个包对外提供什么。`INCLUDE_DIRS` 写头文件目录，`CATKIN_DEPENDS` 写对外暴露的依赖。自己玩的小包写个空的 `catkin_package()` 也能编过，但别人依赖你的时候就抓瞎了。

`include_directories` 加自己的 `include` 和 `${catkin_INCLUDE_DIRS}`。后者是所有依赖包的头文件路径，漏了必报错。

`add_executable(节点名 源文件...)`。节点名可以随便起，但 `rosrun 包名 节点名` 和 launch 里的 `type` 都要用它。源文件可以写多个，用空格隔开。

`target_link_libraries` 把 `${catkin_LIBRARIES}` 链进来。不写的话编译能过，链接的时候一堆 `undefined reference`。

`add_dependencies` 只在用自定义消息时需要。作用是保证消息头文件先生成，再编译你的节点。不加的话，第一次编译偶尔会失败，第二次又好了，很迷惑。

`catkin_install_python` 把 Python 脚本注册进 `devel`。`install(TARGETS ...)` 是把 C++ 节点装到 `install/` 空间，只在你要发布二进制包时有用，平时可以不写。

## 编译产物在哪

`catkin_make` 之后：

- C++ 可执行文件在 `devel/lib/包名/`
- Python 脚本在 `devel/lib/包名/`（被复制过去）
- 消息生成的头文件在 `devel/include/包名/`
- `devel/setup.bash` 把这些路径加进环境变量

所以改完 C++ 代码不重新 `catkin_make`，跑的还是旧程序。这个坑每年都有人踩，现象是"我明明改了代码但没生效"。

## 常见报错对照

| 报错                                                              | 原因                                           | 处理                                     |
| --------------------------------------------------------------- | -------------------------------------------- | -------------------------------------- |
| `fatal error: xxx.h: No such file or directory`                 | `find_package` 没列，或 `include_directories` 没加 | 补依赖，加 `${catkin_INCLUDE_DIRS}`         |
| `undefined reference to xxx`                                    | `target_link_libraries` 没写                   | 补 `${catkin_LIBRARIES}`                |
| `Could not find a package configuration file provided by "xxx"` | 系统没装这个包，或没 source                            | `apt install ros-noetic-xxx`，重新 source |
| `The manifest must contain a <name> tag`                        | `package.xml` 语法错，标签没闭合                      | 用 `xmllint --noout package.xml` 检查     |
| `roslaunch` 报 `type is not executable`                          | `add_executable` 的名字和 launch 里的 `type` 不一致   | 两边改成同一个名字                              |
| `Permission denied` 跑 Python 节点                                 | 脚本没有执行权限                                     | `chmod +x scripts/*.py`                |
| 第一次编译过，第二次反而失败                                                  | 消息生成顺序问题                                     | 加 `add_dependencies`                   |
| `catkin_make` 说找不到 `src/CMakeLists.txt`                         | 工作空间没初始化                                     | `catkin_init_workspace src`            |

## 最后一条建议

不要一次把 `CMakeLists.txt` 写全。先写能编过的最小版本，跑通了再加消息、加 Python、加安装规则。一次加太多，报错的时候分不清是哪一处引起的。
