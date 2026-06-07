#!/bin/bash

# Kolory dla czystego i profesjonalnego feedbacku w konsoli
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}🧹 [AeroShepherd] Czyszczenie środowiska z procesów w tle...${NC}"
pkill -f gz
pkill -f px4
pkill -f MicroXRCEAgent
pkill -f ros_gz_bridge
pkill -f rqt_image_view
sleep 1.5
echo -e "${GREEN}✅ Środowisko gotowe do pracy.${NC}"

echo -e "${CYAN}🚀 Uruchamianie zintegrowanego ekosystemu drona...${NC}"

# 1. Główny proces: Oficjalny i czysty start celu gz_aeroshepherd na karcie NVIDIA
gnome-terminal --title="🛸 1. PX4 SITL & Gazebo" -- bash -c "
  echo -e '${GREEN}▶ Kompilacja i uruchamianie dedykowanego celu AeroShepherd...${NC}';
  cd ~/PX4-Autopilot && __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia PX4_GZ_WORLD=aeroshepherd PX4_GZ_POSE="0,0,0.5,0,0,0" make px4_sitl gz_aeroshepherd;
  exec bash" &

sleep 1

# 2. Agent DDS
gnome-terminal --tab --title="📡 2. Micro-XRCE-DDS Agent" -- bash -c "
  echo -e '${YELLOW}⏳ Oczekiwanie na inicjalizację portów PX4...${NC}';
  sleep 5;
  echo -e '${GREEN}▶ Uruchamianie Agenta DDS...${NC}';
  cd ~/Micro-XRCE-DDS-Agent/build && ./MicroXRCEAgent udp4 -p 8888;
  exec bash" &

# 3. QGroundControl (Z automatycznym nadawaniem praw wykonywalności)
gnome-terminal --tab --title="🗺️ 3. QGroundControl" -- bash -c "
  echo -e '${YELLOW}⏳ Oczekiwanie na stabilizację silnika fizycznego...${NC}';
  sleep 7;
  echo -e '${GREEN}▶ Uruchamianie stacji naziemnej QGC...${NC}';
  if [ -f ~/QGroundControl.AppImage ]; then 
    chmod +x ~/QGroundControl.AppImage && ~/QGroundControl.AppImage; 
  else 
    chmod +x ./QGroundControl.AppImage && ./QGroundControl.AppImage; 
  fi;
  exec bash" &

# 4. Logika i monitorowanie w ROS 2
gnome-terminal --tab --title="📊 4. ROS 2 Monitor" -- bash -c "
  echo -e '${YELLOW}⏳ Sourcing środowiska i restart daemona ROS 2...${NC}';
  sleep 9;
  source /opt/ros/jazzy/setup.bash && source ~/ros2_ws/install/setup.bash;
  ros2 daemon stop && ros2 daemon start;
  echo -e '${GREEN}▶ Uruchamianie węzła monitorowania baterii...${NC}';
  ros2 run aeroshepherd battery_monitor;
  exec bash" &

# 5. Podwójny stabilny mostek wideo (RGB + Thermal)
gnome-terminal --tab --title="🎥 5. Ros Gz Bridges" -- bash -c "
  echo -e '${YELLOW}⏳ Oczekiwanie na inicjalizację sensorów optycznych...${NC}';
  sleep 9;
  source /opt/ros/jazzy/setup.bash;
  echo -e '${GREEN}▶ Uruchamianie mostka kamery RGB...${NC}';
  ros2 run ros_gz_bridge parameter_bridge /world/aeroshepherd/model/aeroshepherd_0/link/base_link/sensor/camera_sensor/image@sensor_msgs/msg/Image[gz.msgs.Image &
  echo -e '${GREEN}▶ Uruchamianie mostka kamery TERMOWIZYJNEJ...${NC}';
  ros2 run ros_gz_bridge parameter_bridge /world/aeroshepherd/model/aeroshepherd_0/link/base_link/sensor/thermal_camera/image@sensor_msgs/msg/Image[gz.msgs.Image;
  exec bash" &

# 6. Autorski wielospektralny węzeł analityczny YOLOv8
gnome-terminal --tab --title="📺 6. AeroShepherd Dual-Vision Live" -- bash -c "
  echo -e '${YELLOW}⏳ Oczekiwanie na strumienie danych...${NC}';
  sleep 12;
  source /opt/ros/jazzy/setup.bash && source ~/ros2_ws/install/setup.bash;
  echo -e '${GREEN}▶ Odpalanie zsynchronizowanego podglądu wizji (RGB + IR)...${NC}';
  python3 ~/ros2_ws/src/aeroshepherd/aeroshepherd/thermal_vision.py;
  exec bash"
  
echo -e "${GREEN}✨ Wszystkie zakładki zostały pomyślnie wpięte do okna roboczego!${NC}"