# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction, Shutdown, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, TextSubstitution

from launch_ros.actions import Node


def generate_launch_description():

    pkg_ros_gz_sim_demos = get_package_share_directory('ros_gz_sim_demos')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r camera_sensor.sdf --headless-rendering'}.items(),
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_ros_gz_sim_demos, 'rviz', 'camera.rviz')],
        condition=IfCondition(LaunchConfiguration('rviz'))
    )

    # Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/camera@sensor_msgs/msg/Image@ignition.msgs.Image',
                   '/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo'],
        output='screen'
    )

    # Record video
    recorder = Node(
        package='image_view',
        executable='video_recorder',
        parameters=[{
            "filename": LaunchConfiguration('output_video'),
        }],
        remappings=[
            ("image", "camera")
        ]
    )

    # shutdown
    shutdown = Node(
        package='cam_test',
        executable='stop',
        on_exit=[
            LogInfo(msg=["Node 2 stopped. Stopping everything..."]), 
            Shutdown(reason="Five second timeout")  
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true',
                              description='Open RViz.'),
        DeclareLaunchArgument('output_video', default_value='/tmp/output',
                              description='Output path'),
        gz_sim,
        bridge,
        rviz,
        recorder,
        shutdown, 
    ])
