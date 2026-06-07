import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from px4_msgs.msg import BatteryStatus, VehicleLocalPosition
import math

class PonrEstimator(Node):
    def __init__(self):
        super().__init__('ponr_estimator')
        
        # Profil QoS dla PX4
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # Stan drona (zmienne globalne węzła)
        self.battery_pct = 1.0       # 0.0 do 1.0 (100%)
        self.drone_x = 0.0           # Pozycja X od punktu startu (metry)
        self.drone_y = 0.0           # Pozycja Y od punktu startu (metry)
        self.drone_z = 0.0           # Wysokość (w układzie NED: wartości ujemne to góra!)
        self.vx = 0.0                # Prędkość w osi X (m/s)
        self.vy = 0.0                # Prędkość w osi Y (m/s)
        
        # ----------------- PARAMETRY WASZEGO DRONA -----------------
        self.max_airspeed = 12.0     # Maksymalna prędkość drona w powietrzu (m/s)
        self.safe_reserve = 15.0     # Procent baterii na lądowanie awaryjne (%)
        # -----------------------------------------------------------

        # Subskrypcja Baterii
        self.battery_sub = self.create_subscription(
            BatteryStatus, '/fmu/out/battery_status_v1', self.battery_callback, qos_profile)
            
        # Subskrypcja Pozycji i Prędkości lokalnej (Zmień nazwę tematu jeśli grep pokazał inaczej!)
        self.position_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position_v1', self.position_callback, qos_profile)
            
        # Timer uruchamiający algorytm kalkulacji co 1 sekundę
        self.timer = self.create_timer(1.0, self.calculate_point_of_no_return)
        self.get_logger().info('Mózg nawigacyjny AeroShepherd (PoNR) gotowy!')

    def battery_callback(self, msg):
        self.battery_pct = msg.remaining

    def position_callback(self, msg):
        self.drone_x = msg.x
        self.drone_y = msg.y
        self.drone_z = msg.z  # W NED: -msg.z daje realną wysokość nad ziemią
        self.vx = msg.vx
        self.vy = msg.vy

    def calculate_point_of_no_return(self):
        # 1. Obliczamy odległość od bazy (0,0) za pomocą pitagorasa
        distance_to_home = math.sqrt(self.drone_x**2 + self.drone_y**2)
        
        # 2. Obliczamy aktualną prędkość nad ziemią (Ground Speed)
        ground_speed = math.sqrt(self.vx**2 + self.vy**2)
        
        # 3. ESTYMACJA WIATRU (Uproszczona):
        # Jeśli dron leci do bazy z prędkością maksymalną przez powietrze (max_airspeed),
        # a wiatr wieje mu w twarz, to jego prędkość powrotu spadnie.
        # Załóżmy pesymistyczny wariant, że wiatr wieje prosto w twarz w drodze powrotnej:
        estimated_wind_headwind = max(0.0, self.max_airspeed - ground_speed) if ground_speed > 0.1 else 0.0
        
        return_speed = self.max_airspeed - estimated_wind_headwind
        if return_speed <= 1.0: 
            return_speed = 1.0 # Zabezpieczenie przed dzieleniem przez zero przy huraganie
            
        # 4. Obliczamy czas potrzebny na powrót do bazy (w sekundach)
        time_to_return = distance_to_home / return_speed
        
        # 5. Dynamiczne wyliczenie progu baterii potrzebnego na powrót
        # Przyjmujemy założenie (do kalibracji), że 100% baterii starcza na 1200 sekund (20 minut) lotu.
        # Pobór prądu rośnie, jeśli dron leci pod wiatr (zwiększamy zapotrzebowanie)
        estimated_battery_drain_per_sec = 1.0 / 1200.0
        if estimated_wind_headwind > 0:
            estimated_battery_drain_per_sec *= (1.0 + (estimated_wind_headwind / self.max_airspeed))

        battery_needed_for_flight = (time_to_return * estimated_battery_drain_per_sec) * 100.0
        
        # Całkowity wymagany próg powrotu = potrzebna bateria + rezerwa bezpieczeństwa
        ponr_threshold = battery_needed_for_flight + self.safe_reserve
        
        # Aktualny stan baterii w procentach
        current_battery_procent = self.battery_pct * 100
        
        # Wyświetlanie raportu
        self.get_logger().info(
            f'Dystans: {distance_to_home:.1f}m | Bateria: {current_battery_procent:.1f}% | '
            f'Wymagany powrót przy: {ponr_threshold:.1f}%'
        )
        
        # Decyzja algorytmu o natychmiastowym przerwaniu misji
        if current_battery_procent <= ponr_threshold:
            self.get_logger().error(
                f'!!! KRYTYCZNY PUNKT BEZPOWROTU OSIĄGNIĘTY !!! '
                f'Wracaj do bazy! Potrzebujesz {ponr_threshold:.1f}%, masz {current_battery_procent:.1f}%'
            )

def main(args=None):
    rclpy.init(args=args)
    node = PonrEstimator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()