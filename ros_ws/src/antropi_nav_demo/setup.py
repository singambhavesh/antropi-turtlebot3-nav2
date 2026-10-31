from setuptools import setup

package_name = 'antropi_nav_demo'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', ['config/nav2_params.yaml']),
        ('share/' + package_name + '/launch', ['launch/demo.launch.py', 'launch/navigation.launch.py', 'launch/gazebo.launch.py']),
        ('share/' + package_name + '/rviz', ['rviz/nav_demo.rviz']),
        ('share/' + package_name + '/worlds', ['worlds/antropi_nav.world']),
        ('share/' + package_name + '/maps', ['maps/map.yaml', 'maps/map.pgm']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Singam Bhavesh Reddy',
    maintainer_email='bhavesh@email.com',
    description='TurtleBot3 autonomous navigation demo with Nav2 for Antropi Robotics internship assignment',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'send_goal = antropi_nav_demo.send_goal:main',
        ],
    },
)