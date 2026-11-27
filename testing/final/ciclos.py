"""
Diagnóstico de acumulación con Fase 1 + Fase 2 por ciclo.
Registra error estimado después de CADA fase para ver si F2 compensa o amplifica.

Uso:  python diag_acumulacion.py
"""
import math, time
from oak9 import Robot
from go_recto import ok, get_yaw, avanzar_recto, stop_wheels
from lazo_giro import girar_forzado

ROBOT_IP = "172.20.10.12"
BIAS = 0.0
N_CICLOS = 10

# Fases como listas de (tipo, deg)
FASE_1 = [
    ("av", None), ("gi", 90), ("av", None), ("gi", 180),
    ("av", None), ("gi", -90), ("av", None), ("gi", 180),
]
FASE_2 = [
    ("av", None), ("gi", -90), ("av", None), ("gi", 180),
    ("av", None), ("gi", 90), ("av", None), ("gi", 180),
]


def ejecutar_fase(robot, pasos, x, y):
    """Ejecuta una lista de pasos, actualiza x,y. Retorna (x,y)."""
    for tipo, deg in pasos:
        if tipo == "av":
            d, dx, dy, _ = avanzar_recto(robot, 1000)
            x += dx; y += dy
        else:
            girar_forzado(robot, deg * (1 - BIAS))
    return x, y


def main():
    with Robot(ROBOT_IP) as robot:
        try:
            print(f"BIAS={BIAS*100:.1f}%  Ciclos={N_CICLOS}")
            print(f"Cada ciclo = Fase 1 (8 pasos) + Fase 2 (8 pasos)")
            print(f"Recorrido total: {N_CICLOS * 8} m aprox")
            print(f"Tiempo estimado: {N_CICLOS * 1.5:.0f} min")
            input("\nRobot en marca. Enter para comenzar...")

            ok(robot.encoder.reset())
            yaw0 = get_yaw(robot)
            x_total, y_total = 0.0, 0.0

            print(f"\nYaw inicial: {yaw0:.2f}\n")

            # Encabezado de tabla
            print(f"{'Cic':>3} | {'Err_F1 (mm)':>12} | {'Err_F2 (mm)':>12} | "
                  f"{'ΔF2 (mm)':>10} | {'Tendencia':>12}")
            print("-" * 70)

            hist_err_f1 = []     # error acumulado después de F1 cada ciclo
            hist_err_f2 = []     # error acumulado después de F2 cada ciclo
            hist_delta_f2 = []   # cuánto cambió el error por F2 (negativo = compensa)

            for ciclo in range(1, N_CICLOS + 1):
                # ── Fase 1 ──
                x_total, y_total = ejecutar_fase(robot, FASE_1, x_total, y_total)
                err_f1 = math.hypot(x_total, y_total)
                hist_err_f1.append(err_f1)

                # ── Fase 2 ──
                x_total, y_total = ejecutar_fase(robot, FASE_2, x_total, y_total)
                err_f2 = math.hypot(x_total, y_total)
                hist_err_f2.append(err_f2)

                delta_f2 = err_f2 - err_f1
                hist_delta_f2.append(delta_f2)

                if delta_f2 < -2:
                    tendencia = "COMPENSA ✅"
                elif delta_f2 > 2:
                    tendencia = "AMPLIFICA ❌"
                else:
                    tendencia = "neutro"

                print(f"{ciclo:>3} | {err_f1:>12.0f} | {err_f2:>12.0f} | "
                      f"{delta_f2:>+10.0f} | {tendencia:>12}")

            # ── Análisis ──
            print("\n" + "=" * 70)
            print("ANÁLISIS")
            print("=" * 70)

            avg_delta_f2 = sum(hist_delta_f2) / len(hist_delta_f2)
            n_compensa = sum(1 for d in hist_delta_f2 if d < -2)
            n_amplifica = sum(1 for d in hist_delta_f2 if d > 2)

            print(f"  ΔF2 promedio: {avg_delta_f2:+.1f} mm/ciclo")
            if avg_delta_f2 < -1:
                print(f"  → F2 COMPENSA en promedio {abs(avg_delta_f2):.1f} mm/ciclo ✅")
            elif avg_delta_f2 > 1:
                print(f"  → F2 AMPLIFICA en promedio {avg_delta_f2:.1f} mm/ciclo ❌")
            else:
                print(f"  → F2 es neutro (no cambia el error)")

            print(f"\n  Ciclos donde F2 compensó (>2mm):    {n_compensa}/{N_CICLOS}")
            print(f"  Ciclos donde F2 amplificó (>2mm):   {n_amplifica}/{N_CICLOS}")

            print(f"\n  Error final acumulado: {err_f2:.0f} mm")
            print(f"  Error promedio por ciclo completo: {err_f2/N_CICLOS:.1f} mm")

            # Diagnóstico del tipo de crecimiento
            if N_CICLOS >= 5:
                err_c5 = hist_err_f2[4]
                err_c10 = hist_err_f2[-1]
                ratio = err_c10 / max(err_c5, 1)
                print(f"\n  Error en ciclo 5:   {err_c5:.0f} mm")
                print(f"  Error en ciclo 10:  {err_c10:.0f} mm")
                print(f"  Ratio C10/C5: {ratio:.2f}")
                if ratio > 1.7:
                    print(f"  → Crecimiento LINEAL (sistemático) ⚠️")
                elif ratio > 1.3:
                    print(f"  → Crecimiento mixto")
                else:
                    print(f"  → Crecimiento SUB-LINEAL (random walk) ✅")

            print("\n" + "=" * 70)
            print(">>> MIDE CON CINTA:")
            print("    Lateral (Y):       ______ cm")
            print("    Longitudinal (X):  ______ cm")
            print("    Orientación:       ¿mira al inicio?")

        finally:
            try:
                robot.wheel_velocity.stop(); robot.motor.stop()
            except Exception:
                pass


if __name__ == "__main__":
    main()