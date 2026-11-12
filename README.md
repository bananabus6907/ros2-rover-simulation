# ROS2 Rover Robot Simulation

Gazebo를 이용한 URDF/Xacro 기반 차동구동(Differential Drive) 로봇 시뮬레이션 프로젝트입니다.

## 프로젝트 개요

카메라가 장착된 3륜 로버 로봇을 URDF/Xacro로 모델링하고, Gazebo 시뮬레이션 환경에서 라인 트레이싱을 위한 영상 처리를 수행합니다.

### 주요 기능

- **URDF/Xacro 로봇 모델링**: 파라미터 기반 로봇 설계
- **Differential Drive**: 2륜 차동구동 방식
- **카메라 센서**: Gazebo 카메라 플러그인 통합
- **영상 보정**: 180도 회전 영상 처리
- **ROS2-Gazebo 브릿지**: 시뮬레이션과 ROS2 통신

## 로봇 사양

### 하드웨어 구성

```
로봇 구조:
├── Base Link (몸체)
│   ├── 크기: 1.0m (L) × 0.5m (W) × 0.3m (H)
│   └── 재질: Gazebo/White
├── Left Wheel (좌측 바퀴)
│   ├── 반지름: 0.3m
│   ├── 폭: 0.25m
│   └── 재질: Gazebo/Red
├── Right Wheel (우측 바퀴)
│   └── (좌측과 동일)
├── Caster Wheel (캐스터 바퀴)
│   ├── 반지름: 0.2m
│   └── 재질: Gazebo/Black
└── Camera Link (카메라)
    ├── 위치: 몸체 정면 상단 중앙
    └── 방향: Roll 180° (영상 반전)
```

### 센서 및 액추에이터

- **Differential Drive Plugin**
  - 좌우 바퀴 독립 제어
  - Wheel separation: 0.32m
  - Odometry 발행 (30Hz)
  - Max torque: 20 Nm

- **Camera Sensor**
  - Topic: `/camera/image_raw`
  - 해상도: 설정 가능
  - 180도 보정 후 `/camera/image_corrected`로 재발행

## 시스템 구조

```
┌─────────────────────────────────────────────────┐
│            Gazebo Simulation                     │
│  ┌──────────────┐         ┌─────────────┐      │
│  │  Rover Robot │ ◄─────► │ Camera Plugin│      │
│  │  (URDF/Xacro)│         └─────────────┘      │
│  └──────────────┘                               │
│         │                                        │
│         │ /cmd_vel (Twist)                      │
│         │ /odom (Odometry)                      │
│         │ /camera/image_raw (Image)             │
└─────────┼────────────────────────────────────────┘
          │
          │ ROS-GZ Bridge
          │
┌─────────▼────────────────────────────────────────┐
│                ROS2 Network                       │
│  ┌───────────────────────────────────────┐      │
│  │  camera_viewer_node (C++)              │      │
│  │  - Subscribe: /camera/image_raw        │      │
│  │  - Publish: /camera/image_corrected    │      │
│  │  - Process: 180° flip                  │      │
│  └───────────────────────────────────────┘      │
└──────────────────────────────────────────────────┘
```

## 파일 구조

```
simulation/
├── CMakeLists.txt          # 빌드 설정
├── package.xml             # 패키지 메타데이터
├── README.md
├── urdf/
│   ├── my_rover.urdf.xacro # 로봇 URDF 정의
│   └── camera.urdf.xacro   # 카메라 센서 매크로
├── launch/
│   └── simulation.launch.py # 시뮬레이션 실행 스크립트
├── src/
│   └── camera_viewer.cpp   # 카메라 영상 처리 노드
├── worlds/
│   └── default.sdf         # Gazebo 월드 파일
└── configs/
    ├── server.config       # Gazebo 서버 설정
    └── bridge.yaml         # ROS-GZ 브릿지 설정
```

## 기술 스택

- **ROS2**: Humble Hawksbill
- **Gazebo**: Harmonic (또는 Garden)
- **언어**: C++ (노드), Python (Launch), XML (URDF/Xacro)
- **라이브러리**:
  - OpenCV (영상 처리)
  - cv_bridge (ROS-OpenCV 변환)
  - ros_gz_sim (ROS2-Gazebo 통합)

## 설치 및 빌드

### 필수 요구사항

```bash
# ROS2 Humble
sudo apt install ros-humble-desktop

# Gazebo 및 ROS-GZ 브릿지
sudo apt install ros-humble-ros-gz-sim ros-humble-ros-gz-bridge

# OpenCV 및 cv_bridge
sudo apt install ros-humble-cv-bridge libopencv-dev
```

