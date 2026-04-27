from setuptools import find_packages, setup

package_name = 'lidar_scan_viewer'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/view_scan.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='paint-o-bot',
    maintainer_email='paint-o-bot@todo.todo',
    description='Simple LaserScan subscriber to inspect /scan data',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'scan_listener = lidar_scan_viewer.scan_listener:main',
        ],
    },
)
