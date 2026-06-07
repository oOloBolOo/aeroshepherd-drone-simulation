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
        
        # Standardowy model detekcji (bez problematycznego .track)
        self.model = YOLO("yolov8n.pt")
        
        self.cv_rgb = None
        self.cv_thermal = None

        # --- PARAMETRY KALIBRACJI FUZJI SENSORYCZNEJ ---
        self.CALIB_DX = 0       
        self.CALIB_DY = -5      
        self.CALIB_SCALE = 1.0  

        # --- AUTORSKI TRACKER GEOMETRYCZNY Z PAMIĘCIĄ ---
        # Struktura: { track_id: [x1, y1, x2, y2, frames_lost] }
        self.active_tracks = {}
        self.next_cow_id = 0
        self.total_counted_cows = set()

        # Subskrypcje pasm wizyjnych
        self.sub_rgb = self.create_subscription(Image, '/world/aeroshepherd/model/aeroshepherd_0/link/base_link/sensor/camera_sensor/image', self.rgb_callback, 10)
        self.sub_thermal = self.create_subscription(Image, '/world/aeroshepherd/model/aeroshepherd_0/link/base_link/sensor/thermal_camera/image', self.thermal_callback, 10)
        
        self.timer = self.create_timer(0.04, self.render_callback)
        self.get_logger().info("🚀 Inteligentny system Sensor Fusion AeroShepherd (Proximity Tracking) aktywny!")

    def rgb_callback(self, msg):
        self.cv_rgb = self.bridge.imgmsg_to_cv2(msg, "bgr8")

    def thermal_callback(self, msg):
        gray = self.bridge.imgmsg_to_cv2(msg, "mono8")
        
        # Auto-Gain kontrastu tła
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        if max_val > min_val:
            gray_normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        else:
            gray_normalized = gray
            
        self.cv_thermal = cv2.applyColorMap(gray_normalized, cv2.COLORMAP_JET)

    def render_callback(self):
        if self.cv_rgb is None or self.cv_thermal is None:
            return

        # Resizing do rozdzielczości roboczej interfejsu
        rgb_res = cv2.resize(self.cv_rgb, (640, 480))
        thermal_res = cv2.resize(self.cv_thermal, (640, 480))

        # Pobieramy surowe detekcje z pasma RGB
        results_rgb = self.model(rgb_res, conf=0.25, verbose=False)[0]
        
        current_boxes = []
        for box in results_rgb.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            current_boxes.append((x1, y1, x2, y2))
        
        # --- ALGORYTM ŚLEDZENIA PROKSYMALNEGO ---
        new_tracks = {}
        matched_current_indices = set()
        
        # 1. Kojarzenie istniejących śladów z nowymi ramkami (Greedy Proximity Match)
        for track_id, track_data in self.active_tracks.items():
            tx1, ty1, tx2, ty2, frames_lost = track_data
            tcx, tcy = (tx1 + tx2) / 2, (ty1 + ty2) / 2
            
            best_match_idx = -1
            min_dist = 40.0  # Maksymalne przesunięcie krowy na ekranie między klatkami (w pikselach)
            
            for idx, (bx1, by1, bx2, by2) in enumerate(current_boxes):
                if idx in matched_current_indices:
                    continue
                bcx, bcy = (bx1 + bx2) / 2, (by1 + by2) / 2
                dist = ((tcx - bcx)**2 + (tcy - bcy)**2)**0.5
                
                if dist < min_dist:
                    min_dist = dist
                    best_match_idx = idx
            
            if best_match_idx != -1:
                # Znaleziono kontynuację śladu - resetujemy licznik klatek zgubienia
                nbx1, nby1, nbx2, nby2 = current_boxes[best_match_idx]
                new_tracks[track_id] = [nbx1, nby1, nbx2, nby2, 0]
                matched_current_indices.add(best_match_idx)
            else:
                # Chwilowy zanik detekcji - inkrementujemy bufor pamięci (do 45 klatek = ~1.8 sekundy)
                if frames_lost < 45:
                    new_tracks[track_id] = [tx1, ty1, tx2, ty2, frames_lost + 1]
        
        # 2. Rejestracja zupełnie nowych obiektów wchodzących w kadr
        for idx, (bx1, by1, bx2, by2) in enumerate(current_boxes):
            if idx in matched_current_indices:
                continue
            
            self.next_cow_id += 1
            new_tracks[self.next_cow_id] = [bx1, by1, bx2, by2, 0]
            self.total_counted_cows.add(self.next_cow_id)
            
        self.active_tracks = new_tracks

        # --- RENDERING I FUZJA MATRYCOWA ---
        w_kadrze = 0
        for track_id, track_data in self.active_tracks.items():
            tx1, ty1, tx2, ty2, frames_lost = track_data
            
            # Rysujemy tylko obiekty aktualnie potwierdzone w klatce
            if frames_lost > 0:
                continue
                
            w_kadrze += 1
            
            # Pasmo VIS (RGB)
            cv2.rectangle(rgb_res, (tx1, ty1), (tx2, ty2), (0, 255, 0), 2)
            cv2.putText(rgb_res, f"krowa #{track_id}", (tx1, ty1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Pasmo IR (Fuzja geometryczna ze skorygowaną paralaksą)
            w = tx2 - tx1
            h = ty2 - ty1
            cx = int((tx1 + tx2) / 2 * self.CALIB_SCALE) + self.CALIB_DX
            cy = int((ty1 + ty2) / 2 * self.CALIB_SCALE) + self.CALIB_DY
            
            itx1 = int(cx - (w / 2) * self.CALIB_SCALE)
            ity1 = int(cy - (h / 2) * self.CALIB_SCALE)
            itx2 = int(cx + (w / 2) * self.CALIB_SCALE)
            ity2 = int(cy + (h / 2) * self.CALIB_SCALE)
            
            cv2.rectangle(thermal_res, (itx1, ity1), (itx2, ity2), (0, 0, 255), 2)
            cv2.putText(thermal_res, f"KROWA #{track_id}", (itx1, ity1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Interfejs telemetryczny dla operatora UAV
        cv2.putText(rgb_res, f"W KADRZE: {w_kadrze} szt.", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(thermal_res, f"ZAREJESTROWANE STADO (TOTAL): {len(self.total_counted_cows)}", (20, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

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

if __name__ == '__main__':
    main()