import random
import os

# --- KONFIGURACJA OPTYMALIZACJI ---
LICZBA_KROW = 50  
ZAKRES_X = (6.0, 60.0)    
ZAKRES_Y = (-35.0, 35.0)  

SCIEZKA_SWIATA = os.path.expanduser("~/PX4-Autopilot/Tools/simulation/gz/worlds/aeroshepherd.sdf")

KOLORY = [
    (0.3, 0.2, 0.1, 1.0),   
    (0.4, 0.25, 0.15, 1.0), 
    (0.15, 0.15, 0.15, 1.0) 
]

def generuj_swiat():
    # NAGŁÓWEK: Kompletny zestaw pluginów rdzenia Gazebo + sensory wymagane przez PX4
    naglowek = """<?xml version="1.0" encoding="UTF-8"?>
<sdf version="1.9">
  <world name="aeroshepherd">
    <physics type="ode">
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>250</real_time_update_rate>
    </physics>

    <gravity>0 0 -9.81</gravity>
    <magnetic_field>6e-06 2.3e-05 -4.2e-05</magnetic_field>

    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>

    <plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"/>
    <plugin filename="gz-sim-magnetometer-system" name="gz::sim::systems::Magnetometer"/>
    <plugin filename="gz-sim-air-pressure-system" name="gz::sim::systems::AirPressure"/>
    <plugin filename="gz-sim-navsat-system" name="gz::sim::systems::NavSat"/>

    <atmosphere type="adiabatic">
      <temperature>288.15</temperature> </atmosphere>

    <scene>
      <grid>false</grid>
      <ambient>0.7 0.7 0.7 1</ambient>
      <background>0.5 0.7 0.9 1</background>
      <shadows>true</shadows>
      <fog><type>linear</type><color>0.7 0.8 0.85 1</color><start>10.0</start><end>100.0</end></fog>
    </scene>

    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>200 200</size></plane></geometry>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>200 200</size></plane></geometry>
          <material>
            <ambient>0.2 0.4 0.15 1</ambient>
            <diffuse>0.25 0.45 0.17 1</diffuse>
          </material>
        </visual>
      </link>
    </model>

    <light name="sunUTC" type="directional">
      <pose>0 0 500 0 -0 0</pose>
      <cast_shadows>true</cast_shadows>
      <intensity>1</intensity>
      <direction>0.001 0.625 -0.78</direction>
      <diffuse>0.904 0.904 0.904 1</diffuse>
    </light>

    <spherical_coordinates>
      <surface_model>EARTH_WGS84</surface_model>
      <world_frame_orientation>ENU</world_frame_orientation>
      <latitude_deg>47.397971057728974</latitude_deg>
      <longitude_deg>8.546163739800146</longitude_deg>
      <elevation>0</elevation>
    </spherical_coordinates>
"""

    krowy_xml = ""
    for i in range(1, LICZBA_KROW + 1):
        x = round(random.uniform(*ZAKRES_X), 1)
        y = round(random.uniform(*ZAKRES_Y), 1)
        rot = round(random.uniform(-3.14, 3.14), 2)
        r, g, b, alpha = KOLORY[i % len(KOLORY)]
        
        # JEDYNA POPRAWNA STRUKTURA: Plugin Thermal siedzi twardo wewnątrz znacznika <visual>
        krowy_xml += f"""
    <model name="krowa_{i}">
      <static>true</static>
      <pose>{x} {y} 0.5 0 0 {rot}</pose>
      <link name="link">
        <visual name="visual">
          <geometry><box><size>1.4 0.6 1.0</size></box></geometry>
          <material>
            <ambient>{r:.2f} {g:.2f} {b:.2f} {alpha}</ambient>
            <diffuse>{r:.2f} {g:.2f} {b:.2f} {alpha}</diffuse>
          </material>
          <plugin filename="gz-sim-thermal-system" name="gz::sim::systems::Thermal">
            <temperature>310.15</temperature> </plugin>
        </visual>
      </link>
    </model>"""

    stopka = "\n  </world>\n</sdf>\n"
    
    with open(SCIEZKA_SWIATA, "w") as f:
        f.write(naglowek + krowy_xml + stopka)
    print("✅ Wygenerowano kompletny, stabilny i w pełni sensoryczny świat SDF.")

if __name__ == "__main__":
    generuj_swiat()