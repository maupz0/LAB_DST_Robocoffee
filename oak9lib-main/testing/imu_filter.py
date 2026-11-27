import time
from oak9 import Robot

ROBOT_IP = "172.20.10.12"

def ok(resp):
    if not resp["ok"]:
        raise RuntimeError(resp.get("raw_line", resp))
    return resp

robot = Robot(ROBOT_IP)
try:
    print("Antes:", ok(robot.imu.filter_get()))

    # Cambiar alpha 0.98 -> 0.90
    print("Seteando alpha=0.90...")
    print(ok(robot.imu.filter_set(alpha=0.98, ts_ms=10)))

    time.sleep(0.5)
    print("Después:", ok(robot.imu.filter_get()))
finally:
    try:
        robot.motor.stop()
    except Exception:
        pass
    robot.close()