#!/usr/bin/env python3
"""
Gazebo-only launch file for Antropi Nav Demo.

Launches Gazebo Classic with the custom world and robot_state_publisher.
Run this FIRST, wait for Gazebo to fully start and /odom to publish,
then run navigation.launch.py in a separate terminal.
"""

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Custom world with additional obstacles for better demo
    world_file = PathJoinSubstitution([
        FindPackageShare("antropi_nav_demo"),
        "worlds",
        "antropi_nav.world",
    ])

    # Gazebo Classic
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("gazebo_ros"),
                "launch",
                "gazebo.launch.py",
            ])
        ),
        launch_arguments={
            "world": world_file,
            "gui": "true",
        }.items(),
    )

    # Robot state publisher
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("turtlebot3_gazebo"),
                "launch",
                "robot_state_publisher.launch.py",
            ])
        ),
        launch_arguments={"use_sim_time": "true"}.items(),
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
        robot_state_publisher,
    ])