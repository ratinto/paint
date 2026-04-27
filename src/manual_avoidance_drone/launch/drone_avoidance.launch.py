import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='manual_avoidance_drone',
            executable='rc_reader',
            name='rc_reader_node',
            output='screen'
        ),
        Node(
            package='manual_avoidance_drone',
            executable='lidar_processor',
            name='lidar_processor_node',
            output='screen'
        ),
        Node(
            package='manual_avoidance_drone',
            executable='avoidance_controller',
            name='avoidance_controller_node',
            output='screen'
        ),
        Node(
            package='manual_avoidance_drone',
            executable='flight_manager',
            name='flight_manager_node',
            output='screen'
        )
    ])