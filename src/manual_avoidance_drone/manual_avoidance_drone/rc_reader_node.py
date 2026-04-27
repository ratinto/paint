import rclpy
from rclpy.node import Node
from mavros_msgs.msg import RCIn
from geometry_msgs.msg import Twist

class RCReaderNode(Node):
    def __init__(self):
        super().__init__('rc_reader_node')
        
        self.sub_rc = self.create_subscription(
            RCIn,
            '/mavros/rc/in',
            self.rc_callback,
            10
        )
        
        self.pub_cmd = self.create_publisher(Twist, '/pilot_cmd_vel', 10)
        
        # Timer to check for RC timeout
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.last_rc_time = self.get_clock().now()
        
        self.deadzone = 50
        self.center = 1500
        
        # Limits
        self.max_lin_x = 2.0
        self.max_lin_y = 2.0
        self.max_lin_z = 1.0
        self.max_ang_z = 1.0
        
        self.get_logger().info('RC Reader Node Started.')

    def map_channel(self, val, deadzone, center, min_val, max_val, out_min, out_max):
        if val > (center + deadzone):
            ratio = (val - (center + deadzone)) / (max_val - (center + deadzone))
            return ratio * out_max
        elif val < (center - deadzone):
            ratio = ((center - deadzone) - val) / ((center - deadzone) - min_val)
            return ratio * out_min
        return 0.0
        
    def rc_callback(self, msg: RCIn):
        if len(msg.channels) < 4:
            return
            
        self.last_rc_time = self.get_clock().now()
        
        ch_roll = msg.channels[0]
        ch_pitch = msg.channels[1]
        ch_throttle = msg.channels[2]
        ch_yaw = msg.channels[3]
        
        cmd = Twist()
        
        # Mapping Pitch -> linear.x (Forward/Backward) - usually low pitch stick = forward
        # Let's map conventionally: pitch stick forward (usually lowering PWM to 1000)
        # We will assume standard: 
        # Pitch: 1000 (forward) to 2000 (backward) -> mapping inverted
        # For simplicity, let's map 1500-2000 to positive, 1000-1500 to negative, user configures transmitter.
        cmd.linear.x = self.map_channel(ch_pitch, self.deadzone, self.center, 1000, 2000, -self.max_lin_x, self.max_lin_x)
        
        # Mapping Roll -> linear.y (Left/Right)
        cmd.linear.y = self.map_channel(ch_roll, self.deadzone, self.center, 1000, 2000, -self.max_lin_y, self.max_lin_y)
        
        # Mapping Throttle -> linear.z (Up/Down)
        cmd.linear.z = self.map_channel(ch_throttle, self.deadzone, self.center, 1000, 2000, -self.max_lin_z, self.max_lin_z)
        
        # Mapping Yaw -> angular.z
        cmd.angular.z = self.map_channel(ch_yaw, self.deadzone, self.center, 1000, 2000, -self.max_ang_z, self.max_ang_z)
        
        self.pub_cmd.publish(cmd)

    def timer_callback(self):
        # 0.5s timeout for RC signal
        now = self.get_clock().now()
        if (now - self.last_rc_time).nanoseconds / 1e9 > 0.5:
            # Hover command
            cmd = Twist()  # all zeros
            self.pub_cmd.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = RCReaderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()