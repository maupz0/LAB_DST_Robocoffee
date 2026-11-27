import time
from oak9 import Robot

ROBOT_IP = "172.20.10.12"

def ok(resp):
    if not resp["ok"]:
        raise RuntimeError(resp.get("raw_line", resp))
    return resp


def girar_forzado(robot, delta_deg, tol=2.0, settle_time=1.0,
                  timeout=20.0, print_every=5,
                  max_v=70, kp=2.0, v_min=15):
    y0 = ok(robot.imu.attitude_get())["yaw"]
    target = y0 + delta_deg
    print(f"[giro] yaw inicial: {y0:.2f}  target: {target:.2f}")

    t0 = time.time()
    it = 0
    stable = 0
    while time.time() - t0 < timeout:
        y = ok(robot.imu.attitude_get())["yaw"]
        err = target - y
        if abs(err) < tol:
            stable += 1
            if stable >= 3:
                break
        else:
            stable = 0
        v = max(-max_v, min(max_v, err * kp))
        if abs(err) > tol and abs(v) < v_min:
            v = v_min if err > 0 else -v_min
        ok(robot.wheel_velocity.set(left=-v, right=v))
        if it % print_every == 0:
            print(f"[giro] yaw={y:7.2f}  err={err:7.2f}  v={v:6.1f}")
        it += 1
        time.sleep(0.1)

    t_settle = time.time()
    while time.time() - t_settle < settle_time:
        y = ok(robot.imu.attitude_get())["yaw"]
        err = target - y
        if abs(err) > 0.7:
            v = max(-25, min(25, err * 3))
            if abs(v) < 12:
                v = 12 if err > 0 else -12
        else:
            v = 0
        ok(robot.wheel_velocity.set(left=-v, right=v))
        time.sleep(0.1)

    ok(robot.wheel_velocity.set(left=0, right=0))
    time.sleep(0.3)
    y_fin = ok(robot.imu.attitude_get())["yaw"]
    err_fin = y_fin - target
    print(f"[giro] yaw final: {y_fin:.2f}  error: {err_fin:.2f}°")
    return err_fin


if __name__ == "__main__":
    with Robot(ROBOT_IP) as robot:
        try:
            girar_forzado(robot, 86)
        finally:
            try:
                robot.motor.stop()
            except Exception:
                pass