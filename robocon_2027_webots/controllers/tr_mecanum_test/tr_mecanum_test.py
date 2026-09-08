from controller import Robot


TIME_STEP = 16

robot = Robot()


motor_names = {
    'fl': 'front_left_wheel_motor',
    'fr': 'front_right_wheel_motor',
    'rl': 'rear_left_wheel_motor',
    'rr': 'rear_right_wheel_motor',
}


motors = {}

for key, device_name in motor_names.items():
    motor = robot.getDevice(device_name)
    motor.setPosition(float('inf'))
    motor.setVelocity(0.0)
    motors[key] = motor

WHEEL_RADIUS = 0.10
HALF_WHEELBASE = 0.18
HALF_TRACK_WIDTH = 0.285
MAX_WHEEL_SPEED = 20.0


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def set_chassis_velocity(vx, vy, wz):
    vy = -vy
    rotational_lever = (
        HALF_WHEELBASE
        + HALF_TRACK_WIDTH
    )

    fl = (
        vx
        - vy
        - rotational_lever * wz
    ) / WHEEL_RADIUS

    fr = (
        vx
        + vy
        + rotational_lever * wz
    ) / WHEEL_RADIUS

    rl = (
        vx
        + vy
        - rotational_lever * wz
    ) / WHEEL_RADIUS

    rr = (
        vx
        - vy
        + rotational_lever * wz
    ) / WHEEL_RADIUS

    wheel_velocities = [fl, fr, rl, rr]

    largest_velocity = max(
        abs(value)
        for value in wheel_velocities
    )

    if largest_velocity > MAX_WHEEL_SPEED:
        scale = MAX_WHEEL_SPEED / largest_velocity

        fl *= scale
        fr *= scale
        rl *= scale
        rr *= scale

    set_normalized_velocity(
        fl,
        fr,
        rl,
        rr,
    )
    
def set_normalized_velocity(fl, fr, rl, rr):
    motors['fl'].setVelocity(fl)
    motors['fr'].setVelocity(fr)
    motors['rl'].setVelocity(rl)
    motors['rr'].setVelocity(rr)

while robot.step(TIME_STEP) != -1:
    set_chassis_velocity(0.0, 0.0, 0.0)