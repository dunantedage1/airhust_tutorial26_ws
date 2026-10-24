cmake_minimum_required(VERSION 3.0.2)
project(lab_vision_sim_task3)

find_package(catkin REQUIRED)

catkin_package()

install(DIRECTORY launch worlds models config
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
