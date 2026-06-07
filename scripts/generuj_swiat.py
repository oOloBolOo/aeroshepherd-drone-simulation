import random
import os

# --- KONFIGURACJA ---
LICZBA_KROW = 50  # <--- Tutaj wpisz, ile krów chcesz mieć na polu!
ZAKRES_X = (6.0, 60.0)    # Odległość przed dronem (metry)
ZAKRES_Y = (-35.0, 35.0)  # Szerokość pastwiska (lewo/prawo)

SCIEZKA_SWIATA = os.path.expanduser("~/PX4-Autopilot/Tools/simulation/gz/worlds/aeroshepherd.sdf")

# --- BAZOWY NAGŁÓWEK ŚWIATA (Visual, Niebo, Słońce, Geopozycja) ---
naglowek = """<?xml version="1.0" encoding="UTF-8"?>
<sdf version="1.9">
  <world name="aeroshepherd">
    <physics type="ode">
      <max_step_size>0.004</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>250</real_time_update_rate>
    </physics>
    <gravity>0 0 -9.8</gravity>
    <magnetic_field>6e-06 2.3e-05 -4.2e-05</magnetic_field>
    <atmosphere type="adiabatic"/>
    
    <scene>
      <grid>false</grid>
      <ambient>0.7 0.7 0.7 1</ambient>
      <background>0.5 0.7 0.9 1</background>
      <shadows>true</shadows>
      <sky>
        <clouds>
          <speed>12</speed>
          <ambient>0.8 0.8 0.8 1.0</ambient>
        </clouds>
      </sky>
      <fog>
        <color>0.7 0.8 0.85 1.0</color>
        <type>linear</type>
        <start>10.0</start>
        <end>100.0</end>
      </fog>
    </scene>

    <model name="ground_plane">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry><plane><normal>0 0 1</normal><size>200 200</size></plane></geometry>
          <surface><friction><ode/></friction><bounce/><contact/></surface>
        </collision>
        <visual name="visual">
          <geometry><plane><normal>0 0 1</normal><size>200 200</size></plane></geometry>
          <material>
            <ambient>0.22 0.40 0.15 1.0</ambient>
            <diffuse>0.25 0.45 0.17 1.0</diffuse>
            <specular>0.01 0.01 0.01 1.0</specular>
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
      <specular>0.271 0.271 0.271 1</specular>
      <attenuation>
        <range>2000</range><linear>0</linear><constant>1</constant><quadratic>0</quadratic>
      </attenuation>
    </light>

    <spherical_coordinates>
      <surface_model>EARTH_WGS84</surface_model>
      <world_frame_orientation>ENU</world_frame_orientation>
      <latitude_deg>47.397971057728974</latitude_deg>
      <longitude_deg>8.546163739800146</longitude_deg>
      <elevation>0</elevation>
    </spherical_coordinates>
"""

# --- GENEROWANIE STADA ---
krowy_xml = ""
for i in range(1, LICZBA_KROW + 1):
    x = round(random.uniform(*ZAKRES_X), 2)
    y = round(random.uniform(*ZAKRES_Y), 2)
    rot = round(random.uniform(-3.14, 3.14), 2)
    
    # Różnicowanie odcieni brązu/szarości dla realizmu wizualnego
    r = round(random.uniform(0.2, 0.5), 2)
    g = round(random.uniform(0.15, 0.35), 2)
    b = round(random.uniform(0.0, 0.15), 2)

    krowy_xml += f"""
    <model name="krowa_auto_{i}">
      <static>true</static>
      <pose>{x} {y} 0.5 0 0 {rot}</pose>
      <link name="link">
        <collision name="collision">
          <geometry><box><size>1.4 0.6 1.0</size></box></geometry>
        </collision>
        <visual name="body">
          <geometry><box><size>1.4 0.6 1.0</size></box></geometry>
          <material><ambient>{r} {g} {b} 1</ambient><diffuse>{r} {g} {b} 1</diffuse></material>
        </visual>
        <visual name="head">
          <pose>0.7 0 0.3 0 0 0</pose>
          <geometry><box><size>0.4 0.4 0.4</size></box></geometry>
          <material><ambient>0.1 0.1 0.1 1</ambient><diffuse>0.1 0.1 0.1 1</diffuse></material>
        </visual>
      </link>
    </model>"""

# --- ZAPIS KOMPLETNEGO PLIKU SDF ---
stopka = "\n  </world>\n</sdf>\n"

try:
    with open(SCIEZKA_SWIATA, "w") as f:
        f.write(naglowek + krowy_xml + stopka)
    print(f"✨ Sukces! Wygenerowano świat z {LICZBA_KROW} krowami bezpośrednio w pliku: {SCIEZKA_SWIATA}")
except Exception as e:
    print(f"❌ Błąd zapisu: {e}")