import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    webots_package_dir = get_package_share_directory(
        'robocon_2027_webots'
    )
    description_package_dir = get_package_share_directory(
        'robocon_2027_description'
    )

    webots_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                webots_package_dir,
                'launch',
                'simulation.launch.py'
            )
        )
    )

    xacro_file = os.path.join(
        description_package_dir,
        'urdf',
        'tr.urdf.xacro'
    )

    rviz_config_file = os.path.join(
        description_package_dir,
        'rviz',
        'tr_robot_sim.rviz'
    )

    robot_description = ParameterValue(
        Command([
            'xacro ',
            xacro_file
        ]),
        value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {
                'robot_description': robot_description
            }
        ]
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
    )

    return LaunchDescription([
        webots_simulation,
        robot_state_publisher,
        rviz,
    ])
