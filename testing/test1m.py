import time
from oak9 import Robot

ROBOT_IP = "172.20.10.12"   # tu IP actual

def ok(resp):
    if not resp["ok"]:
        raise RuntimeError(resp.get("raw_line", resp))
    return resp

with Robot(ROBOT_IP) as robot:
    try:
        ok(robot.encoder.reset())
        ok(robot.pose.set(x_mm=0, y_mm=0, theta_deg=0))

        print("set:", ok(robot.go2point.set(x=1000, y=0)))

        status = robot.go2point.status()
        while status["active"]:
            time.sleep(0.1)
            status = robot.go2point.status()

        print("status final:", status)
        print("pose final:  ", robot.pose.get())
        print("encoder:     ", robot.encoder.read())
    finally:
        robot.go2point.stop()