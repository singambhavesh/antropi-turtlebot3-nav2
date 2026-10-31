@echo off
title Antropi Nav2 Demo - Interactive Side-by-Side Launcher

echo ======================================================================
echo    ANTROPI ROBOTICS - TURTLEBOT3 NAV2 DEMO (SIDE-BY-SIDE)
echo ======================================================================
echo.
echo Launching Gazebo in Terminal 1...
start "Gazebo Simulation" cmd /k "wsl -d Ubuntu-22.04 -- bash -c \"source /opt/ros/humble/setup.bash && source '/mnt/c/Users/admin/OneDrive - Amrita vishwa vidyapeetham/Documents/Amtropic Assignmennt/ros_ws/install/setup.bash' && export TURTLEBOT3_MODEL=burger && ros2 launch antropi_nav_demo gazebo.launch.py\""

echo Waiting 10 seconds for Gazebo to spawn robot and start physics...
timeout /t 10 /nobreak >nul

echo Launching Nav2 + RViz in Terminal 2...
start "Nav2 and RViz" cmd /k "wsl -d Ubuntu-22.04 -- bash -c \"source /opt/ros/humble/setup.bash && source '/mnt/c/Users/admin/OneDrive - Amrita vishwa vidyapeetham/Documents/Amtropic Assignmennt/ros_ws/install/setup.bash' && export TURTLEBOT3_MODEL=burger && ros2 launch antropi_nav_demo navigation.launch.py\""

echo.
echo ======================================================================
echo Both Gazebo and RViz are opening!
echo.
echo 1. Put Gazebo on the LEFT half of your screen.
echo 2. Put RViz on the RIGHT half of your screen.
echo 3. Start your screen recording (Press: Win + Shift + R or Win + Alt + R).
echo.
echo When you are ready to send the navigation goal, press any key below...
echo ======================================================================
pause

echo.
echo Sending autonomous navigation goal to (x=0.5, y=0.5)...
wsl -d Ubuntu-22.04 -- bash -c "source /opt/ros/humble/setup.bash && source '/mnt/c/Users/admin/OneDrive - Amrita vishwa vidyapeetham/Documents/Amtropic Assignmennt/ros_ws/install/setup.bash' && ros2 run antropi_nav_demo send_goal --x 0.5 --y 0.5"

echo.
echo Goal completed! You can now stop your screen recording.
pause
