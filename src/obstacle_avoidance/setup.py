from setuptools import find_packages, setup

package_name = 'obstacle_avoidance'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/avoid.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='paint-o-bot',
    maintainer_email='paint-o-bot@todo.todo',
    description='Simple obstacle avoidance between LiDAR and Pixhawk MAVROS',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'avoider = obstacle_avoidance.obstacle_avoider:main'
        ],
    },
)
