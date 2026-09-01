import os

from glob import glob
from setuptools import find_packages, setup

package_name = 'robocon_2027_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',['resource/' + package_name]
        ),
        (
            'share/' + package_name, ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),glob('launch/*.launch.py')
        ),
        (
            os.path.join('share', package_name, 'config'), glob('config/*.yaml')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hilal',
    maintainer_email='hilaltsabitulazmiarbai@gmail.com',
    description='i make this package for control the robot',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'tr_controller = '
            'robocon_2027_controller.tr_controller:main',
            'br_controller = '
            'robocon_2027_controller.br_controller:main',
        ],
    },
)
