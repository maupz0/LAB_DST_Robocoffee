import csv, os

TEST_FIELDS = [
    'test_id','fecha','hora_inicio','hora_fin','duracion_total_s',
    'yaw_inicial','yaw_final','error_yaw_total_deg',
    'pos_x_est','pos_y_est','error_pos_est',
    'error_lat_real','error_lon_real','error_pos_real',
    'err_giro_p2','err_giro_p4','err_giro_p6','err_giro_p8',
    'peak_p3','peak_p5','peak_p7',
    'dist_encoder','dist_ideal','eficiencia_pct',
    't_avances','t_giros','resultado','notas'
]

SEGMENT_FIELDS = [
    'test_id','segmento_id','tipo','comando','comando_efectivo',
    't_inicio_s','t_fin_s','duracion_s',
    'yaw_inicio','yaw_fin','error_yaw_deg',
    'pos_x_ini','pos_y_ini','pos_x_fin','pos_y_fin',
    'delta_x','delta_y','delta_dist',
    'peak_yaw_error_deg','vel_promedio_mm_s'
]

def init_csvs():
    for fname, fields in [('robocoffee_tests.csv', TEST_FIELDS),
                           ('robocoffee_segments.csv', SEGMENT_FIELDS)]:
        if not os.path.exists(fname):
            with open(fname, 'w', newline='') as f:
                csv.DictWriter(f, fieldnames=fields).writeheader()
            print(f"[csv] creado: {fname}")

def log_test(row):
    with open('robocoffee_tests.csv', 'a', newline='') as f:
        csv.DictWriter(f, fieldnames=TEST_FIELDS).writerow(row)

def log_segment(row):
    with open('robocoffee_segments.csv', 'a', newline='') as f:
        csv.DictWriter(f, fieldnames=SEGMENT_FIELDS).writerow(row)