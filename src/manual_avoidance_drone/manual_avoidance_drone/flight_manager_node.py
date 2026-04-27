import rclpy
from rclpy.node import Node
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode

class FlightManagerNode(Node):
    def __init__(self):
        super().__init__('flight_manager_node')
        
        self.sub_state = self.create_subscription(
            State,
            '/mavros/state',
            self.state_callback,
            10
        )
        
        self.client_arm = self.create_client(CommandBool, '/mavros/cmd/arming')
        self.client_mode = self.create_client(SetMode, '/mavros/set_mode')
        
        self.fcu_connected = False
        self.fcu_mode = ""
        self.fcu_armed = False
        
        self.timer = self.create_timer(1.0, self.timer_callback)
        
        self.get_logger().info('Flight Manager Node Started. Supervising GUIDED + Arming state.')

    def state_callback(self, msg: State):
        self.fcu_connected = msg.connected
        self.fcu_mode = msg.mode
        self.fcu_armed = msg.armed

    def timer_callback(self):
        if not self.fcu_connected:
            self.get_logger().info('Waiting for FCU connection...', throttle_duration_sec=5.0)
            return
            
        # Ensure mode is GUIDED
        if self.fcu_mode != 'GUIDED':
            if self.client_mode.wait_for_service(timeout_sec=1.0):
                self.get_logger().info('Requesting GUIDED mode...')
                req = SetMode.Request()
                req.custom_mode = 'GUIDED'
                self.client_mode.call_async(req)
            return  # Wait for mode to change
            
        # Ensure armed
        if not self.fcu_armed:
            if self.client_arm.wait_for_service(timeout_sec=1.0):
                self.get_logger().info('Requesting ARM...')
                req = CommandBool.Request()
                req.value = True
                self.client_arm.call_async(req)

def main(args=None):
    rclpy.init(args=args)
    node = FlightManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()