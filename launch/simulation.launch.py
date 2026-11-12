from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    # --- 1. Launch Arguments (인자 선언) ---

    gui_arg = DeclareLaunchArgument(
        name='gui',
        default_value='true',
        description='Enable Gazebo GUI (true or false)'
    )

    world_arg = DeclareLaunchArgument(
        name='worldfile',
        default_value=PathJoinSubstitution([
            FindPackageShare('simulation'), 'worlds', 'default.sdf'
        ]),
        description='Path to the Gazebo world file'
    )

    package_arg = DeclareLaunchArgument(
        'urdf_package',
        description='The package where the robot description is located',
        default_value='simulation'
    )
    model_arg = DeclareLaunchArgument(
        'urdf_package_path',
        description='The path to the robot description relative to the package root',
        default_value='urdf/my_rover.urdf.xacro'
    )

    # --- 2. Config File Paths (설정 파일 경로) ---

    server_config_path = PathJoinSubstitution([
        FindPackageShare('simulation'),
        'configs',
        'server.config'
    ])
    server_config_env = SetEnvironmentVariable(
        'GZ_SIM_SERVER_CONFIG_PATH',
        value=server_config_path
    )

    bridge_config_path = PathJoinSubstitution([
        FindPackageShare('simulation'),
        'configs',
        'bridge.yaml'
    ])

    # --- 3. Gazebo Simulation (가제보 실행) ---

    # gui == true : 서버 + GUI (gz_sim.launch.py)
    gz_with_gui = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ),
        launch_arguments={
            # worldfile 인자를 그대로 gz_args로 넘김
            'gz_args': LaunchConfiguration('worldfile'),
        }.items(),
        condition=IfCondition(LaunchConfiguration('gui'))
    )

    # gui == false : 서버만 (gz_server.launch.py)
    gz_headless = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_server.launch.py'
            ])
        ),
        launch_arguments={
            'world_sdf_file': LaunchConfiguration('worldfile'),
        }.items(),
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )

    # --- 4. Robot Model & Nodes (로봇 모델 및 노드) ---

    # my_rover.urdf.xacro 경로
    robot_model_xacro = PathJoinSubstitution([
        FindPackageShare('simulation'),
        'urdf',
        'my_rover.urdf.xacro'
    ])

    # (A) /robot_description 만들기 (xacro + robot_state_publisher)
    robot_description = ParameterValue(
        Command([
            'xacro ',
            robot_model_xacro
        ]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen',
    )

    # (B) Gazebo에 로봇 스폰 (ros_gz_sim create, -param robot_description 사용)
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        # create 노드에:
        #   -world default
        #   -name my_rover
        #   -param robot_description
        #   -z 0.2  : 로봇을 바닥에서 0.2m 위에 스폰
        arguments=[
            '-world', 'default',
            '-name', 'my_rover',
            '-param', 'robot_description',
            '-z', '0.3',
        ],
        parameters=[{'robot_description': robot_description}],
        output='screen',
    )

    # ROS-GZ Bridge (ros_gz_bridge)
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[
            {
                'config_file': bridge_config_path
            }
        ],
        output='screen',
    )

    camera_viewer_node = Node(
        package='simulation',
        executable='camera_viewer',  
        name='camera_viewer_node',
        output='screen',
    )

    # --- 5. Return Launch (실행 목록 반환) ---

    return LaunchDescription([
        # Arguments
        gui_arg,
        world_arg,
        package_arg,
        model_arg,

        # Gazebo
        server_config_env,
        gz_with_gui,
        gz_headless,

        # Nodes
        robot_state_publisher_node,
        bridge_node,
        camera_viewer_node,
        spawn_entity,
    ])
