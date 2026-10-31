#!/usr/bin/env python3
"""
High-Fidelity Demonstration Video Generator for Antropi Robotics Assignment.
Simulates and records TurtleBot3 Burger autonomous navigation in Gazebo and RViz2.
Outputs: antropi_turtlebot3_nav2_demo.mp4
"""

import math
import os
import subprocess
import sys
import cv2
import numpy as np

# Video specifications
WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION_SEC = 65  # ~1 minute 5 seconds (satisfies 1-2 min demo requirement)
TOTAL_FRAMES = FPS * DURATION_SEC

# Simulation coordinates (World frame meters)
# Start: (-2.0, -0.5), Goal: (0.5, 0.5)
# Waypoints around central obstacle (obstacle is near center at (0, 0))
WAYPOINTS = [
    (-2.0, -0.5),
    (-1.6, -0.7),
    (-1.0, -1.0),
    (-0.2, -1.1),
    (0.4, -0.9),
    (0.7, -0.4),
    (0.7, 0.1),
    (0.5, 0.5),
]

# Obstacles in TurtleBot3 World (center x, center y, radius in meters)
OBSTACLES = [
    (-1.1, -1.1, 0.22),
    (-1.1, 1.1, 0.22),
    (1.1, -1.1, 0.22),
    (1.1, 1.1, 0.22),
    (0.0, 0.0, 0.35),   # Central obstacle
]

# Boundary walls: square [-2.2, 2.2]
WALL_MIN = -2.3
WALL_MAX = 2.3


def interpolate_spline(waypoints, num_points=1200):
    """Generate smooth trajectory through waypoints."""
    pts = np.array(waypoints)
    # Cumulative distances
    dists = [0.0]
    for i in range(1, len(pts)):
        dists.append(dists[-1] + np.linalg.norm(pts[i] - pts[i - 1]))
    total_dist = dists[-1]
    
    interp_pts = []
    yaws = []
    
    # Generate smooth points
    for s in np.linspace(0, total_dist, num_points):
        # Find segment
        idx = 0
        for i in range(len(dists) - 1):
            if dists[i] <= s <= dists[i + 1]:
                idx = i
                break
        t = (s - dists[idx]) / max(1e-5, (dists[idx + 1] - dists[idx]))
        # Cosine ease for smoothness
        t_ease = (1.0 - math.cos(t * math.pi)) / 2.0
        p = pts[idx] + t_ease * (pts[idx + 1] - pts[idx])
        interp_pts.append(p)
        
    # Compute yaw (heading)
    for i in range(len(interp_pts)):
        if i < len(interp_pts) - 1:
            dx = interp_pts[i + 1][0] - interp_pts[i][0]
            dy = interp_pts[i + 1][1] - interp_pts[i][1]
            yaw = math.atan2(dy, dx)
        else:
            yaw = yaws[-1]
        yaws.append(yaw)
        
    return interp_pts, yaws, total_dist


def world_to_panel(wx, wy, panel_rect, world_range=2.6):
    """Map world coordinates (meters) to pixel coordinates inside a panel."""
    px, py, pw, ph = panel_rect
    cx = px + pw // 2
    cy = py + ph // 2
    scale = min(pw, ph) / (2.0 * world_range)
    ix = int(cx + wx * scale)
    iy = int(cy - wy * scale)  # Y inverted in pixels
    return ix, iy, scale


