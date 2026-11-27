import math, time
from oak9 import Robot
from go_recto import ok, get_yaw, avanzar_recto, stop_wheels
from lazo_giro import girar_forzado

ROBOT_IP = "172.20.10.12"


def main():
    with Robot(ROBOT_IP) as robot:
        try:
            input("Robot en la marca inicial. Enter para comenzar...")
            ok(robot.encoder.reset())
            yaw0 = get_yaw(robot)
            x, y = 0.0, 0.0
            print(f"Yaw inicial: {yaw0:.2f}  Pos: ({x:.0f}, {y:.0f})")

            def avance(label):
                nonlocal x, y
                print(f"\n=== {label} ===")
                d, dx, dy, yaw_e = avanzar_recto(robot, 1000)
                x += dx; y += dy
                print(f"→ recorrido {d:.0f} mm, delta=({dx:+.0f},{dy:+.0f}), "
                      f"pos=({x:.0f},{y:.0f}), yaw={yaw_e:.2f}")
                time.sleep(0.5)

            def giro(label, deg):
                print(f"\n=== {label} ===")
                girar_forzado(robot, deg)
                time.sleep(0.3)

            # ══════════════════════════════════════════════
            # FASE 1: SECUENCIA ORIGINAL (Pasos 1-8)
            # ══════════════════════════════════════════════
            print("\n" + "█" * 50)
            print("  FASE 1: SECUENCIA ORIGINAL")
            print("█" * 50)

            avance("Paso 1: Avanzar 1 m")
            giro("Paso 2: Girar +90°", 86)
            avance("Paso 3: Avanzar 1 m")
            giro("Paso 4: Girar +180°", 172)
            avance("Paso 5: Avanzar 1 m")
            giro("Paso 6: Girar -90°", -86)
            avance("Paso 7: Avanzar 1 m")
            giro("Paso 8: Girar +180° final", 174)

            yaw_mid = get_yaw(robot)
            x_mid, y_mid = x, y
            print(f"\n>>> Fase 1 completa. Pos=({x:.0f},{y:.0f})  "
                  f"Yaw={yaw_mid:.2f}  (Δ={((yaw_mid-yaw0)%360):.2f}°)")

            # ══════════════════════════════════════════════
            # FASE 2: SECUENCIA ESPEJO (Pasos 9-16)
            # giros 90 con signo opuesto, 180 iguales
            # ══════════════════════════════════════════════
            print("\n" + "█" * 50)
            print("  FASE 2: SECUENCIA ESPEJO")
            print("█" * 50)

            avance("Paso 9:  Avanzar 1 m")
            giro("Paso 10: Girar -90° (espejo)", -86)
            avance("Paso 11: Avanzar 1 m")
            giro("Paso 12: Girar +180° (espejo)", 172)
            avance("Paso 13: Avanzar 1 m")
            giro("Paso 14: Girar +90° (espejo)", 86)
            avance("Paso 15: Avanzar 1 m")
            giro("Paso 16: Girar +180° final (espejo)", 174)

            yaw_fin = get_yaw(robot)
            dyaw_fase1 = (yaw_mid - yaw0) % 360
            dyaw_fase2 = (yaw_fin - yaw_mid) % 360
            dyaw_total = (yaw_fin - yaw0) % 360

            print("\n" + "=" * 50)
            print("RESUMEN FINAL")
            print("=" * 50)
            print(f"  Yaw inicial:        {yaw0:.2f}")
            print(f"  Yaw tras Fase 1:    {yaw_mid:.2f}  (Δ {dyaw_fase1:+.2f}°)")
            print(f"  Yaw tras Fase 2:    {yaw_fin:.2f}  (Δ {dyaw_fase2:+.2f}°)")
            print(f"  Δyaw total:         {dyaw_total:.2f}°  (ideal 360×(1-bias)²)")
            print()
            print(f"  Pos tras Fase 1:    ({x_mid:.0f}, {y_mid:.0f}) mm")
            print(f"  Pos final:          ({x:.0f}, {y:.0f}) mm")
            print(f"  Error pos est:      {math.hypot(x, y):.0f} mm")
            print()
            print(f"  Orientación final:  "
                  f"{'✅ = inicial' if (dyaw_total < 5 or dyaw_total > 355) else '⚠️  desviada ~' + f'{min(dyaw_total, 360-dyaw_total):.0f}°'}")
            print("=" * 50)
            print("\n>>> MIDE FÍSICAMENTE con cinta métrica:")
            print("    - Error lateral (Y):       ______ cm")
            print("    - Error longitudinal (X):  ______ cm")

        finally:
            try:
                robot.wheel_velocity.stop(); robot.motor.stop()
            except Exception:
                pass


if __name__ == "__main__":
    main()