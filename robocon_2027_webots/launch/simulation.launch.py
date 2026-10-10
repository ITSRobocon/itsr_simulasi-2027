import os

import launch
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from webots_ros2_driver.webots_controller import WebotsController
from webots_ros2_driver.webots_launcher import WebotsLauncher


def generate_launch_description():
    package_directory = get_package_share_directory(
        'robocon_2027_webots'
    )

    world_path = os.path.join(
        package_directory,
        'worlds',
        'simple_arena.wbt'
    )

    robot_description_path = os.path.join(
        package_directory,
        'urdf',
        'tr_webots.urdf'
    )

    with open(robot_description_path, 'r', encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    webots = WebotsLauncher(
        world=world_path
    )

    tr_webots_controller = WebotsController(
        robot_name='tr_robot',
        parameters=[
            {
                'robot_description': robot_description
            }
        ],
        respawn=True,
    )

    tr_driver = Node(
        package='robocon_2027_webots',
        executable='tr_webots_driver',
        namespace='/tr_webots',
        name='driver',
        output='screen',
    )

    shutdown_handler = (
        launch.actions.RegisterEventHandler(
            event_handler=(
                launch.event_handlers.OnProcessExit(
                    target_action=webots,
                    on_exit=[
                        launch.actions.EmitEvent(
                            event=launch.events.Shutdown()
                        )
                    ]
                )
            )
        )
    )

    return LaunchDescription([
        webots,
        tr_webots_controller,
        #tr_driver,
        shutdown_handler,
    ])