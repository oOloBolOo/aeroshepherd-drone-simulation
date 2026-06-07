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
        
        # Ładujemy lekki model bazowy
        self.model = YOLO("yolov8n.pt")
        
        self.cv_rgb = None
        self.cv_thermal = None

        # Subskrypcje pasm wizyjnych
        self.sub_rgb = self.create_subscription(Image, '/world/aeroshepherd/model/aeroshepherd_0/link/base_link/sensor/camera_sensor/image', self.rgb_callback, 10)
        self.sub_thermal = self.create_subscription(Image, '/world/aeroshepherd/model/aeroshepherd_0/link/base_link/sensor/thermal_camera/image', self.thermal_callback, 10)
        
        self.timer = self.create_timer(0.04, self.render_callback)
        self.get_logger().info("🚀 System wielospektralny AeroShepherd (Fuzja Pasma + Live Counter) aktywny!")

    def rgb_callback(self, msg):
        self.cv_rgb = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def thermal_callback(self, msg):
        # ✅ POPRAWKA: mono8 idealnie dopasowane do formatu <format>L8</format> w SDF
        gray = self.bridge.imgmsg_to_cv2(msg, "mono8")
        
        # Bezpieczny Auto-Gain: eliminujemy cyjanowy szum tła
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        if max_val > min_val:
            gray_normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        else:
            gray_normalized = gray
            
        self.cv_thermal = cv2.applyColorMap(gray_normalized, cv2.COLORMAP_JET)

    def render_callback(self):
        if self.cv_rgb is None or self.cv_thermal is None:
            return

        # Skalowanie do równej rozdzielczości roboczej
        rgb_res = cv2.resize(self.cv_rgb, (640, 480))
        thermal_res = cv2.resize(self.cv_thermal, (640, 480))

        # Pobieramy surowe wyniki detekcji z pasma RGB
        results_rgb = self.model(rgb_res, conf=0.35, verbose=False)[0]
        
        # Inicjalizacja licznika krów dla aktualnej klatki lotu
        licznik_krow = 0

        # Iterujemy po wykrytych obiektach, żeby ręcznie narysować zunifikowane ramki
        for box in results_rgb.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            
            # --- RYSOWANIE NA PASMIE RGB ---
            cv2.rectangle(rgb_res, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(rgb_res, f"krowa {conf:.2f}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # --- FUZJA: Przeniesienie pozycji geometrycznej na pasmo termowizyjne ---
            cv2.rectangle(thermal_res, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(thermal_res, f"krowa {conf:.2f}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            licznik_krow += 1

        # Nakładanie interfejsu (OSD) z dynamicznym licznikiem w locie
        cv2.putText(rgb_res, "PASMO VIS (RGB) - LIVE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(thermal_res, f"PASMO IR - ZLICZONE KROWY: {licznik_krow}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Łączenie obrazów w jeden horyzontalny panel wejściowy dla operatora
        presentation_view = cv2.hconcat([rgb_res, thermal_res])
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

# ✅ POPRAWKA: Przywrócone systemowe podkreślenia warunku uruchomieniowego
if __name__ == '__main__':
    main()