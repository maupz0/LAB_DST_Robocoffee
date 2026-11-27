import time
from oak9 import Robot

ROBOT_IP = "172.20.10.12"

def ok(resp):
    if not resp["ok"]:
        raise RuntimeError(resp.get("raw_line", resp))
    return resp

with Robot(ROBOT_IP) as robot:
    try:
        print("NO toques el robot. Arrancando en 5 s...")
        time.sleep(5)

        print("Filtro:", ok(robot.imu.filter_get()))

        print(f"\n{'t(s)':>5} | {'yaw':>8} | {'pose_theta':>10}")
        print("-" * 30)

        t0 = time.time()
        while time.time() - t0 < 30:
            att  = ok(robot.imu.attitude_get())
            pose = ok(robot.pose.get())
            t = time.time() - t0
            yaw = att.get("yaw", att.get("yaw_deg", 0))
            print(f"{t:5.1f} | {yaw:8.2f} | {pose['theta_deg']:10.2f}")
            time.sleep(1)
    finally:
        try:
            robot.motor.stop()
        except Exception:
            pass