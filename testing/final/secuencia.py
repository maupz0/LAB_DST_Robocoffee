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

            avance("Paso 1: Avanzar 1 m")
            giro("Paso 2: Girar +90°", 86)
            avance("Paso 3: Avanzar 1 m")
            giro("Paso 4: Girar +180°", 172)
            avance("Paso 5: Avanzar 1 m")
            giro("Paso 6: Girar -90°", -86)
            avance("Paso 7: Avanzar 1 m")
            giro("Paso 8: Girar +180° final", 170)

            yaw_fin = get_yaw(robot)
            dyaw = (yaw_fin - yaw0) % 360
            print("\n" + "=" * 40)
            print("RESUMEN")
            print(f"  Yaw inicial:  {yaw0:.2f}")
            print(f"  Yaw final:    {yaw_fin:.2f}")
            print(f"  Δyaw total:   {dyaw:.2f}°")
            print(f"  Pos final ≈   ({x:.0f}, {y:.0f}) mm")
            print(f"  Error pos ≈   {math.hypot(x, y):.0f} mm")
            print(f"  Orientación:  {'aprox a inicial' if (dyaw < 5 or dyaw > 355) else 'desviado'}")
            print("=" * 40)

        finally:
            try:
                robot.wheel_velocity.stop(); robot.motor.stop()
            except Exception:
                pass


if __name__ == "__main__":
    main()
