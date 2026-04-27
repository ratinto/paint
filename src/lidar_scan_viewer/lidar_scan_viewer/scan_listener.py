import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import LaserScan


class ScanListener(Node):
    def __init__(self) -> None:
        super().__init__('scan_listener')
        self.declare_parameter('topic', '/scan')
        self.topic = self.get_parameter('topic').get_parameter_value().string_value

        # QoS settings to match YDLIDAR driver (BEST_EFFORT)
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        self.subscription = self.create_subscription(
            LaserScan,
            self.topic,
            self.scan_callback,
            qos,
        )

        self.get_logger().info(f'Listening for LaserScan on topic: {self.topic}')

    def scan_callback(self, msg: LaserScan) -> None:
        total_points = len(msg.ranges)
        if total_points == 0:
            return

        # Calculate directional indices
        front_index = total_points // 2
        left_index = total_points // 4
        right_index = 3 * total_points // 4

        front_distance = msg.ranges[front_index]
        left_distance = msg.ranges[left_index]
        right_distance = msg.ranges[right_index]

        self.get_logger().info(
            f'Front: {front_distance:.2f}m | Left: {left_distance:.2f}m | Right: {right_distance:.2f}m'
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ScanListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
