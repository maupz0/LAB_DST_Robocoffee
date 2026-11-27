import time
from oak9 import Robot

ROBOT_IP = "172.20.10.12"

def ok(resp):
    if not resp["ok"]:
        raise RuntimeError(resp.get("raw_line", resp))
    return resp

with Robot(ROBOT_IP) as robot:
    try:
        y0 = ok(robot.imu.attitude_get())["yaw"]
        target = y0 + 90  # giro de 90° a la izquierda
        print(f"yaw inicial: {y0:.2f}  target: {target:.2f}")

        t0 = time.time()
        while time.time() - t0 < 20:
            y = ok(robot.imu.attitude_get())["yaw"]
            err = target - y
            if abs(err) < 2:
                break
            v = max(-70, min(70, err * 2))

            # Piso anti-fricción: evita que el robot se atasque a baja velocidad
            if abs(err) > 2 and abs(v) < 15:
                v = 15 if err > 0 else -15

            ok(robot.wheel_velocity.set(left=-v, right=v))
            print(f"yaw={y:7.2f}  err={err:7.2f}  v={v:6.1f}")
            time.sleep(0.1)

        ok(robot.wheel_velocity.set(left=0, right=0))
        time.sleep(0.5)
        y_fin = ok(robot.imu.attitude_get())["yaw"]
        print(f"\nyaw final: {y_fin:.2f}  (target: {target:.2f})")
        print(f"error final: {y_fin - target:.2f}°")
    finally:
        try:
            robot.motor.stop()
        except Exception:
            pass