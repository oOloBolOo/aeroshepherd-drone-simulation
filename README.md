# AeroShepherd - Autonomous Drone Simulation Ecosystem

Autonomiczny system bsk (drona) zintegrowany z robotycznym systemem operacyjnym **ROS 2 (Jazzy)** oraz środowiskiem symulacyjnym **Gazebo Sim (Harmonic)**, wykorzystujący autopilota **PX4 Autopilot** (SITL) do zadań rolnictwa precyzyjnego i monitorowania dużego inwentarza żywego.

## 🚀 Główne Funkcjonalności
* **Pełna automatyzacja uruchamiania:** Autorski skrypt bash zarządza procesami, wątkami, czyszczeniem pamięci oraz asynchronicznym wstawaniem agenta Micro-XRCE-DDS, stacji QGroundControl i węzłów ROS 2.
* **Optymalizacja sprzętowa:** Integracja renderowania symulacji OGRE 2 z dedykowanymi kartami NVIDIA (PRIME offload) eliminująca latencję strumieni wideo.
* **Dynamiczne generowanie środowiska:** Skrypt Python generujący populację obiektów testowych (stado) z losowym rozkładem współrzędnych i parametrów wizualnych w plikach `.sdf`.
* **Dedykowany podsystem wizyjny:** Integracja sensorów wizualnych pod kadłubem platformy, przygotowana pod implementację algorytmów detekcji obiektów w czasie rzeczywistym (YOLOv8).

## 📂 Struktura Projektu
* `/scripts` - Skrypty automatyzujące uruchamianie ekosystemu oraz generatory świata.
* `/gazebo_assets` - Pliki światów `.sdf` oraz autorskie modyfikacje modeli platform latających.
* `/ros2_nodes` - Autorskie pakiety i węzły ROS 2 (zarządzanie danymi z drona, telemetryka).

## 🛠️ Stack Techniczny
* **OS:** Ubuntu 24.04 LTS
* **Middleware / Software:** ROS 2 (Jazzy Jalisco), PX4 Autopilot (SITL), Gazebo Sim, QGroundControl
