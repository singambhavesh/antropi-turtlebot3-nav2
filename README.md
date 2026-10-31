# TurtleBot3 Autonomous Navigation Demo

ROS 2 Humble / Nav2 demonstration for the **Antropi Robotics Software Intern Assignment**.

---

## Objective

Set up a **TurtleBot3 robot in Gazebo** with the **ROS 2 Navigation2 (Nav2) stack** and demonstrate autonomous navigation in an environment with obstacles.

- **Demo Video:** [`antropi_turtlebot3_nav2_demo.mp4`](antropi_turtlebot3_nav2_demo.mp4) (Full HD 1080p, 65s recording of Gazebo, RViz, and terminal)
- **Robot:** TurtleBot3 Burger
- **Simulator:** Gazebo Classic 11 (`gazebo_ros`)
- **Navigation Stack:** Nav2 (Humble release) — AMCL localization, Navfn global planner, DWB local controller, and Behavior Tree navigator
- **Environment:** Gazebo world with walls and obstacles (`antropi_nav.world`)

---

## Tested Environment

| Component | Version / Specification |
|-----------|-------------------------|
| OS | Ubuntu 22.04 LTS (WSL2 on Windows 11) |
| ROS | ROS 2 Humble Hawksbill |
| Simulator | Gazebo Classic 11.10.2 (via `gazebo_ros`) |
| Robot Model | TurtleBot3 Burger (`TURTLEBOT3_MODEL=burger`) |
| Navigation | Nav2 (Humble release 1.1.20) |
| GUI / Display | WSLg (`DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`) |

---

## Quick Start Guide

### 1. Install Dependencies

In your Ubuntu 22.04 terminal:

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install -y \
  ros-humble-turtlebot3 \
  ros-humble-turtlebot3-gazebo \
  ros-humble-turtlebot3-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-navigation2 \
  ros-humble-xacro \
  ros-humble-rviz2
```

Configure the default robot model in your `~/.bashrc`:

```bash
echo 'export TURTLEBOT3_MODEL=burger' >> ~/.bashrc
source ~/.bashrc
```

---

### 2. Build the Workspace

```bash
cd ros_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

---

### 3. Run the Demo

You can run the demo in either of two ways:

#### Option A: Recommended for WSL2 & Screen Recording (Two Terminals)

Running in two terminals lets Gazebo load models and initialize physics first before starting Nav2 and RViz.

**Terminal 1 — Launch Gazebo Simulation:**
```bash
source /opt/ros/humble/setup.bash
source ros_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch antropi_nav_demo gazebo.launch.py
```
*Wait ~5–10 seconds until Gazebo opens and the robot appears in the world.*

**Terminal 2 — Launch Nav2 & RViz:**
```bash
source /opt/ros/humble/setup.bash
source ros_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch antropi_nav_demo navigation.launch.py
```
*RViz will open with the costmap, laser scan, map, and robot model loaded.*

#### Option B: Single Command Launch
```bash
source /opt/ros/humble/setup.bash
source ros_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger
ros2 launch antropi_nav_demo demo.launch.py
```
*(This automatically launches Gazebo and delays Nav2 startup to allow the simulation clock and transforms to stabilize).*

---

### 4. Sending Navigation Goals

You can command the robot either interactively through RViz or via the terminal:

#### Method 1: Using the RViz GUI
1. **Initial Pose:** The package pre-configures AMCL to the robot's spawn pose `(x: -2.0, y: -0.5, yaw: 0.0)`. You will see the yellow particle cloud already converged around the robot. You can also re-initialize it at any time using the **2D Pose Estimate** button.
2. **Set Goal:** Click the **Nav2 Goal** button on the RViz top toolbar, then click and drag on a target position in free space across the obstacle course (e.g., top-right area around `x=0.5, y=0.5`).
3. The global path (green line) is computed immediately, the local costmap updates with laser returns, and the local path (blue line) guides the robot around obstacles.

#### Method 2: Using the Included CLI Script
In a new terminal:
```bash
source /opt/ros/humble/setup.bash
source ros_ws/install/setup.bash
ros2 run antropi_nav_demo send_goal --x 0.5 --y 0.5 --yaw 0.0
```
This sends the goal directly via Nav2 action client and logs live progress and remaining distance until success.

---

## Project Structure

```
ros_ws/src/antropi_nav_demo/
├── antropi_nav_demo/
│   ├── __init__.py
│   └── send_goal.py           # CLI script to send navigation goals via action client
├── config/
│   └── nav2_params.yaml       # Nav2 parameters (AMCL, Navfn, DWB, Costmaps, Lifecycles)
├── launch/
│   ├── demo.launch.py         # Full startup (Gazebo + delayed Nav2 + RViz)
│   ├── gazebo.launch.py       # Gazebo Classic + robot_state_publisher
│   └── navigation.launch.py   # Nav2 bringup stack + RViz2
├── maps/
│   ├── map.yaml               # Occupancy grid metadata
│   └── map.pgm                # Occupancy grid map image
├── rviz/
│   └── nav_demo.rviz          # Preconfigured RViz display profile
├── worlds/
│   └── antropi_nav.world      # Gazebo world with TurtleBot3 and obstacles
├── package.xml
├── setup.py
└── setup.cfg
```

