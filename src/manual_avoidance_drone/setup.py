from setuptools import find_packages, setup

package_name = 'manual_avoidance_drone'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/drone_avoidance.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='paint-o-bot',
    maintainer_email='paint-o-bot@todo.todo',
    description='Manual Drone Avoidance System using MAVROS and LiDAR',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'rc_reader = manual_avoidance_drone.rc_reader_node:main',
            'lidar_processor = manual_avoidance_drone.lidar_processor_node:main',
            'avoidance_controller = manual_avoidance_drone.avoidance_controller_node:main',
            'flight_manager = manual_avoidance_drone.flight_manager_node:main',
        ],
    },
)