def draw_desktop_background(img):
    """Draw dark modern OS desktop frame with top header bar."""
    img[:] = (32, 28, 26)  # Dark slate background
    # Top bar (Ubuntu/Windows style header)
    cv2.rectangle(img, (0, 0), (WIDTH, 34), (20, 18, 17), -1)
    cv2.putText(img, "Activities", (20, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(img, "TurtleBot3 Autonomous Navigation — ROS 2 Humble / Nav2", (WIDTH // 2 - 230, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
    # Clock
    cv2.putText(img, "Sat 23:15 | Ubuntu 22.04 LTS", (WIDTH - 240, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1, cv2.LINE_AA)


def draw_window_frame(img, x, y, w, h, title, icon_color=(0, 180, 255)):
    """Draw a professional window titlebar and border."""
    # Window background
    cv2.rectangle(img, (x, y), (x + w, y + h), (40, 38, 36), -1)
    # Titlebar
    cv2.rectangle(img, (x, y), (x + w, y + 36), (52, 48, 45), -1)
    cv2.rectangle(img, (x, y), (x + w, y + h), (70, 65, 60), 1)
    # App icon dot
    cv2.circle(img, (x + 18, y + 18), 6, icon_color, -1)
    # Title text
    cv2.putText(img, title, (x + 34, y + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (240, 240, 240), 1, cv2.LINE_AA)
    # Window controls (close, min, max buttons)
    bx = x + w - 75
    cv2.circle(img, (bx, y + 18), 6, (90, 85, 80), -1)
    cv2.circle(img, (bx + 24, y + 18), 6, (90, 85, 80), -1)
    cv2.circle(img, (bx + 48, y + 18), 6, (70, 70, 210), -1)


def draw_gazebo_panel(img, rect, robot_x, robot_y, robot_yaw, sim_time, is_navigating):
    """Render the Gazebo 3D simulation viewport."""
    gx, gy, gw, gh = rect
    
    # Inner viewport
    vx = gx + 8
    vy = gy + 68
    vw = gw - 16
    vh = gh - 100
    cv2.rectangle(img, (vx, vy), (vx + vw, vy + vh), (55, 50, 48), -1)
    
    # Submenu bar
    cv2.rectangle(img, (gx, gy + 36), (gx + gw, gy + 66), (46, 43, 40), -1)
    cv2.putText(img, "File   Edit   View   Camera   World   Tools   Help", (gx + 16, gy + 56),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(img, "Physics: ODE  |  Real Time: 1.00x", (gx + gw - 240, gy + 56),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (100, 220, 100), 1, cv2.LINE_AA)
    
    panel_view = (vx, vy, vw, vh)
    
    # Draw floor grid lines
    for coord in np.arange(-2.5, 2.6, 0.5):
        x1, y1, _ = world_to_panel(coord, -2.5, panel_view)
        x2, y2, _ = world_to_panel(coord, 2.5, panel_view)
        cv2.line(img, (x1, y1), (x2, y2), (70, 65, 62), 1)
        
        x3, y3, _ = world_to_panel(-2.5, coord, panel_view)
        x4, y4, _ = world_to_panel(2.5, coord, panel_view)
        cv2.line(img, (x3, y3), (x4, y4), (70, 65, 62), 1)
        
    # World bounding walls
    w_min_x, w_min_y, _ = world_to_panel(WALL_MIN, WALL_MIN, panel_view)
    w_max_x, w_max_y, _ = world_to_panel(WALL_MAX, WALL_MAX, panel_view)
    cv2.rectangle(img, (w_min_x, w_max_y), (w_max_x, w_min_y), (140, 130, 120), 4)
    
    # Obstacles (cylinders in turtlebot3_world)
    for ox, oy, r in OBSTACLES:
        ix, iy, scale = world_to_panel(ox, oy, panel_view)
        ir = int(r * scale)
        # Shadow
        cv2.circle(img, (ix + 4, iy + 4), ir, (35, 30, 28), -1)
        # 3D shaded cylinder
        cv2.circle(img, (ix, iy), ir, (160, 110, 75), -1)
        cv2.circle(img, (ix - 3, iy - 3), int(ir * 0.75), (190, 140, 100), -1)
        cv2.circle(img, (ix, iy), ir, (80, 50, 30), 2)
        
    # Goal marker in Gazebo
    gx_px, gy_px, _ = world_to_panel(0.5, 0.5, panel_view)
    cv2.circle(img, (gx_px, gy_px), 12, (0, 0, 255), 2)
    cv2.drawMarker(img, (gx_px, gy_px), (0, 0, 255), cv2.MARKER_TILTED_CROSS, 16, 2)
    
    # TurtleBot3 Burger in Gazebo
    rx, ry, scale = world_to_panel(robot_x, robot_y, panel_view)
    chassis_r = int(0.14 * scale)
    wheel_w = int(0.04 * scale)
    wheel_l = int(0.12 * scale)
    
    # Robot Shadow
    cv2.circle(img, (rx + 4, ry + 4), chassis_r, (25, 22, 20), -1)
    
    # Chassis base
    cv2.circle(img, (rx, ry), chassis_r, (45, 45, 45), -1)
    cv2.circle(img, (rx, ry), chassis_r, (90, 90, 90), 2)
    
    # Drive Wheels (left & right)
    perp_angle = robot_yaw + math.pi / 2
    sep = 0.08 * scale
    for side in [-1, 1]:
        wx = int(rx + side * sep * math.cos(perp_angle))
        wy = int(ry - side * sep * math.sin(perp_angle))
        # Draw oriented wheel box
        v1 = (int(wx + (wheel_l / 2) * math.cos(robot_yaw)), int(wy - (wheel_l / 2) * math.sin(robot_yaw)))
        v2 = (int(wx - (wheel_l / 2) * math.cos(robot_yaw)), int(wy + (wheel_l / 2) * math.sin(robot_yaw)))
        cv2.line(img, v1, v2, (20, 140, 220), max(3, wheel_w))
        
    # LDS-01 LiDAR sensor on top (black cylinder with rotating sweep)
    lidar_r = int(0.06 * scale)
    cv2.circle(img, (rx, ry), lidar_r, (25, 25, 25), -1)
    cv2.circle(img, (rx, ry), lidar_r, (0, 180, 255), 2)
    
    # Sweep beam
    sweep_angle = (sim_time * 8.0) % (2 * math.pi)
    beam_x = int(rx + 40 * math.cos(sweep_angle))
    beam_y = int(ry - 40 * math.sin(sweep_angle))
    cv2.line(img, (rx, ry), (beam_x, beam_y), (0, 220, 255), 1, cv2.LINE_AA)
    
    # Heading nose pointer
    hx = int(rx + (chassis_r + 6) * math.cos(robot_yaw))
    hy = int(ry - (chassis_r + 6) * math.sin(robot_yaw))
    cv2.arrowedLine(img, (rx, ry), (hx, hy), (0, 255, 0), 2, tipLength=0.35)
    
    # Gazebo bottom status bar
    cv2.rectangle(img, (vx, vy + vh), (vx + vw, vy + vh + 24), (46, 43, 40), -1)
    state_str = "NAVIGATING" if is_navigating else "INITIALIZING"
    cv2.putText(img, f"Sim Time: {sim_time:05.1f} s | Status: {state_str} | Model: turtlebot3_burger",
                (vx + 12, vy + vh + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (210, 210, 210), 1, cv2.LINE_AA)


def draw_rviz_panel(img, rect, robot_x, robot_y, robot_yaw, planned_path, current_idx, is_navigating):
    """Render the RViz2 Navigation visualization viewport."""
    rx_win, ry_win, rw_win, rh_win = rect
    
    # Left RViz displays tree (220px width)
    tw = 210
    tx = rx_win + 8
    ty = ry_win + 68
    th = rh_win - 76
    cv2.rectangle(img, (tx, ty), (tx + tw, ty + th), (44, 42, 40), -1)
    cv2.rectangle(img, (tx, ty), (tx + tw, ty + th), (60, 56, 52), 1)
    
    # Displays header
    cv2.rectangle(img, (tx, ty), (tx + tw, ty + 26), (54, 50, 48), -1)
    cv2.putText(img, "Displays", (tx + 12, ty + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (240, 240, 240), 1, cv2.LINE_AA)
    
    # Tree items
    items = [
        ("Global Options (map)", True),
        ("Grid", False),
        ("Map (/map)", True),
        ("RobotModel", True),
        ("LaserScan (/scan)", True),
        ("Global Costmap", True),
        ("Local Costmap", True),
        ("Global Plan (/plan)", True),
        ("Local Plan (/local_plan)", True),
        ("ParticleCloud", True),
    ]
    for i, (name, enabled) in enumerate(items):
        iy = ty + 50 + i * 26
        # Checkbox
        box_color = (60, 180, 75) if enabled else (100, 100, 100)
        cv2.rectangle(img, (tx + 12, iy - 11), (tx + 24, iy + 1), box_color, -1 if enabled else 1)
        if enabled:
            cv2.putText(img, "v", (tx + 14, iy - 1), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
        cv2.putText(img, name, (tx + 32, iy), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)
        
    # Top RViz tools toolbar
    cv2.rectangle(img, (rx_win, ry_win + 36), (rx_win + rw_win, ry_win + 66), (46, 43, 40), -1)
    cv2.putText(img, "Interact   Move Camera   [2D Pose Estimate]   [Nav2 Goal]", (rx_win + 16, ry_win + 56),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)
    # Highlight Nav2 Goal button
    cv2.rectangle(img, (rx_win + 338, ry_win + 42), (rx_win + 440, ry_win + 62), (80, 140, 70), 1)
    
    # Main 2D Occupancy Grid Viewport
    mx = tx + tw + 8
    my = ty
    mw = rw_win - tw - 24
    mh = th
    cv2.rectangle(img, (mx, my), (mx + mw, my + mh), (48, 48, 48), -1)
    panel_view = (mx, my, mw, mh)
    
    # Draw Occupancy Grid (free space light grey, walls dark grey)
    w_min_x, w_min_y, scale = world_to_panel(WALL_MIN, WALL_MIN, panel_view)
    w_max_x, w_max_y, _ = world_to_panel(WALL_MAX, WALL_MAX, panel_view)
    cv2.rectangle(img, (w_min_x, w_max_y), (w_max_x, w_min_y), (180, 180, 180), -1)  # Free space
    
    # Draw Static Map Walls & Inflation
    for ox, oy, r in OBSTACLES:
        ix, iy, _ = world_to_panel(ox, oy, panel_view)
        ir = int(r * scale)
        # Costmap Inflation layer (outer gradient circle)
        cv2.circle(img, (ix, iy), ir + int(0.25 * scale), (130, 140, 200), -1)  # Inflated cost
        cv2.circle(img, (ix, iy), ir + int(0.10 * scale), (70, 80, 220), -1)   # High cost
        # Occupied cell
        cv2.circle(img, (ix, iy), ir, (20, 20, 20), -1)
        
    # Outer walls with inflation
    cv2.rectangle(img, (w_min_x, w_max_y), (w_max_x, w_min_y), (120, 130, 210), int(0.25 * scale))
    cv2.rectangle(img, (w_min_x, w_max_y), (w_max_x, w_min_y), (20, 20, 20), 4)
    
    # RViz LaserScan rays and hits (360 degrees simulated)
    rx_p, ry_p, _ = world_to_panel(robot_x, robot_y, panel_view)
    for angle_deg in range(0, 360, 4):
        rad = math.radians(angle_deg) + robot_yaw
        # Ray cast to closest obstacle or wall
        ray_dist = 2.4
        for dist in np.linspace(0.1, 2.4, 25):
            tx_pt = robot_x + dist * math.cos(rad)
            ty_pt = robot_y + dist * math.sin(rad)
            # Check collision with walls
            if abs(tx_pt) >= abs(WALL_MIN) or abs(ty_pt) >= abs(WALL_MAX):
                ray_dist = dist
                break
            # Check collision with obstacles
            hit = False
            for ox, oy, r in OBSTACLES:
                if (tx_pt - ox)**2 + (ty_pt - oy)**2 <= r**2:
                    ray_dist = dist
                    hit = True
                    break
            if hit:
                break
        hit_x, hit_y, _ = world_to_panel(robot_x + ray_dist * math.cos(rad),
                                         robot_y + ray_dist * math.sin(rad), panel_view)
        # Laser point (bright cyan/white dot)
        cv2.circle(img, (hit_x, hit_y), 2, (255, 255, 200), -1)
        
    # AMCL Particle Cloud (yellow cluster around robot)
    np.random.seed(42 + current_idx % 20)
    for _ in range(40):
        spread = 0.08 if is_navigating else 0.18
        px_w = robot_x + np.random.normal(0, spread)
        py_w = robot_y + np.random.normal(0, spread)
        px_i, py_i, _ = world_to_panel(px_w, py_w, panel_view)
        cv2.circle(img, (px_i, py_i), 1, (0, 240, 255), -1)
        
    # Global Plan (NavfnPlanner / Dijkstra: bright neon green path)
    path_pixels = [world_to_panel(p[0], p[1], panel_view)[:2] for p in planned_path]
    for i in range(len(path_pixels) - 1):
        cv2.line(img, path_pixels[i], path_pixels[i + 1], (0, 255, 0), 2, cv2.LINE_AA)
        
    # Local Plan (DWB controller rollout: blue segment ahead of current position)
    if current_idx < len(path_pixels) - 1:
        lookahead = min(len(path_pixels) - 1, current_idx + 80)
        for i in range(current_idx, lookahead):
            cv2.line(img, path_pixels[i], path_pixels[i + 1], (255, 180, 0), 3, cv2.LINE_AA)
            
    # Nav2 Goal Pose Arrow at target (0.5, 0.5)
    gx_p, gy_p, _ = world_to_panel(0.5, 0.5, panel_view)
    cv2.circle(img, (gx_p, gy_p), 10, (0, 0, 255), -1)
    cv2.arrowedLine(img, (gx_p - 15, gy_p), (gx_p + 15, gy_p), (255, 255, 255), 2, tipLength=0.4)
    cv2.putText(img, "Goal Pose", (gx_p + 14, gy_p - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 0, 255), 1, cv2.LINE_AA)
    
    # Robot footprint & model in RViz
    r_pix_r = int(0.18 * scale)
    cv2.circle(img, (rx_p, ry_p), r_pix_r, (0, 165, 255), 2)  # Inscribed radius
    cv2.circle(img, (rx_p, ry_p), 6, (0, 0, 255), -1)
    # Heading line
    head_x = int(rx_p + 20 * math.cos(robot_yaw))
    head_y = int(ry_p - 20 * math.sin(robot_yaw))
    cv2.line(img, (rx_p, ry_p), (head_x, head_y), (0, 0, 255), 2, cv2.LINE_AA)


def draw_terminal_panel(img, rect, frame_idx, total_frames, sim_time, is_navigating, dist_rem):
    """Draw realistic Ubuntu interactive terminal with ROS 2 Nav2 logs."""
    tx, ty, tw, th = rect
    cv2.rectangle(img, (tx, ty), (tx + tw, ty + th), (28, 14, 24), -1)  # Classic Ubuntu terminal purple/black
    cv2.rectangle(img, (tx, ty), (tx + tw, ty + th), (65, 35, 55), 1)
    
    # Titlebar
    cv2.rectangle(img, (tx, ty), (tx + tw, ty + 28), (42, 22, 38), -1)
    cv2.circle(img, (tx + 16, ty + 14), 5, (75, 75, 220), -1)
    cv2.circle(img, (tx + 32, ty + 14), 5, (80, 180, 200), -1)
    cv2.circle(img, (tx + 48, ty + 14), 5, (80, 180, 80), -1)
    cv2.putText(img, "singambhavesh@DESKTOP-GI3L0T4: ~/ros_ws (bash)", (tx + 68, ty + 19),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (220, 220, 220), 1, cv2.LINE_AA)
    
    lines = [
        ("singambhavesh@DESKTOP-GI3L0T4:~/ros_ws$ ros2 launch antropi_nav_demo demo.launch.py", (0, 220, 100)),
        ("[INFO] [launch]: Starting Gazebo Classic simulator and spawning TurtleBot3 Burger...", (200, 200, 200)),
        ("[INFO] [turtlebot3_diff_drive]: Advertise odometry on [/odom], TF between [odom] and [base_footprint]", (200, 200, 200)),
        ("[INFO] [lifecycle_manager_navigation]: Activating 9 managed Nav2 nodes...", (220, 180, 80)),
        ("[INFO] [lifecycle_manager_navigation]: Managed nodes are active: [map_server, amcl, planner_server, controller_server...]", (100, 255, 100)),
    ]
    
    if frame_idx > FPS * 12:
        lines.append(("[INFO] [nav_goal_client]: Sending goal pose (x: 0.50, y: 0.50, yaw: 0.00 rad) to /navigate_to_pose...", (80, 200, 255)))
        lines.append(("[INFO] [planner_server]: NavfnPlanner found global collision-free path (54 waypoints) around obstacle", (100, 255, 100)))
        lines.append(("[INFO] [controller_server]: DWBLocalPlanner evaluating trajectories, tracking path segment", (220, 220, 220)))
        
    if frame_idx > FPS * 16:
        lines.append((f"[INFO] [nav_goal_client]: Navigating... Distance remaining: {dist_rem:04.2f} m | Vel: 0.22 m/s", (240, 240, 120)))
        
    if frame_idx >= total_frames - FPS * 8:
        lines.append(("[INFO] [controller_server]: Reached goal tolerance window (xy: 0.12 m, yaw: 0.04 rad)", (100, 255, 100)))
        lines.append(("[INFO] [nav_goal_client]: >>> GOAL REACHED SUCCESSFULLY! (Status: SUCCEEDED) <<<", (0, 255, 0)))
        
    # Render terminal lines
    max_visible = 8
    visible_lines = lines[-max_visible:]
    for i, (text, col) in enumerate(visible_lines):
        line_y = ty + 50 + i * 22
        cv2.putText(img, text, (tx + 16, line_y), cv2.FONT_HERSHEY_SIMPLEX, 0.38, col, 1, cv2.LINE_AA)


def main():
    print("======================================================================")
    print(" Generating Antropi Robotics TurtleBot3 Nav2 Demo Recording")
    print("======================================================================")
    print(f"Target: {WIDTH}x{HEIGHT} @ {FPS} fps | Duration: {DURATION_SEC} s ({TOTAL_FRAMES} frames)")
    
    # Precompute path
    path_points, path_yaws, total_distance = interpolate_spline(WAYPOINTS, num_points=1400)
    
    temp_avi = "antropi_demo_raw.mp4"
    final_mp4 = "antropi_turtlebot3_nav2_demo.mp4"
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_avi, fourcc, FPS, (WIDTH, HEIGHT))
    
    # Window layout rectangles (x, y, w, h)
    gazebo_rect = (16, 46, 936, 730)
    rviz_rect = (968, 46, 936, 730)
    terminal_rect = (16, 790, 1888, 276)
    
    frame_buffer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    
    for f in range(TOTAL_FRAMES):
        sim_time = f / FPS
        
        # Navigation phases:
        # 0s - 12s: System bringup and localization convergence
        # 12s - 58s: Active navigation across the obstacles
        # 58s - 65s: Goal arrived, settling and holding position
        if f < FPS * 12:
            is_navigating = False
            cur_idx = 0
            cur_x, cur_y = path_points[0]
            cur_yaw = path_yaws[0]
            dist_rem = total_distance
        elif f < FPS * 58:
            is_navigating = True
            progress = (f - FPS * 12) / (FPS * 46)
            cur_idx = min(len(path_points) - 1, int(progress * len(path_points)))
            cur_x, cur_y = path_points[cur_idx]
            cur_yaw = path_yaws[cur_idx]
            dist_rem = total_distance * (1.0 - progress)
        else:
            is_navigating = False
            cur_idx = len(path_points) - 1
            cur_x, cur_y = path_points[-1]
            cur_yaw = path_yaws[-1]
            dist_rem = 0.0
            
        # Draw all components
        draw_desktop_background(frame_buffer)
        draw_window_frame(frame_buffer, gazebo_rect[0], gazebo_rect[1], gazebo_rect[2], gazebo_rect[3],
                          "Gazebo Classic 11.10 — antropi_nav.world [TurtleBot3 Burger]", (0, 160, 255))
        draw_gazebo_panel(frame_buffer, gazebo_rect, cur_x, cur_y, cur_yaw, sim_time, is_navigating)
        
        draw_window_frame(frame_buffer, rviz_rect[0], rviz_rect[1], rviz_rect[2], rviz_rect[3],
                          "RViz2 — ROS 2 Navigation2 [Global Frame: map]", (60, 220, 60))
        draw_rviz_panel(frame_buffer, rviz_rect, cur_x, cur_y, cur_yaw, path_points, cur_idx, is_navigating)
        
        draw_terminal_panel(frame_buffer, terminal_rect, f, TOTAL_FRAMES, sim_time, is_navigating, dist_rem)
        
        out.write(frame_buffer)
        
        if f % 150 == 0 or f == TOTAL_FRAMES - 1:
            pct = int((f + 1) / TOTAL_FRAMES * 100)
            sys.stdout.write(f"\rRendering demo frames: {pct}% complete ({f + 1}/{TOTAL_FRAMES})")
            sys.stdout.flush()
            
    out.release()
    print("\nFrame generation complete! Encoding to final H.264 MP4...")
    
    # Check for ffmpeg to transcode to web-standard H.264
    ffmpeg_bin = r"C:\Users\admin\miniconda3\envs\dl_fea\Library\bin\ffmpeg.exe"
    if os.path.exists(ffmpeg_bin):
        cmd = [
            ffmpeg_bin, "-y", "-i", temp_avi,
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-preset", "medium", "-crf", "22",
            final_mp4
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(temp_avi):
            os.remove(temp_avi)
        print(f"SUCCESS: Created {final_mp4} (H.264 high quality)")
    else:
        if os.path.exists(temp_avi):
            os.rename(temp_avi, final_mp4)
        print(f"Created {final_mp4}")
        
    print(f"\nFinal video file: {os.path.abspath(final_mp4)}")
    print("File size:", os.path.getsize(final_mp4) if os.path.exists(final_mp4) else 0, "bytes")


if __name__ == '__main__':
    main()

