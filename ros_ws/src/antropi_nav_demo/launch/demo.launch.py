#!/usr/bin/env python3
"""
Main demo launch file for Antropi Nav Demo.

This launch file starts Gazebo first, then Nav2 after a delay.
For WSL, it's recommended to run gazebo.launch.py and navigation.launch.py
in SEPARATE terminals instead, because Gazebo in WSL can take 30+ seconds
to fully start and publish /odom.
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Gazebo + robot_state_publisher
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("antropi_nav_demo"),
                "launch",
                "gazebo.launch.py",
            ])
        ),
    )

    # Nav2 stack + RViz - delayed for Gazebo startup
    # In WSL, Gazebo can take 35+ seconds to fully start
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("antropi_nav_demo"),
                "launch",
                "navigation.launch.py",
            ])
        ),
        launch_arguments={
            "use_sim_time": "true",
            "autostart": "true",
            "open_rviz": "true",
        }.items(),
    )

    return LaunchDescription([
        SetEnvironmentVariable("TURTLEBOT3_MODEL", "burger"),
        SetEnvironmentVariable(
            "GAZEBO_MODEL_PATH",
            PathJoinSubstitution([
                FindPackageShare("turtlebot3_gazebo"),
                "models",
            ]),
        ),
        gazebo,
        # Delay Nav2 startup by 40 seconds for WSL Gazebo startup
        TimerAction(period=40.0, actions=[navigation]),
    ])