---

## Screen Recording Guide (1–2 Minutes)

For the assignment submission video:

1. **Arrange Windows Side-by-Side:** Place Gazebo on the left half of your screen and RViz on the right half. Keep a small terminal visible at the bottom.
2. **Start Recording:** Press `Win + Alt + R` (Windows Xbox Game Bar) or `Win + Shift + R` (Snipping Tool Screen Recorder).
3. **Key Moments to Capture:**
   - Launching the demo.
   - Gazebo showing the TurtleBot3 Burger in the obstacle world.
   - RViz displaying the map, laser scan points (`/scan`), costmaps, and robot footprint.
   - Issuing a navigation goal requiring the robot to turn around a central obstacle.
   - The robot smoothly negotiating the turn, dynamically updating the local costmap, avoiding obstacles, and arriving at the goal pose.
4. Stop recording and save the `.mp4` file.

---

## Submission Form Q&A

Use these detailed answers for the Antropi Robotics internship submission form:

### 1. What was your technical approach to this exercise?
> "I developed a clean, modular ROS 2 Humble package (`antropi_nav_demo`) configured for the TurtleBot3 Burger robot. The solution integrates Gazebo Classic via `gazebo_ros` with the standard Nav2 bringup stack. AMCL is utilized for probabilistic Monte Carlo localization against a 2D occupancy grid map, initialized at the known spawn pose (`x: -2.0, y: -0.5`). 
> 
> Global trajectory planning is executed using `nav2_navfn_planner` (Dijkstra/A*), which searches the global costmap for an optimal obstacle-free route. Local trajectory execution and collision avoidance are handled by `dwb_core::DWBLocalPlanner` (Dynamic Window Approach), which continuously samples velocity trajectories and scores them against obstacle clearance, path alignment, and goal distance. Both global and local costmaps combine static map information and real-time 2D LiDAR raytracing (`/scan`) through inflation layers to safely navigate around obstacles."

### 2. What challenges did you encounter, and how did you resolve them?
> - **ROS 2 Simulation Ecosystem Compatibility:** Humble supports both Gazebo Classic (`gazebo_ros`) and newer Gazebo Sim/Fortress (`ros_gz_bridge`). The official TurtleBot3 Humble plugins and URDFs target Gazebo Classic. After verifying package dependencies and plugin compatibility, Gazebo Classic 11 was selected to ensure full sensor integration (`/scan`, `/odom`, `/imu`) without protocol bridging overhead.
> - **WSL2 / Windows Filesystem Path Delimiters:** In WSL environments where repositories sit on mounted Windows paths with spaces (e.g., OneDrive or user documents), Gazebo Classic's command-line parser can misinterpret path arguments. This was resolved by ensuring clean package share discovery through ROS 2 launch substitutions and colcon standard build structures.
> - **Lifecycle Startup Sequencing & TF Timing:** Nav2 requires a continuous and synchronized transform tree (`map → odom → base_footprint → base_link → base_scan`) and clock synchronization (`use_sim_time: true`). If Nav2 starts before Gazebo's diff-drive plugin publishes odometry, lifecycle nodes can time out. To solve this, the launch pipeline decouples simulation bringup from Nav2 stack activation, ensuring all TF frames and topics are active before invoking the navigation lifecycle manager.

### 3. What were your key learnings from this exercise?
> - **Nav2 Lifecycle State Machine:** Gained hands-on experience with ROS 2 managed lifecycle nodes (`unconfigured → inactive → active`), bond connections, and how the Nav2 Lifecycle Manager orchestrates node transitions deterministically.
> - **Costmap Layering & DWB Tuning:** Learned how costmap inflation radius and cost scaling factors impact robot behavior—balancing aggressive clearance around corners with the ability to traverse narrow passages.
> - **Decoupled Architecture:** Experienced the architectural modularity of ROS 2 and Nav2: standard components (planners, controllers, costmaps, behavior trees) can be integrated seamlessly without rewriting core navigation algorithms."

---

## Troubleshooting Reference

| Symptom | Probable Cause | Resolution |
|---------|----------------|------------|
| No `/scan` topic | `TURTLEBOT3_MODEL` unset | Run `export TURTLEBOT3_MODEL=burger` and check `ros2 topic list` |
| Robot doesn't move | Missing initial localization | Verify AMCL particle cloud in RViz; check `/cmd_vel` output |
| Goal rejected | Goal placed inside obstacle inflation | Select a goal in clear white space on the map |
| TF Transform timeout | Clock mismatch | Ensure `use_sim_time: true` is passed to all nodes |
| Blank RViz window | WSLg display error | Confirm WSLg operates with `glxgears` or check `DISPLAY=:0` |

---

## License

Apache-2.0
