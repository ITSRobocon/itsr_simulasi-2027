from glob import glob
import os
from setuptools import find_packages, setup

package_name = 'robocon_2027_webots'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join(
                'share',
                package_name,
                'launch'
            ),
            glob('launch/*.launch.py')
        ),
        (
            os.path.join(
                'share',
                package_name,
                'worlds'
            ),
            glob('worlds/*.wbt')
        ),
        (
            os.path.join(
                'share',
                package_name,
                'worlds',
                'textures'
            ),
            glob('worlds/textures/*')
        ),
        (
            os.path.join(
                'share',
                package_name,
                'protos'
            ),
            glob('protos/*.proto')
        ),
        (
            os.path.join(
                'share',
                package_name,
                'urdf'
            ),
            glob('urdf/*')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hilal',
    maintainer_email='hilaltsabitulazmiarbai@gmail.com',
    description='this package is for robocon 2027 simulation and control',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'controller_node = robocon_2027_controller.controller_node:main',
        ],
    },
)
