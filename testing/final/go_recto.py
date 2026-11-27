import time, math
from oak9 import Robot

# Variable global para peak de yaw durante avances
CURRENT_PEAK = {'value': 0.0}

def set_peak_ref(ref):
    global CURRENT_PEAK
    CURRENT_PEAK = ref

ROBOT_IP = "172.20.10.12"
WHEEL_RADIUS_MM = 33.50
CPR = 897
MM_PER_TICK = 2 * math.pi * WHEEL_RADIUS_MM / CPR
MIN_V = 50


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
            stop_wheels(rb); time.sleep(0.3)
            if abs(wrap180(target_yaw - get_yaw(rb))) < tol:
                return
            continue
        s = 1 if err > 0 else -1
        if abs(err) > 15:
            v = max(min_v, min(max_v, 2.0*abs(err)))
            ok(rb.wheel_velocity.set(left=-s*v, right=s*v))
            time.sleep(0.05)
        else:
            ok(rb.wheel_velocity.set(left=-s*min_v, right=s*min_v))
            time.sleep(0.08); stop_wheels(rb); time.sleep(0.25)
    stop_wheels(rb)
    raise TimeoutError(f"giro no convergio, yaw={get_yaw(rb):.1f}")

def advance_straight(rb, dist_mm, target_yaw, base_v=260, kp_yaw=5.0, ki_yaw=0.2,
                     integ0=3.0, max_corr=160.0, tol=10.0, slow_zone=60.0,
                     min_adv=90, timeout=20.0, print_every=5,
                     ramp_dist=200.0, ramp_v=140.0, kp_ramp=1.5, max_corr_ramp=50.0):
    enc_prev = get_enc_avg(rb); enc0 = enc_prev
    yaw_prev = get_yaw(rb)
    x_est, y_est = 0.0, 0.0
    t0 = time.time()
    t_prev, integ = t0, integ0
    it = 0

    while time.time() - t0 < timeout:
        enc_now = get_enc_avg(rb)
        done = (enc_now - enc0) * MM_PER_TICK
        remaining = dist_mm - done
        if remaining <= tol:
            break
        now = time.time()
        dt, t_prev = now - t_prev, now
        yaw_now = get_yaw(rb)
        err = wrap180(target_yaw - yaw_now)

        # Trackear peak (agregar esta línea)
        if abs(err) > CURRENT_PEAK['value']:
            CURRENT_PEAK['value'] = abs(err)

        delta_mm = (enc_now - enc_prev) * MM_PER_TICK
        yaw_avg = (yaw_prev + yaw_now) / 2.0
        th = math.radians(yaw_avg)
        x_est += delta_mm * math.cos(th)
        y_est += delta_mm * math.sin(th)
        enc_prev = enc_now; yaw_prev = yaw_now

        en_ramp = done < ramp_dist
        en_frenado = remaining <= slow_zone
        if en_ramp:
            v = ramp_v; kp_eff = kp_ramp; max_corr_eff = max_corr_ramp
        elif en_frenado:
            v = max(min_adv, base_v * remaining / slow_zone)
            kp_eff = kp_yaw; max_corr_eff = max_corr
        else:
            v = base_v; kp_eff = kp_yaw; max_corr_eff = max_corr

        lim = min(max_corr_eff, max(0.0, v - MIN_V))
        p_term = kp_eff * err
        if abs(p_term) < lim and not en_frenado:
            integ = max(-lim/ki_yaw, min(lim/ki_yaw, integ + err*dt))

        corr = p_term + ki_yaw * integ
        corr = max(-lim, min(lim, corr))
        l, r = v - corr, v + corr
        ok(rb.wheel_velocity.set(left=l, right=r))
        if it % print_every == 0:
            fase = "ramp" if en_ramp else ("fren" if en_frenado else "crui")
            print(f"{now-t0:4.1f}s [{fase}] hecho={done:6.0f} yaw_err={err:6.2f} integ={integ:6.2f} v={v:5.1f} L={l:6.1f} R={r:6.1f}")
        it += 1
        time.sleep(0.05)
    stop_wheels(rb)
    time.sleep(0.4)
    return done, x_est, y_est, get_yaw(rb)

def go_to(rb, x_mm, y_mm):
    yaw0 = get_yaw(rb)
    head = math.degrees(math.atan2(y_mm, x_mm))
    target = yaw0 + head
    dist = math.hypot(x_mm, y_mm)
    print(f"yaw0={yaw0:.2f} giro={head:.1f} dist={dist:.0f}")
    turn_to(rb, target)
    print(f"giro listo, yaw={get_yaw(rb):.2f} (target {target:.2f})")
    d, dx, dy, _ = advance_straight(rb, dist, target)
    print(f"avance listo: {d:.0f} mm, delta=({dx:.0f},{dy:.0f}), yaw={get_yaw(rb):.2f}")
    ok(rb.wheel_velocity.stop())


def avanzar_recto(rb, dist_mm, v_base=260, timeout=20.0, print_every=5):
    yaw_actual = get_yaw(rb)
    return advance_straight(rb, dist_mm, yaw_actual,
                            base_v=v_base, timeout=timeout, print_every=print_every)


if __name__ == "__main__":
    with Robot(ROBOT_IP) as robot:
        try:
            for x in (1000, -1000):
                input(f"Robot en la marca, caster alineado. Enter para ({x}, 0)")
                ok(robot.encoder.reset())
                go_to(robot, x, 0)
                print("enc:", ok(robot.encoder.read()))
                print("yaw final:", get_yaw(robot))
        finally:
            try:
                robot.wheel_velocity.stop(); robot.motor.stop()
            except Exception:
                pass