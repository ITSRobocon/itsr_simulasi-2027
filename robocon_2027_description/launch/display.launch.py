import os

from ament_index_python.packages import (
    get_package_share_directory,
)

from launch import LaunchDescription
from launch.substitutions import Command

from launch_ros.actions import Node

from launch_ros.parameter_descriptions import (
    ParameterValue,
)


def generate_launch_description():
    package_dir = get_package_share_directory(
        'robocon_2027_description'
    )

    xacro_file = os.path.join(
        package_dir,
        'urdf',
        'tr.urdf.xacro'
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
                'robot_description':
                    robot_description
            }
        ]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        joint_state_publisher,
        rviz,
    ])