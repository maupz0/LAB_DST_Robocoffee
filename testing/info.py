from oak9 import Robot

ip_robot = ("172.20.10.12")


with Robot(ip_robot) as robot:

    print("motor invert:   ", robot.motor.invert_get())
    print("encoder invert: ", robot.encoder.invert_get())
    print("cpr:            ", robot.encoder.cpr_get())
    print("geometry:       ", robot.geometry.get())
    print("pose:           ", robot.pose.get())
    print("encoder read:   ", robot.encoder.read())
    print("go2point pid:   ", robot.go2point.pid_get())
    print("vel pid:        ", robot.wheel_velocity.pid_get())
    print("pos pid:        ", robot.wheel_position.pid_get())
    print("go2point status:", robot.go2point.status())