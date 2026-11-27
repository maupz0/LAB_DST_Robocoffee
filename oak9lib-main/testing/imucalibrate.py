import time
from oak9 import Robot

ROBOT_IP = "172.20.10.12"

def ok(resp):
    if not resp["ok"]:
        raise RuntimeError(resp.get("raw_line", resp))
    return resp

robot = Robot(ROBOT_IP)
try:
    print("Quieto 5 s antes de calibrar...")
    time.sleep(5)

    print("Calibrando:", ok(robot.imu.calibrate()))
    time.sleep(1)

    print(f"\n{'t(s)':>5} | {'yaw':>8} | {'pose_theta':>10}")
    print("-" * 30)

    t0 = time.time()
    first_yaw = None
    yaw = None
    while time.time() - t0 < 30:
        att  = ok(robot.imu.attitude_get())
        pose = ok(robot.pose.get())
        t = time.time() - t0
        yaw = att.get("yaw", att.get("yaw_deg", 0))
        if first_yaw is None:
            first_yaw = yaw
        print(f"{t:5.1f} | {yaw:8.2f} | {pose['theta_deg']:10.2f}")
        time.sleep(1)

    drift = yaw - first_yaw
    print(f"\nDrift 30 s: {drift:.2f}°  ({drift/30:.3f}°/s)")
    print(f"Antes de calibrar era: -11.3°  (-0.377°/s)")
finally:
    try:
        robot.motor.stop()
    except Exception:
        pass
    robot.close()