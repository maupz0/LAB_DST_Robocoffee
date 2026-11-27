import time
from oak9 import Robot
ROBOT_IP = "172.20.10.12"
def ok(r):
    if not r["ok"]: raise RuntimeError(r.get("raw_line", r))
    return r

with Robot(ROBOT_IP) as robot:
    try:
        ok(robot.encoder.reset())
        ok(robot.pose.set(0,0,0))
        input("Empuja el robot ~1000 mm EN LÍNEA RECTA (usa una regla/cuerda de guía). Enter al terminar...")
        print("pose:", ok(robot.pose.get()))
        print("encoder:", ok(robot.encoder.read()))
        print("imu:", ok(robot.imu.attitude_get()))
    finally:
        try: robot.motor.stop()
        except: pass