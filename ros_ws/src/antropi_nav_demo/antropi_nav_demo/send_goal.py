#!/usr/bin/env python3
"""
Convenience script to send a navigation goal to TurtleBot3 Nav2 stack.
Can be run via: ros2 run antropi_nav_demo send_goal [--x X] [--y Y] [--yaw YAW]
"""

import sys
import argparse
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
import math


class NavGoalClient(Node):
    def __init__(self, x=0.5, y=0.5, yaw=0.0):
        super().__init__('nav_goal_client')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.target_x = x
        self.target_y = y
        self.target_yaw = yaw

    def send_goal(self):
        self.get_logger().info('Waiting for /navigate_to_pose action server...')
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Action server not available after 10s timeout!')
            return False

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(self.target_x)
        goal_msg.pose.pose.position.y = float(self.target_y)
        goal_msg.pose.pose.position.z = 0.0

        # Convert yaw to quaternion (rotation around Z axis)
        half_yaw = self.target_yaw * 0.5
        goal_msg.pose.pose.orientation.z = math.sin(half_yaw)
        goal_msg.pose.pose.orientation.w = math.cos(half_yaw)

        self.get_logger().info(
            f'Sending navigation goal: x={self.target_x:.2f}, y={self.target_y:.2f}, yaw={self.target_yaw:.2f} rad'
        )

        send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self._feedback_callback
        )
        send_goal_future.add_done_callback(self._goal_response_callback)
        return True

    def _goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal was rejected by Nav2!')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted! Robot is navigating...')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._get_result_callback)

    def _feedback_callback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(
            f'Remaining distance: {fb.distance_remaining:.2f} m | Nav time: {fb.navigation_time.sec} s',
            throttle_duration_sec=2.0
        )

    def _get_result_callback(self, future):
        status = future.result().status
        # Status 4 = STATUS_SUCCEEDED in action_msgs
        if status == 4:
            self.get_logger().info('>>> GOAL REACHED SUCCESSFULLY! <<<')
        else:
            self.get_logger().warn(f'Navigation ended with status code: {status}')
        rclpy.shutdown()


def main(args=None):
    parser = argparse.ArgumentParser(description='Send navigation goal to Nav2')
    parser.add_argument('--x', type=float, default=0.5, help='Target X coordinate in meters')
    parser.add_argument('--y', type=float, default=0.5, help='Target Y coordinate in meters')
    parser.add_argument('--yaw', type=float, default=0.0, help='Target orientation yaw in radians')
    parsed_args, unknown = parser.parse_known_args(sys.argv[1:])

    rclpy.init(args=args)
    client = NavGoalClient(x=parsed_args.x, y=parsed_args.y, yaw=parsed_args.yaw)
    if client.send_goal():
        rclpy.spin(client)
    else:
        rclpy.shutdown()


if __name__ == '__main__':
    main()
