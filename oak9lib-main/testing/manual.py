from oak9 import Robot

ROBOT_IP = "172.20.10.12"

with Robot(ROBOT_IP) as robot:
    robot.encoder.reset()
    input("Empuja el robot en línea recta 1000 mm medidos y da Enter...")
    print(robot.encoder.read())