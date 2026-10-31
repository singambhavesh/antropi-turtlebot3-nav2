#!/usr/bin/env bash
# Antropi Robotics Intern Assignment - One-Click Demo Launcher
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="${SCRIPT_DIR}/ros_ws"

echo "=========================================================="
echo " Starting TurtleBot3 Nav2 Autonomous Navigation Demo"
echo "=========================================================="

source /opt/ros/humble/setup.bash

if [ -f "${WS_DIR}/install/setup.bash" ]; then
    source "${WS_DIR}/install/setup.bash"
else
    echo "Building workspace first..."
    cd "${WS_DIR}"
    colcon build --symlink-install
    source install/setup.bash
    cd "${SCRIPT_DIR}"
fi

export TURTLEBOT3_MODEL=burger
echo "TURTLEBOT3_MODEL set to: ${TURTLEBOT3_MODEL}"
echo ""
echo "Launching Gazebo + Nav2 + RViz..."
echo "Tip: Arrange Gazebo on the left and RViz on the right for recording."
echo "=========================================================="

ros2 launch antropi_nav_demo demo.launch.py
