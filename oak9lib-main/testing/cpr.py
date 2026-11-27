from oak9 import Robot

ROBOT_IP = "172.20.10.12"

with Robot(ROBOT_IP) as robot:
    robot.encoder.reset()
    input("Da exactamente 10 vueltas a UNA rueda (robot levantado) y Enter...")
    e = robot.encoder.read()
    print(e)
    print("ticks/vuelta izq:", abs(e["left"]) / 10, " der:", abs(e["right"]) / 10)