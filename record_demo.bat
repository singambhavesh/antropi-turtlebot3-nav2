@echo off
setlocal enabledelayedexpansion

title Antropi Nav2 Demo - Screen Recorder

echo ======================================================================
echo    ANTROPI ROBOTICS INTERN ASSIGNMENT - DEMO VIDEO RECORDER
echo ======================================================================
echo.
echo This tool records your desktop while TurtleBot3 autonomously navigates
echo through the obstacle course using ROS 2 Humble Navigation2 (Nav2).
echo.
echo Output file: antropi_nav2_demo.mp4
echo.
echo Steps:
echo   1. FFmpeg will start recording your screen.
echo   2. Gazebo and RViz will launch in WSL2.
echo   3. Once Nav2 is active, an autonomous goal is automatically sent.
echo   4. When the robot reaches the goal, press 'q' in this window to save.
echo.
echo TIP: You can also record anytime using Windows shortcut: Win + Shift + R
echo.
pause

set FFMPEG_BIN=C:\Users\admin\miniconda3\envs\dl_fea\Library\bin\ffmpeg.exe

if not exist "!FFMPEG_BIN!" (
    echo Error: FFmpeg binary not found at !FFMPEG_BIN!
    echo Please use Windows Screen Recorder instead: Press Win + Shift + R
    pause
    exit /b 1
)

echo.
echo [1/3] Starting background screen capture to antropi_nav2_demo.mp4...
start "FFmpeg Recorder" "!FFMPEG_BIN!" -f gdigrab -framerate 25 -i desktop -c:v libx264 -preset ultrafast -pix_fmt yuv420p -y antropi_nav2_demo.mp4

echo.
echo [2/3] Launching Gazebo and Nav2 in WSL2...
wsl -d Ubuntu-22.04 -- bash -c "source /opt/ros/humble/setup.bash && source '/mnt/c/Users/admin/OneDrive - Amrita vishwa vidyapeetham/Documents/Amtropic Assignmennt/ros_ws/install/setup.bash' && export TURTLEBOT3_MODEL=burger && ros2 launch antropi_nav_demo demo.launch.py"

echo.
echo [3/3] Demo finished. Please switch to the FFmpeg window and press 'q' to stop recording.
echo Your video will be saved as antropi_nav2_demo.mp4 in this folder.
pause
