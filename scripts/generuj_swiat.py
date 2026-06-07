import random
import os

# --- KONFIGURACJA OPTYMALIZACJI ---
LICZBA_KROW = 50  
ZAKRES_X = (6.0, 60.0)    
ZAKRES_Y = (-35.0, 35.0)  

SCIEZKA_SWIATA = os.path.expanduser("~/PX4-Autopilot/Tools/simulation/gz/worlds/aeroshepherd.sdf")

# Paleta kolorów dająca świetny kontrast w termowizji
KOLORY = [
    (0.3, 0.2, 0.1, 1.0),   
    (0.4, 0.25, 0.15, 1.0), 
    (0.15, 0.15, 0.15, 1.0) 
]

def generuj_swiat():
    # NAGŁÓWEK: Twoja super szybka fizyka + właściwa nazwa świata pod spawner PX4
    naglowek = """<?xml version="1.0" encoding="UTF-8"?>
<sdf version="1.9">
  <world name="aeroshepherd">
    <physics type="ode">
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>250</real_time_update_rate>
      <gravity>0 0 -9.8</gravity>
    </physics>
    
    <atmosphere type="adiabatic"/>
    <scene>
      <grid>false</grid>
      <ambient>0.7 0.7 0.7 1</ambient>
      <background>0.5 0.7 0.9 1</background>
      <shadows>true</shadows>
      <fog><type>linear</type><color>0.7 0.8 0.85 1</color><start>10.0</start><end>100.0</end></fog>
    </scene>

    <light type="directional" name="sunUTC">
      <cast_shadows>true</cast_shadows>
      <diffuse>0.9 0.9 0.9 1</diffuse>
      <specular>0.2 0.2 0.2 1</specular>
      <direction>0.001 0.625 -0.78</direction>
      <pose>0 0 500 0 0 0</pose>
    </light>

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

    <spherical_coordinates>
      <surface_model>EARTH_WGS84</surface_model>
      <world_frame_orientation>ENU</world_frame_orientation>
      <latitude_deg>47.397971057728974</latitude_deg>
      <longitude_deg>8.546163739800146</longitude_deg>
      <elevation>0</elevation>
    </spherical_coordinates>

    <model name="stado_krow">
      <static>true</static>
      <plugin filename="gz-sim-thermal-system" name="gz::sim::systems::Thermal">
        <temperature>310.15</temperature>
      </plugin>
"""

    krowy_xml = ""
    for i in range(1, LICZBA_KROW + 1):
        x = round(random.uniform(*ZAKRES_X), 1)
        y = round(random.uniform(*ZAKRES_Y), 1)
        rot = round(random.uniform(-3.14, 3.14), 2)
        
        r, g, b, alpha = KOLORY[i % len(KOLORY)]
        
        # Brak kolizji i inercji = zero obciążenia dla serwera Gazebo
        krowy_xml += f"""
      <link name="krowa_{i}">
        <pose>{x} {y} 0.5 0 0 {rot}</pose>
        <visual name="visual_{i}">
          <geometry>
            <box><size>1.4 0.6 1.0</size></box>
          </geometry>
          <material>
            <ambient>{r:.2f} {g:.2f} {b:.2f} {alpha}</ambient>
            <diffuse>{r:.2f} {g:.2f} {b:.2f} {alpha}</diffuse>
          </material>
        </visual>
      </link>"""

    stopka = """
    </model>
  </world>
</sdf>
"""

    xml_final = naglowek + krowy_xml + stopka
    
    try:
        with open(SCIEZKA_SWIATA, "w") as f:
            f.write(xml_final)
        print("✅ Świat został pomyślnie nadpisany stabilną i zoptymalizowaną strukturą.")
    except Exception as e:
        print(f"❌ Błąd zapisu: {e}")

if __name__ == "__main__":
    generuj_swiat()