### 워크스페이스 빌드

```bash
# 워크스페이스 생성
mkdir -p ~/simulation_ws/src
cd ~/simulation_ws/src

# 프로젝트 클론
git clone <your-repo-url> simulation

# 빌드
cd ~/simulation_ws
colcon build --symlink-install
source install/setup.bash
```

## 실행 방법

### 기본 실행 (GUI 포함)

```bash
ros2 launch simulation simulation.launch.py
```

### Headless 모드 (GUI 없음)

```bash
ros2 launch simulation simulation.launch.py gui:=false
```

### 커스텀 월드 파일 사용

```bash
ros2 launch simulation simulation.launch.py worldfile:=/path/to/your/world.sdf
```

## ROS2 토픽

| 토픽 | 타입 | 설명 |
|------|------|------|
| `/cmd_vel` | `geometry_msgs/Twist` | 로봇 속도 제어 (입력) |
| `/odom` | `nav_msgs/Odometry` | 로봇 위치 정보 (출력) |
| `/camera/image_raw` | `sensor_msgs/Image` | 원본 카메라 영상 |
| `/camera/image_corrected` | `sensor_msgs/Image` | 180도 보정된 영상 |

## 로봇 제어 예제

### 텔레오퍼레이션 (키보드)

```bash
# 터미널 1: 시뮬레이션 실행
ros2 launch simulation simulation.launch.py

# 터미널 2: 키보드 제어
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### 명령어로 직접 제어

```bash
# 전진
ros2 topic pub /cmd_vel geometry_msgs/Twist \
  "{linear: {x: 0.5}, angular: {z: 0.0}}"

# 좌회전
ros2 topic pub /cmd_vel geometry_msgs/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.5}}"
```

## 카메라 영상 확인

```bash
# RViz2로 영상 확인
ros2 run rqt_image_view rqt_image_view

# 또는 명령줄에서 토픽 확인
ros2 topic echo /camera/image_corrected
```

## URDF/Xacro 파라미터

`urdf/my_rover.urdf.xacro`에서 수정 가능한 주요 파라미터:

```xml
<xacro:property name="wheel_separation" value="0.070" />
<xacro:property name="wheel_radius" value="0.3" />
<xacro:property name="caster_wheel_radius" value="0.2" />
<xacro:property name="wheel_width" value="0.25" />
<xacro:property name="body_width" value="0.5" />
<xacro:property name="body_length" value="1.0" />
<xacro:property name="body_height" value="0.3" />
```

## 개발 노트

### camera_viewer 노드

- **목적**: Gazebo 카메라의 180도 반전 영상을 보정
- **처리**: `cv::flip(image, -1)` - 상하좌우 반전
- **성능**: GUI 출력 제거로 경량화

### Differential Drive 설정

- **마찰 계수 (mu1, mu2)**: 0.84 (바퀴), 0.2 (몸체)
- **최대 토크**: 20 Nm
- **가속도**: 1.0 m/s²
- **Odometry 주파수**: 30 Hz

## 문제 해결

### 로봇이 스폰되지 않을 때

```bash
# Gazebo 서버 재시작
killall -9 gz
ros2 launch simulation simulation.launch.py
```

### 카메라 토픽이 안 보일 때

```bash
# 브릿지 설정 확인
ros2 topic list | grep camera

# 브릿지 재시작
ros2 run ros_gz_bridge parameter_bridge /camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image
```

### URDF 문법 확인

```bash
# Xacro 변환 확인
xacro urdf/my_rover.urdf.xacro > /tmp/robot.urdf

# URDF 검증
check_urdf /tmp/robot.urdf
```

## 학습 내용

1. **URDF/Xacro 모델링**
   - 파라미터 기반 로봇 설계
   - Joint와 Link 관계 정의
   - Gazebo 플러그인 통합

2. **ROS2-Gazebo 통합**
   - ros_gz_bridge 활용
   - Launch 파일 작성
   - Topic 매핑

3. **영상 처리**
   - cv_bridge 사용법
   - OpenCV 기본 연산
   - ROS2 이미지 메시지 변환

## 참고 자료

- [ROS2 Documentation](https://docs.ros.org/en/humble/)
- [Gazebo Documentation](https://gazebosim.org/docs)
- [URDF Tutorial](http://wiki.ros.org/urdf/Tutorials)
- [Xacro Tutorial](http://wiki.ros.org/xacro)

## 라이선스

Educational Project

## 작성자

- 2021042014 이승준
- 로봇 프로그래밍 과제 6, 7
