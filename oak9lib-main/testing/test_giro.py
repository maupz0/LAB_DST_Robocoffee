import time
from oak9 import Robot

with Robot("172.20.10.12") as robot:
    for _ in range(20):
        y = robot.imu.attitude_get()["yaw"]
        print(f"yaw = {y:8.2f}")
        time.sleep(0.5)