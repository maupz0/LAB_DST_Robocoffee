import math, time
from datetime import datetime
from oak9 import Robot
from go_recto import ok, get_yaw, avanzar_recto, stop_wheels, set_peak_ref
from lazo_giro import girar_forzado
from logging_utils import init_csvs, log_test, log_segment

ROBOT_IP = "172.20.10.12"
DIST_IDEAL = 4000
G90, G180 = 90, 180

PEAK_REF = {'value': 0.0}
 

def main():
    init_csvs()

    try:
        test_id = int(input("Test ID (1-10): ").strip())
    except ValueError:
        print("Test ID inválido. Saliendo.")
        return

    input(f"Robot en marca inicial. Enter para TEST #{test_id}...")

    with Robot(ROBOT_IP) as robot:
        try:
            set_peak_ref(PEAK_REF)

            ok(robot.encoder.reset())
            yaw0 = get_yaw(robot)
            x, y = 0.0, 0.0
            t_inicio = time.time()
            fecha = datetime.now().strftime('%Y-%m-%d')
            hora_ini = datetime.now().strftime('%H:%M:%S')

            giros_err = []
            peaks_avance = []
            dist_total = 0.0
            t_avances = 0.0
            t_giros = 0.0

            def avance(seg_id, label):
                nonlocal x, y, dist_total, t_avances
                PEAK_REF['value'] = 0.0
                x_i, y_i = x, y
                yaw_i = get_yaw(robot)
                t_i = time.time()

                print(f"\n=== {label} ===")
                d, dx, dy, yaw_f = avanzar_recto(robot, 1000)

                t_f = time.time()
                dur = t_f - t_i
                t_avances += dur
                x += dx; y += dy
                dist_total += d
                peak = PEAK_REF['value']
                vel = d / max(dur, 0.01)

                log_segment({
                    'test_id': test_id, 'segmento_id': seg_id, 'tipo': 'avance',
                    'comando': 1000, 'comando_efectivo': 1000,
                    't_inicio_s': round(t_i - t_inicio, 2),
                    't_fin_s': round(t_f - t_inicio, 2),
                    'duracion_s': round(dur, 2),
                    'yaw_inicio': round(yaw_i, 2), 'yaw_fin': round(yaw_f, 2),
                    'error_yaw_deg': round(yaw_f - yaw_i, 2),
                    'pos_x_ini': round(x_i, 0), 'pos_y_ini': round(y_i, 0),
                    'pos_x_fin': round(x, 0), 'pos_y_fin': round(y, 0),
                    'delta_x': round(dx, 0), 'delta_y': round(dy, 0),
                    'delta_dist': round(d, 0),
                    'peak_yaw_error_deg': round(peak, 2),
                    'vel_promedio_mm_s': round(vel, 1)
                })
                print(f"→ {d:.0f}mm  peak={peak:.1f}°  vel={vel:.0f}mm/s")

            def giro(seg_id, label, deg):
                nonlocal t_giros
                yaw_i = get_yaw(robot)
                t_i = time.time()

                print(f"\n=== {label} ===")
                err_fin = girar_forzado(robot, deg)
                giros_err.append(err_fin)

                t_f = time.time()
                dur = t_f - t_i
                t_giros += dur
                yaw_f = get_yaw(robot)

                log_segment({
                    'test_id': test_id, 'segmento_id': seg_id, 'tipo': 'giro',
                    'comando': deg, 'comando_efectivo': deg,
                    't_inicio_s': round(t_i - t_inicio, 2),
                    't_fin_s': round(t_f - t_inicio, 2),
                    'duracion_s': round(dur, 2),
                    'yaw_inicio': round(yaw_i, 2), 'yaw_fin': round(yaw_f, 2),
                    'error_yaw_deg': round(err_fin, 2),
                    'pos_x_ini': round(x, 0), 'pos_y_ini': round(y, 0),
                    'pos_x_fin': round(x, 0), 'pos_y_fin': round(y, 0),
                    'delta_x': 0, 'delta_y': 0, 'delta_dist': 0,
                    'peak_yaw_error_deg': abs(deg),
                    'vel_promedio_mm_s': 0
                })

            # Secuencia (86/172/-86/174)
            avance(1, "Paso 1")
            giro(2, "Paso 2: +90°", G90)
            avance(3, "Paso 3")
            peaks_avance.append(PEAK_REF['value'])
            giro(4, "Paso 4: +180°", G180)
            avance(5, "Paso 5")
            peaks_avance.append(PEAK_REF['value'])
            giro(6, "Paso 6: -90°", -G90)
            avance(7, "Paso 7")
            peaks_avance.append(PEAK_REF['value'])
            giro(8, "Paso 8: +180°", G180)

            # Mediciones físicas
            print("\n" + "=" * 50)
            print("MIDE CON CINTA:")
            lat = float(input("  Lateral (Y) en mm: ").strip() or 0)
            lon = float(input("  Longitudinal (X) en mm: ").strip() or 0)
            notas = input("  Notas (opcional): ").strip()
            err_real = math.hypot(lat, lon)

            t_fin = time.time()
            dur_total = t_fin - t_inicio
            hora_fin = datetime.now().strftime('%H:%M:%S')
            yaw_fin = get_yaw(robot)
            dyaw = (yaw_fin - yaw0) % 360
            err_est = math.hypot(x, y)
            eficiencia = (DIST_IDEAL / max(dist_total, 1)) * 100

            resultado = ('exito' if err_real < 50
                         else 'parcial' if err_real < 100
                         else 'fallo')

            log_test({
                'test_id': test_id, 'fecha': fecha,
                'hora_inicio': hora_ini, 'hora_fin': hora_fin,
                'duracion_total_s': round(dur_total, 1),
                'yaw_inicial': round(yaw0, 2), 'yaw_final': round(yaw_fin, 2),
                'error_yaw_total_deg': round(min(dyaw, 360 - dyaw), 2),
                'pos_x_est': round(x, 0), 'pos_y_est': round(y, 0),
                'error_pos_est': round(err_est, 0),
                'error_lat_real': round(lat, 0),
                'error_lon_real': round(lon, 0),
                'error_pos_real': round(err_real, 0),
                'err_giro_p2': round(giros_err[0], 2),
                'err_giro_p4': round(giros_err[1], 2),
                'err_giro_p6': round(giros_err[2], 2),
                'err_giro_p8': round(giros_err[3], 2),
                'peak_p3': round(peaks_avance[0], 2),
                'peak_p5': round(peaks_avance[1], 2),
                'peak_p7': round(peaks_avance[2], 2),
                'dist_encoder': round(dist_total, 0),
                'dist_ideal': DIST_IDEAL,
                'eficiencia_pct': round(eficiencia, 1),
                't_avances': round(t_avances, 1),
                't_giros': round(t_giros, 1),
                'resultado': resultado,
                'notas': notas
            })

            print(f"\n✅ Test #{test_id} registrado")
            print(f"   Resultado: {resultado}")
            print(f"   Error físico: {err_real:.0f}mm")
            print(f"   Duración: {dur_total:.1f}s")

        finally:
            try:
                robot.wheel_velocity.stop(); robot.motor.stop()
            except Exception:
                pass


if __name__ == "__main__":
    main()