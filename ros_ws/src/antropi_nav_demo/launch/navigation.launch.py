#!/usr/bin/env python3
"""
Navigation launch file for Antropi Nav Demo.

Brings up Nav2 stack with the custom parameter file and map.
Can be launched standalone (headless) or from demo.launch.py.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        "use_sim_time", default_value="true",
        description="Use simulation clock if true"
    )
    autostart_arg = DeclareLaunchArgument(
        "autostart", default_value="true",
        description="Automatically startup the Nav2 stack"
    )
    open_rviz_arg = DeclareLaunchArgument(
        "open_rviz", default_value="true",
        description="Launch RViz2 for visualization"
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    autostart = LaunchConfiguration("autostart")
    open_rviz = LaunchConfiguration("open_rviz")

    # Paths
    params_file = PathJoinSubstitution([
        FindPackageShare("antropi_nav_demo"), "config", "nav2_params.yaml"
    ])
    map_file = PathJoinSubstitution([
        FindPackageShare("antropi_nav_demo"), "maps", "map.yaml"
    ])
    rviz_config = PathJoinSubstitution([
        FindPackageShare("antropi_nav_demo"), "rviz", "nav_demo.rviz"
    ])

    # Nav2 bringup
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare("nav2_bringup"), "launch", "bringup_launch.py"
            ])
        ),
        launch_arguments={
            "map": map_file,
            "params_file": params_file,
            "use_sim_time": use_sim_time,
            "autostart": autostart,
        }.items(),
    )

    # RViz2
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config],
        parameters=[{"use_sim_time": use_sim_time}],
        condition=IfCondition(open_rviz),
        output="screen",
    )

    return LaunchDescription([
        use_sim_time_arg,
        autostart_arg,
        open_rviz_arg,
        nav2,
        rviz_node,
    ])