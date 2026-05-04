import rclpy
from rclpy.node import Node
from mavros_msgs.msg import RCIn


class RCViewerNode(Node):
    def __init__(self):
        super().__init__('rc_viewer_node')

        self.sub_rc = self.create_subscription(
            RCIn,
            '/mavros/rc/in',
            self.rc_callback,
            10
        )

        self.get_logger().info('RC Viewer Node Started. Listening to RC inputs...')

    def rc_callback(self, msg: RCIn):
        channels = list(msg.channels)
        channel_str = ' | '.join(
            f'CH{i + 1}: {val}' for i, val in enumerate(channels) if val != 0
        )
        self.get_logger().info(f'RCIn [{len(channels)} ch] {channel_str}')


def main(args=None):
    rclpy.init(args=args)
    node = RCViewerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
