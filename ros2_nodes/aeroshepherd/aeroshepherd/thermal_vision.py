import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class DualSkyVision(Node):
    def __init__(self):
        super().__init__('dual_sky_vision')
        self.bridge = CvBridge()
        self.model = YOLO("yolov8n.pt")
        
        self.cv_rgb = None
        self.cv_thermal = None

        # Słuchamy PRAWDZIWYCH dwóch kamer z drona
        self.sub_rgb = self.create_subscription(Image, '/world/aeroshepherd/model/aeroshepherd_0/link/base_link/sensor/camera_sensor/image', self.rgb_callback, 10)
        self.sub_thermal = self.create_subscription(Image, '/world/aeroshepherd/model/aeroshepherd_0/link/base_link/sensor/thermal_camera/image', self.thermal_callback, 10)
        
        self.timer = self.create_timer(0.04, self.render_callback)
        self.get_logger().info("🚀 Prawdziwy system wielospektralny AeroShepherd (Natywne GZ Thermal) aktywny!")

    def rgb_callback(self, msg):
        self.cv_rgb = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def thermal_callback(self, msg):
        # Gazebo zwraca surowy, 8-bitowy obraz radiometryczny (L8)
        gray = self.bridge.imgmsg_to_cv2(msg, "mono8")
        # Nakładamy paletę JET na PRAWDZIWE dane termiczne z symulatora
        self.cv_thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    def render_callback(self):
        if self.cv_rgb is None or self.cv_thermal is None:
            return

        rgb_res = cv2.resize(self.cv_rgb, (640, 480))
        thermal_res = cv2.resize(self.cv_thermal, (640, 480))

        # Detekcja YOLOv8 na obu fizycznych pasmach
        res_rgb = self.model(rgb_res, conf=0.35, verbose=False)[0].plot()
        res_thermal = self.model(thermal_res, conf=0.25, verbose=False)[0].plot()

        cv2.putText(res_rgb, "PASMO VIS (RGB) - LIVE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(res_thermal, "PASMO IR (HARDWARE THERMAL)", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        presentation_view = cv2.hconcat([res_rgb, res_thermal])
        cv2.imshow("AeroShepherd Target Acquisition Dashboard", presentation_view)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = DualSkyVision()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()