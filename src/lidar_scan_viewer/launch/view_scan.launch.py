from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        Node(
            package='lidar_scan_viewer',
            executable='scan_listener',
            name='scan_listener',
            output='screen',
            parameters=[{'topic': '/scan'}],
        ),
    ])
