import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray
from mavros_msgs.msg import State

class AvoidanceControllerNode(Node):
    def __init__(self):
        super().__init__('avoidance_controller_node')
        
        self.sub_pilot = self.create_subscription(
            Twist,
            '/pilot_cmd_vel',
            self.pilot_callback,
            10
        )
        
        self.sub_sectors = self.create_subscription(
            Float32MultiArray,
            '/obstacle_sectors',
            self.sectors_callback,
            10
        )
        
        self.sub_state = self.create_subscription(
            State,
            '/mavros/state',
            self.state_callback,
            10
        )
        
        self.pub_cmd = self.create_publisher(Twist, '/mavros/setpoint_velocity/cmd_vel_unstamped', 10)
        
        self.fcu_connected = False
        self.fcu_mode = ""
        
        self.sectors = [float('inf'), float('inf'), float('inf'), float('inf')] # F, L, R, B
        
        # Tuning distances
        self.block_dist = 1.5  # Prevent moving toward obstacle
        self.hover_dist = 0.8  # Force hover if anything gets too close
        
        self.get_logger().info('Avoidance Controller Node Started.')

    def state_callback(self, msg: State):
        self.fcu_connected = msg.connected
        self.fcu_mode = msg.mode

    def sectors_callback(self, msg: Float32MultiArray):
        if len(msg.data) >= 4:
            self.sectors = msg.data

    def pilot_callback(self, msg: Twist):
        # Safety checks
        if not self.fcu_connected:
            return # Don't send anything if FCU is offline
            
        if self.fcu_mode != 'GUIDED':
            return # Only operate when in GUIDED mode
            
        out_cmd = Twist()
        # Copy original commands
        out_cmd.linear.x = msg.linear.x
        out_cmd.linear.y = msg.linear.y
        out_cmd.linear.z = msg.linear.z
        out_cmd.angular.z = msg.angular.z
        
        dist_front = self.sectors[0]
        dist_left = self.sectors[1]
        dist_right = self.sectors[2]
        dist_back = self.sectors[3]
        
        min_overall = min(self.sectors)
        
        # Override to Hover if something is too close
        if min_overall < self.hover_dist:
            out_cmd.linear.x = 0.0
            out_cmd.linear.y = 0.0
            out_cmd.linear.z = 0.0
            self.get_logger().warn(f'OBSTACLE TOO CLOSE ({min_overall:.2f}m) - FORCING HOVER')
            self.pub_cmd.publish(out_cmd)
            return

        # Front blocking
        if dist_front < self.block_dist and out_cmd.linear.x > 0:
            self.get_logger().warn(f'FRONT ({dist_front:.2f}m) - BLOCKING FORWARD')
            out_cmd.linear.x = 0.0
            
        # Back blocking
        if dist_back < self.block_dist and out_cmd.linear.x < 0:
            self.get_logger().warn(f'BACK ({dist_back:.2f}m) - BLOCKING BACKWARD')
            out_cmd.linear.x = 0.0
            
        # Left blocking
        if dist_left < self.block_dist and out_cmd.linear.y > 0:
            self.get_logger().warn(f'LEFT ({dist_left:.2f}m) - BLOCKING LEFT')
            out_cmd.linear.y = 0.0
            
        # Right blocking
        if dist_right < self.block_dist and out_cmd.linear.y < 0:
            self.get_logger().warn(f'RIGHT ({dist_right:.2f}m) - BLOCKING RIGHT')
            out_cmd.linear.y = 0.0
            
        # Publish the safe command
        self.pub_cmd.publish(out_cmd)

def main(args=None):
    rclpy.init(args=args)
    node = AvoidanceControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()