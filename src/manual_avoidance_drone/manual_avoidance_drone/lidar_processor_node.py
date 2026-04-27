import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float32MultiArray

class LidarProcessorNode(Node):
    def __init__(self):
        super().__init__('lidar_processor_node')
        
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.sub_scan = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos
        )
        
        self.pub_sectors = self.create_publisher(Float32MultiArray, '/obstacle_sectors', 10)
        
        self.get_logger().info('Lidar Processor Node Started.')

    def scan_callback(self, msg: LaserScan):
        # Initialize sectors with infinity
        min_front = float('inf')
        min_left = float('inf')
        min_right = float('inf')
        min_back = float('inf')
        
        angle_min = msg.angle_min
        angle_increment = msg.angle_increment
        
        for i, distance in enumerate(msg.ranges):
            # Ignore invalid readings
            if math.isnan(distance) or distance < msg.range_min or distance > msg.range_max:
                continue
                
            # Calculate angle in degrees
            angle_rad = angle_min + i * angle_increment
            # Normalize angle to [-pi, pi]
            angle_rad = math.atan2(math.sin(angle_rad), math.cos(angle_rad))
            angle_deg = math.degrees(angle_rad)
            
            # Map into sectors
            if -30 <= angle_deg <= 30:
                min_front = min(min_front, distance)
            elif 30 < angle_deg <= 120:
                min_left = min(min_left, distance)
            elif -120 <= angle_deg < -30:
                min_right = min(min_right, distance)
            else:  # remaining ranges are 120 to 180 and -180 to -120
                min_back = min(min_back, distance)
                
        # Publish the data: front, left, right, back
        # Using a fixed layout where data[0]=front, data[1]=left, data[2]=right, data[3]=back
        sectors_msg = Float32MultiArray()
        sectors_msg.data = [float(min_front), float(min_left), float(min_right), float(min_back)]
        self.pub_sectors.publish(sectors_msg)

def main(args=None):
    rclpy.init(args=args)
    node = LidarProcessorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()