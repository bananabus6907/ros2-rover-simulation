cmake_minimum_required(VERSION 3.8)
project(simulation)

# --- 1. 필수 패키지 찾기 ---
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(image_transport REQUIRED)

# --- 2. 실행 파일(camera_viewer) 빌드 ---
add_executable(camera_viewer
  src/camera_viewer.cpp
)

ament_target_dependencies(camera_viewer
  rclcpp
  sensor_msgs
  cv_bridge
  image_transport
)

# --- 3. 설치(install) 설정 ---
install(
  TARGETS camera_viewer
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch urdf worlds configs
  DESTINATION share/${PROJECT_NAME}
)

# --- 4. 패키지 마무리 ---
ament_package()
