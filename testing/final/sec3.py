import math, time
from oak9 import Robot
from go_recto import ok, get_yaw, avanzar_recto, stop_wheels
from lazo_giro import girar_forzado

ROBOT_IP = "172.20.10.12"

# ── Bias (compensación de caster) ──
BIAS_90           = 86    # giros de ±90° → ideal 90
BIAS_180_MID      = 172   # 180° intermedios (dentro de la fase)
BIAS_180_FINAL    = 174   # 180° final de cada fase (cierra orientación)
BIAS_180_INTERFASE = 174  # giro 180° entre pares de fases

# Cuántas fases correr. 2 = original + espejo. 4 = +180° y repetir.
NUM_FASES = 4


def main():
    with Robot(ROBOT_IP) as robot:
        try:
            input(f"Robot en marca. {NUM_FASES} fases = {NUM_FASES*4}m total. Enter...")
            ok(robot.encoder.reset())
            yaw0 = get_yaw(robot)
            x, y = 0.0, 0.0
            print(f"Yaw inicial: {yaw0:.2f}  Pos: ({x:.0f}, {y:.0f})")
            print(f"Bias: 90→{BIAS_90}°, 180→{BIAS_180_MID}°/{BIAS_180_FINAL}°, "
                  f"interfase→{BIAS_180_INTERFASE}°")

            def avance(label):
                nonlocal x, y
                print(f"\n=== {label} ===")
                d, dx, dy, yaw_e = avanzar_recto(robot, 1000)
                x += dx; y += dy
                print(f"→ {d:.0f}mm, delta=({dx:+.0f},{dy:+.0f}), "
                      f"pos=({x:.0f},{y:.0f}), yaw={yaw_e:.2f}")
                time.sleep(0.4)

            def giro(label, deg):
                print(f"\n=== {label} ===")
                girar_forzado(robot, deg)
                time.sleep(0.3)

            # ─────────────────────────────────────────────
            def fase_original(nombre):
                """+90, +180, -90, +180 final"""
                print("\n" + "█" * 55)
                print(f"  {nombre}")
                print("█" * 55)
                avance(f"{nombre} - Avance 1")
                giro(f"{nombre} - +90°", BIAS_90)
                avance(f"{nombre} - Avance 2")
                giro(f"{nombre} - +180°", BIAS_180_MID)
                avance(f"{nombre} - Avance 3")
                giro(f"{nombre} - -90°", -BIAS_90)
                avance(f"{nombre} - Avance 4")
                giro(f"{nombre} - +180° final", BIAS_180_FINAL)

            def fase_espejo(nombre):
                """-90, +180, +90, +180 final (espejo de la original)"""
                print("\n" + "█" * 55)
                print(f"  {nombre}")
                print("█" * 55)
                avance(f"{nombre} - Avance 1")
                giro(f"{nombre} - -90°", -BIAS_90)
                avance(f"{nombre} - Avance 2")
                giro(f"{nombre} - +180°", BIAS_180_MID)
                avance(f"{nombre} - Avance 3")
                giro(f"{nombre} - +90°", BIAS_90)
                avance(f"{nombre} - Avance 4")
                giro(f"{nombre} - +180° final", BIAS_180_FINAL)

            # ══════════════════════════════════════════════
            # PAR 1: FASE 1 + FASE 2
            # ══════════════════════════════════════════════
            fase_original("FASE 1: Original")
            fase_espejo("FASE 2: Espejo")

            yaw_p1 = get_yaw(robot)
            x_p1, y_p1 = x, y
            print(f"\n>>> Par 1 completo: Pos=({x:.0f},{y:.0f}) "
                  f"Yaw={yaw_p1:.2f} (Δ={((yaw_p1-yaw0)%360):.2f}°)")

            if NUM_FASES >= 4:
                # ══════════════════════════════════════════
                # GIRO 180° INTERFASE (espejo espacial)
                # ══════════════════════════════════════════
                print("\n" + "★" * 55)
                print("  GIRO 180° INTERFASE — el robot ahora mira al lado opuesto")
                print("★" * 55)
                giro("Interfase: Girar 180°", BIAS_180_INTERFASE)

                # ══════════════════════════════════════════
                # PAR 2: FASE 3 + FASE 4 (mismo patrón, pero espejo espacial)
                # ══════════════════════════════════════════
                fase_original("FASE 3: Original (post-180°)")
                fase_espejo("FASE 4: Espejo (post-180°)")

            # ── Resumen ──
            yaw_fin = get_yaw(robot)
            dyaw_total = (yaw_fin - yaw0) % 360

            print("\n" + "=" * 55)
            print("RESUMEN FINAL")
            print("=" * 55)
            print(f"  Yaw inicial:       {yaw0:.2f}")
            print(f"  Yaw tras Par 1:    {yaw_p1:.2f}  "
                  f"(Δ {((yaw_p1-yaw0)%360):.2f}°)")
            print(f"  Yaw final:         {yaw_fin:.2f}  (Δ total {dyaw_total:.2f}°)")
            print()
            print(f"  Pos tras Par 1:    ({x_p1:.0f}, {y_p1:.0f}) mm")
            print(f"  Pos final:         ({x:.0f}, {y:.0f}) mm")
            print(f"  Error est total:   {math.hypot(x, y):.0f} mm")
            print()
            print(f"  Fases ejecutadas:  {NUM_FASES}")
            print(f"  Recorrido total:   {NUM_FASES * 4} m")
            print("=" * 55)
            print("\n>>> MIDE FÍSICAMENTE con cinta:")
            print("    - Lateral (Y):       ______ cm")
            print("    - Longitudinal (X):  ______ cm")
            print("    - Orientación visual: ¿el robot mira hacia donde empezó?")

        finally:
            try:
                robot.wheel_velocity.stop(); robot.motor.stop()
            except Exception:
                pass


if __name__ == "__main__":
    main()