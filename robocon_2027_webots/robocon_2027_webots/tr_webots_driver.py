import math
import time
import rclpy

from geometry_msgs.msg import Twist, TransformStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster


class TRWebotsDriver:
    """ROS 2 driver untuk TR mecanum robot."""

    def __init__(self):
        self._node = None
        self._robot = None
        self._motors = {}
        self._sensors = {}
        self._target_velocity = {}
        self._cmd_vel_subscription = None
        self._wheel_radius = 0.10
        self._half_wheelbase = 0.18
        self._half_track_width = 0.285
        self._max_wheel_speed = 20.0
        self._motor_direction = {
            'fl': 1.0,
            'fr': 1.0,
            'rl': 1.0,
            'rr': 1.0,
        }
        self._command_timeout = 0.5
        self._last_command_time = time.monotonic()

        self._wheel_joint_names = {
            'fl': 'front_left_wheel_joint',
            'fr': 'front_right_wheel_joint',
            'rl': 'rear_left_wheel_joint',
            'rr': 'rear_right_wheel_joint',
        }
        self._last_wheel_angle = {
            'fl': 0.0,
            'fr': 0.0,
            'rl': 0.0,
            'rr': 0.0,
        }
        self._timestep_sec = 0.032
        self._x = 0.0
        self._y = 0.0
        self._theta = 0.0
        self._joint_state_publisher = None
        self._odom_publisher = None
        self._tf_broadcaster = None

    def init(self, webots_node, properties):
        print('[TR DRIVER] init() dimulai', flush=True)
        
        if not rclpy.ok():
            rclpy.init()

        self._robot = getattr(webots_node, 'robot', None)
        self._node = rclpy.create_node('tr_webots_driver')

        if self._robot is not None:
            self._motors = {
                'fl': self._robot.getDevice('front_left_wheel_motor'),
                'fr': self._robot.getDevice('front_right_wheel_motor'),
                'rl': self._robot.getDevice('rear_left_wheel_motor'),
                'rr': self._robot.getDevice('rear_right_wheel_motor'),
            }

            for motor in self._motors.values():
                motor.setPosition(float('inf'))
                motor.setVelocity(0.0)

            self._sensors = {
                'fl': self._robot.getDevice('front_left_wheel_sensor'),
                'fr': self._robot.getDevice('front_right_wheel_sensor'),
                'rl': self._robot.getDevice('rear_left_wheel_sensor'),
                'rr': self._robot.getDevice('rear_right_wheel_sensor'),
            }

            timestep_ms = int(self._robot.getBasicTimeStep())
            self._timestep_sec = timestep_ms / 1000.0

            for sensor in self._sensors.values():
                sensor.enable(timestep_ms)

        self._target_velocity = {
            'fl': 0.0,
            'fr': 0.0,
            'rl': 0.0,
            'rr': 0.0,
        }

        self._cmd_vel_subscription = self._node.create_subscription(
            Twist,
            '/cmd_vel',
            self._cmd_vel_callback,
            10,
        )

        self._joint_state_publisher = self._node.create_publisher(
            JointState,
            '/joint_states',
            10,
        )
        self._odom_publisher = self._node.create_publisher(
            Odometry,
            '/odom',
            10,
        )
        self._tf_broadcaster = TransformBroadcaster(self._node)

        self._node.get_logger().info('TR driver aktif, subscriber /cmd_vel dibuat')

    def _normalize_wheel_speeds(self, fl, fr, rl, rr):
        max_abs = max(abs(fl), abs(fr), abs(rl), abs(rr), 1.0)

        if max_abs > self._max_wheel_speed:
            scale = self._max_wheel_speed / max_abs
            fl *= scale
            fr *= scale
            rl *= scale
            rr *= scale

        return fl, fr, rl, rr

    def _cmd_vel_callback(self, message):
        vx_ros = message.linear.x
        vy_ros = message.linear.y
        wz_ros = message.angular.z

        print('[TR DRIVER] cmd_vel:', vx_ros, vy_ros, wz_ros, flush=True)

        vx = vx_ros
        vy = -vy_ros
        wz = wz_ros

        lever_arm = self._half_wheelbase + self._half_track_width

        fl = (vx - vy - lever_arm * wz) / self._wheel_radius
        fr = (vx + vy + lever_arm * wz) / self._wheel_radius
        rl = (vx + vy - lever_arm * wz) / self._wheel_radius
        rr = (vx - vy + lever_arm * wz) / self._wheel_radius

        fl, fr, rl, rr = self._normalize_wheel_speeds(fl, fr, rl, rr)

        self._target_velocity['fl'] = fl
        self._target_velocity['fr'] = fr
        self._target_velocity['rl'] = rl
        self._target_velocity['rr'] = rr

        self._last_command_time = time.monotonic()

    def _command_has_timed_out(self):
        elapsed_time = time.monotonic() - self._last_command_time
        return elapsed_time > self._command_timeout

    def _stop_robot(self):
        for wheel_name in self._target_velocity:
            self._target_velocity[wheel_name] = 0.0

    def _read_wheel_velocities(self):
        """Baca sudut roda dari PositionSensor lalu turunkan jadi kecepatan sudut aktual."""
        dt = self._timestep_sec
        angles = {}
        velocities = {}

        for wheel_name, sensor in self._sensors.items():
            angle = sensor.getValue()

            if math.isnan(angle):
                angle = self._last_wheel_angle[wheel_name]

            velocities[wheel_name] = (angle - self._last_wheel_angle[wheel_name]) / dt
            self._last_wheel_angle[wheel_name] = angle
            angles[wheel_name] = angle

        return angles, velocities

    def _publish_joint_states(self, stamp, angles, velocities):
        message = JointState()
        message.header.stamp = stamp
        message.name = [
            self._wheel_joint_names[key] for key in ('fl', 'fr', 'rl', 'rr')
        ]
        message.position = [angles[key] for key in ('fl', 'fr', 'rl', 'rr')]
        message.velocity = [velocities[key] for key in ('fl', 'fr', 'rl', 'rr')]

        self._joint_state_publisher.publish(message)

    def _update_odometry(self, stamp, velocities):
        """Kinematika maju: kecepatan roda aktual -> kecepatan body -> integrasi pose."""
        dt = self._timestep_sec
        r = self._wheel_radius
        lever_arm = self._half_wheelbase + self._half_track_width

        fl = velocities['fl']
        fr = velocities['fr']
        rl = velocities['rl']
        rr = velocities['rr']

        vx = r * (fl + fr + rl + rr) / 4.0
        vy_internal = r * (fr + rl - fl - rr) / 4.0
        wz = r * (fr + rr - fl - rl) / (4.0 * lever_arm)

        vy = -vy_internal

        self._x += (vx * math.cos(self._theta) - vy * math.sin(self._theta)) * dt
        self._y += (vx * math.sin(self._theta) + vy * math.cos(self._theta)) * dt
        self._theta += wz * dt

        quat_z = math.sin(self._theta / 2.0)
        quat_w = math.cos(self._theta / 2.0)

        odom_message = Odometry()
        odom_message.header.stamp = stamp
        odom_message.header.frame_id = 'odom'
        odom_message.child_frame_id = 'base_footprint'
        odom_message.pose.pose.position.x = self._x
        odom_message.pose.pose.position.y = self._y
        odom_message.pose.pose.orientation.z = quat_z
        odom_message.pose.pose.orientation.w = quat_w
        odom_message.twist.twist.linear.x = vx
        odom_message.twist.twist.linear.y = vy
        odom_message.twist.twist.angular.z = wz
        self._odom_publisher.publish(odom_message)

        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_footprint'
        transform.transform.translation.x = self._x
        transform.transform.translation.y = self._y
        transform.transform.rotation.z = quat_z
        transform.transform.rotation.w = quat_w
        self._tf_broadcaster.sendTransform(transform)

    def step(self):
        if self._node is None:
            return

        rclpy.spin_once(self._node, timeout_sec=0)

        if self._command_has_timed_out():
            self._stop_robot()

        for wheel_name, motor in self._motors.items():
            normalized_velocity = self._target_velocity[wheel_name]
            physical_velocity = normalized_velocity * self._motor_direction[wheel_name]
            motor.setVelocity(physical_velocity)

        if self._sensors:
            stamp = self._node.get_clock().now().to_msg()
            angles, velocities = self._read_wheel_velocities()
            self._publish_joint_states(stamp, angles, velocities)
            self._update_odometry(stamp, velocities)


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('tr_webots_driver')
    driver = TRWebotsDriver()
    driver._node = node
    driver._robot = None

    driver._cmd_vel_subscription = node.create_subscription(
        Twist,
        '/cmd_vel',
        driver._cmd_vel_callback,
        10,
    )

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()