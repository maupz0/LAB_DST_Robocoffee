import time, math
from oak9 import Robot

ROBOT_IP = "172.20.10.12"
WHEEL_RADIUS_MM = 33.5      # medido (llanta 66.5 mm)
CPR = 897
MM_PER_TICK = 2 * math.pi * WHEEL_RADIUS_MM / CPR
MIN_V = 50                   # zona muerta medida: debajo de ~45 no se mueve

def ok(r):
    if not r["ok"]:
        raise RuntimeError(r.get("raw_line", r))
    return r

def wrap180(a): return ((a + 180) % 360) - 180
def get_yaw(rb): return ok(rb.imu.attitude_get())["yaw"]

def get_enc_avg(rb):
    e = ok(rb.encoder.read())
    return (e["left"] + e["right"]) / 2.0

def stop_wheels(rb):
    ok(rb.wheel_velocity.set(left=0, right=0))

def turn_to(rb, target_yaw, tol=3.0, max_v=70, min_v=MIN_V, timeout=10.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        err = wrap180(target_yaw - get_yaw(rb))
        if abs(err) < tol:
            stop_wheels(rb)
            time.sleep(0.3)
            if abs(wrap180(target_yaw - get_yaw(rb))) < tol:
                return
            continue
        s = 1 if err > 0 else -1
        if abs(err) > 15:
            v = max(min_v, min(max_v, 2.0 * abs(err)))
            ok(rb.wheel_velocity.set(left=-s * v, right=s * v))
            time.sleep(0.05)
        else:                                   # pulso corto, luego pausa
            ok(rb.wheel_velocity.set(left=-s * min_v, right=s * min_v))
            time.sleep(0.08)
            stop_wheels(rb)
            time.sleep(0.25)
    stop_wheels(rb)
    raise TimeoutError(f"giro no convergio, yaw={get_yaw(rb):.1f}")

def advance_straight(rb, dist_mm, target_yaw, base_v=200, kp_yaw=1.0, ki_yaw=0.4,
                     integ0=10.0, max_corr=30.0, tol=10.0, slow_zone=100.0,
                     min_adv=60, timeout=30.0):
    enc0, t0 = get_enc_avg(rb), time.time()
    t_prev, integ = t0, integ0
    while time.time() - t0 < timeout:
        done = (get_enc_avg(rb) - enc0) * MM_PER_TICK
        remaining = dist_mm - done
        if remaining <= tol:
            break
        now = time.time()
        dt, t_prev = now - t_prev, now
        err = wrap180(target_yaw - get_yaw(rb))
        en_frenado = remaining <= slow_zone
        v = base_v if not en_frenado else max(min_adv, base_v * remaining / slow_zone)
        lim = min(max_corr, max(0.0, v - MIN_V))
        if not en_frenado:                       # integral congelado al frenar
            integ = max(-lim / ki_yaw, min(lim / ki_yaw, integ + err * dt))
        corr = kp_yaw * err + ki_yaw * integ
        corr *= min(1.0, v / base_v)             # menos correccion a menor velocidad
        corr = max(-lim, min(lim, corr))
        l, r = v - corr, v + corr
        ok(rb.wheel_velocity.set(left=l, right=r))
        print(f"{now-t0:4.1f}s hecho={done:6.0f} yaw_err={err:6.2f} integ={integ:6.2f} L={l:6.1f} R={r:6.1f}")
        time.sleep(0.05)
    stop_wheels(rb)
    time.sleep(0.4)
    return (get_enc_avg(rb) - enc0) * MM_PER_TICK

def go_to(rb, x_mm, y_mm):
    yaw0 = get_yaw(rb)
    head = math.degrees(math.atan2(y_mm, x_mm))   # +y = izquierda
    target = yaw0 + head
    dist = math.hypot(x_mm, y_mm)
    print(f"yaw0={yaw0:.2f} giro={head:.1f} dist={dist:.0f}")
    turn_to(rb, target)
    print(f"giro listo, yaw={get_yaw(rb):.2f} (target {target:.2f})")
    hecho = advance_straight(rb, dist, target)
    print(f"avance listo: {hecho:.0f} mm, yaw={get_yaw(rb):.2f} (target {target:.2f})")
    ok(rb.wheel_velocity.stop())

with Robot(ROBOT_IP) as robot:
    try:
        for y in (300, -300):
            input(f"Robot en la marca, caster alineado. Enter para (1000, {y})...")
            ok(robot.encoder.reset())
            go_to(robot, 1000, y)
            print("enc:", ok(robot.encoder.read()))
            print("yaw final:", get_yaw(robot))

    finally:
        try:
            robot.wheel_velocity.stop()
            robot.motor.stop()
        except Exception:
            pass