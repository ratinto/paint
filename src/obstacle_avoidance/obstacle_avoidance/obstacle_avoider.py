import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class ObstacleAvoider(Node):
    def __init__(self) -> None:
        super().__init__('obstacle_avoider')
        
        # We publish velocity commands to MAVROS
        # Usually ArduPilot/PX4 listen to this topic in GUIDED / OFFBOARD mode
        self.cmd_pub = self.create_publisher(
            Twist,
            '/mavros/setpoint_velocity/cmd_vel_unstamped',
            10
        )

        # QoS matching the LiDAR driver (BEST_EFFORT)
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos
        )

        self.declare_parameter('safe_distance', 1.0)
        self.safe_distance = self.get_parameter('safe_distance').value

        self.get_logger().info(f'Obstacle avoidance started (Safe distance: {self.safe_distance}m).')
        self.get_logger().info('Waiting for /scan data...')

    def scan_callback(self, msg: LaserScan) -> None:
        total_points = len(msg.ranges)
        if total_points == 0:
            return

        front_index = total_points // 2
        front_distance = msg.ranges[front_index]
        
        # Prepare the velocity command
        cmd_msg = Twist()
        
        # Valid distance check (ignore infinite or zero if blocked by casing)
        is_valid_distance = (0.1 < front_distance < float('inf')) and not math.isnan(front_distance)

        if is_valid_distance and front_distance < self.safe_distance:
            self.get_logger().warn(f'OBSTACLE DETECTED at {front_distance:.2f}m! Turning right to avoid.')
            # Stop moving forward, turn around Z-axis
            cmd_msg.linear.x = 0.0
            cmd_msg.angular.z = -0.5  # Spin right
        else:
            # self.get_logger().info('Path clear, moving forward.')
            # Move forward slowly, no turn
            cmd_msg.linear.x = 0.2
            cmd_msg.angular.z = 0.0

        # Send command to Pixhawk via MAVROS
        self.cmd_pub.publish(cmd_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
