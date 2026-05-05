import rclpy
from rclpy.node import Node
from mavros_msgs.msg import State, RCIn
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
        
        self.sub_rc = self.create_subscription(
            RCIn,
            '/mavros/rc/in',
            self.rc_callback,
            10
        )
        
        self.client_mode = self.create_client(SetMode, '/mavros/set_mode')
        
        self.fcu_connected = False
        self.fcu_mode = ""
        self.fcu_armed = False
        
        self.get_logger().info('Flight Manager Node Started. Supervising GUIDED toggle via RC.')

    def state_callback(self, msg: State):
        self.fcu_connected = msg.connected
        self.fcu_mode = msg.mode
        self.fcu_armed = msg.armed

    def rc_callback(self, msg: RCIn):
        if not self.fcu_connected or len(msg.channels) < 5:
            return
            
        # We assume Channel 5 (Index 4) is our Manual/Guided switch
        guided_switch_pwm = msg.channels[4]
        
        # Log the switch state periodically to avoid console spam
        self.get_logger().info(f'Channel 5 switch PWM: {guided_switch_pwm}', throttle_duration_sec=2.0)
        
        # Switch LOW (<1500 PWM) -> Change to GUIDED Mode
        if guided_switch_pwm < 1500 and self.fcu_mode != 'GUIDED':
            if self.client_mode.wait_for_service(timeout_sec=1.0):
                self.get_logger().info('Switch LOW: Requesting GUIDED mode...')
                req = SetMode.Request()
                req.custom_mode = 'GUIDED'
                self.client_mode.call_async(req)
                
        # Switch HIGH (>1500 PWM) -> Return to LOITER Mode (Manual)
        elif guided_switch_pwm > 1500 and self.fcu_mode == 'GUIDED':
            if self.client_mode.wait_for_service(timeout_sec=1.0):
                self.get_logger().info('Switch HIGH: Requesting LOITER mode...')
                req = SetMode.Request()
                req.custom_mode = 'LOITER'
                self.client_mode.call_async(req)

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