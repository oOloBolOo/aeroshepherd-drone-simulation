# AeroShepherd - Autonomous Drone Simulation Ecosystem

Autonomiczny system bsk (drona) zintegrowany z robotycznym systemem operacyjnym ROS 2 (Jazzy) oraz środowiskiem symulacyjnym Gazebo Sim (Harmonic), wykorzystujący autopilota PX4 Autopilot (SITL) do zadań rolnictwa precyzyjnego i monitorowania dużego inwentarza żywego.

## Główne Funkcjonalności
* Pełna automatyzacja uruchamiania: Autorski skrypt bash zarządza procesami, wątkami, czyszczeniem pamięci oraz asynchronicznym wstawaniem agenta Micro-XRCE-DDS, stacji QGroundControl i węzłów ROS 2.
* Optymalizacja sprzętowa: Integracja renderowania symulacji OGRE 2 z dedykowanymi kartami NVIDIA (PRIME offload) eliminująca latencję strumieni wideo.
* Dynamiczne generowanie środowiska: Skrypt Python generujący populację obiektów testowych (stado) z losowym rozkładem współrzędnych i parametrów wizualnych w plikach `.sdf`.
* Dedykowany podsystem wizyjny: Integracja sensorów wizualnych pod kadłubem platformy, przygotowana pod implementację algorytmów detekcji obiektów w czasie rzeczywistym (YOLOv8).

## Struktura Projektu
* `/scripts` - Skrypty automatyzujące uruchamianie ekosystemu oraz generatory świata.
* `/gazebo_assets` - Pliki światów `.sdf` oraz autorskie modyfikacje modeli platform latających.
* `/ros2_nodes` - Autorskie pakiety i węzły ROS 2 (zarządzanie danymi z drona, telemetria).

## Instrukcja uruchomienia

### 1. Wymagania systemowe
* Linux Ubuntu 24.04 LTS
* ROS 2 Jazzy Jalisco
* Gazebo Sim (v1.9 / Harmonic)
* PX4 Autopilot (SITL) wraz z aktywnym mostem uXRCE-DDS

### 2. Instalacja zależności
```bash
# Pakiety systemowe i kompilatory
sudo apt update && sudo apt install -y build-essential python3-dev python3-pip python3-colcon-common-extensions

# Biblioteki wizyjne i AI
pip install ultralytics opencv-python lapx --break-system-packages
```

### 3. Przygotowanie przestrzeni roboczej

Sklonowanie repozytorium do przestrzeni roboczej ROS 2 (np. `~/ros2_ws/src/`) i kompilacja pakietów:
```bash
# Przejście do workspace i budowanie na czysto
cd ~/ros2_ws
rm -rf build/aeroshepherd/ install/aeroshepherd/

# Kompilacja z użyciem linków symbolicznych dla Pythona
colcon build --symlink-install
```

### 4. Uruchomienie symulacji

```bash
chmod +x ~/aeroshepherd_project/scripts/start_aeroshepherd.sh
~/aeroshepherd_project/scripts/start_aeroshepherd.sh
```
