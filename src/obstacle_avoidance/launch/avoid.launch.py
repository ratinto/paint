from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='obstacle_avoidance',
            executable='avoider',
            name='obstacle_avoider',
            output='screen',
            parameters=[
                {'safe_distance': 1.0}
            ]
        )
    ])
