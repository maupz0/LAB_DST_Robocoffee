"""
Calibración CPR - versión simple 3 reps.
Robot avanza 2000mm cada vez, tú lo regresas a mano a la marca inicial.
"""
import time
from oak9 import Robot

ROBOT_IP = "172.20.10.12"
CPR_ACTUAL = 897
WHEEL_RADIUS_MM = 33.50
MM_PER_TICK = 2 * 3.14159265 * WHEEL_RADIUS_MM / CPR_ACTUAL
DIST_TARGET = 2000
V_STRAIGHT = 200

def ok(r):
    if not r["ok"]:
        raise RuntimeError(r.get("raw_line", r))
    return r

def get_enc_avg(rb):
    e = ok(rb.encoder.read())
    return (e["left"] + e["right"]) / 2.0

def avanzar_lazo_abierto(rb, dist_mm, v=200):
    enc0 = get_enc_avg(rb)
    ok(rb.wheel_velocity.set(left=v, right=v))
    t0 = time.time()
    while time.time() - t0 < 30:
        d = (get_enc_avg(rb) - enc0) * MM_PER_TICK
        if d >= dist_mm:
            break
        time.sleep(0.02)
    ok(rb.wheel_velocity.stop())   # ← FIX: stop antes de reset
    time.sleep(0.5)
    return (get_enc_avg(rb) - enc0) * MM_PER_TICK


with Robot(ROBOT_IP) as robot:
    try:
        print(f"CPR actual: {CPR_ACTUAL}")
        print(f"MM_PER_TICK: {MM_PER_TICK:.6f}")
        print(f"Objetivo: {DIST_TARGET} mm × 3 reps\n")

        resultados = []
        for i in range(1, 4):
            input(f"\n[{i}/3] Robot en MARCA INICIAL. Enter...")
            ok(robot.wheel_velocity.stop())   # ← por si acaso
            time.sleep(0.2)
            ok(robot.encoder.reset())
            time.sleep(0.1)
            d_enc = avanzar_lazo_abierto(robot, DIST_TARGET)
            real = float(input(f"  Encoder dice: {d_enc:.1f} mm. Real (cinta): "))
            resultados.append((d_enc, real))
            input("  → Regresa el robot a la marca inicial a mano. Enter cuando esté listo...")

        print("\n" + "=" * 60)
        print("RESULTADOS")
        print(f"{'Rep':>4} | {'Encoder':>10} | {'Real':>8} | {'Ratio':>8}")
        print("-" * 60)
        ratios = []
        for i, (d_enc, d_real) in enumerate(resultados, 1):
            r = d_enc / d_real
            ratios.append(r)
            print(f"{i:>4} | {d_enc:>10.1f} | {d_real:>8.1f} | {r:>8.5f}")

        avg = sum(ratios) / len(ratios)
        nuevo_r = WHEEL_RADIUS_MM / avg
        nuevo_cpr = CPR_ACTUAL * avg

        print("-" * 60)
        print(f"Ratio promedio:     {avg:.5f}")
        print(f"WHEEL_RADIUS nuevo: {nuevo_r:.3f}  (actual {WHEEL_RADIUS_MM})")
        print(f"CPR nuevo:          {nuevo_cpr:.1f}  (actual {CPR_ACTUAL})")
        print("=" * 60)
    finally:
        try:
            robot.wheel_velocity.stop()
            robot.motor.stop()
        except Exception:
            pass