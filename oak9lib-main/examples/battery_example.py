from oak9 import Robot

robot = Robot("172.20.10.12")

print(robot.battery.read())                      # voltaje actual de la bateria
print(robot.battery.calibrate(raw=3027, mv=8631)) # raw=lectura ADC, mv=voltaje real medido con multimetro

robot.live_plot(robot.battery.read, ["voltage"], interval=0.2)  # grafica en vivo, refresca cada 0.2s

robot.close()


'''
from oak9 import Robot

robot = Robot("172.20.10.12")

# pequeño setup
print(robot.battery.read())                        # bateria actual
print(robot.battery.calibrate(raw=3027, mv=8631))  # calibrar (adc vs real)

# calibracion inicial filtro ?

print(robot.imu.read())          # datos crudos del acelerometro/giroscopio
print(robot.imu.attitude_get())  # roll/pitch/yaw ya fusionados
print(robot.imu.filter_get())    # parametros del filtro complementario
print(robot.imu.filter_set(alpha=0.98, ts_ms=10)) # peso giro vs acelerometro y periodo de muestreo
print(robot.imu.calibrate())     # calibra el offset del IMU (robot debe estar quieto)

robot.live_plot(robot.imu.attitude_get, ["roll", "pitch", "yaw"],
                interval=0.01)                
robot.close()

# medicion entre desfase imu left and right ? 
print(robot.line.read())  # lectura de los sensores de linea (izquierdo/derecho)

robot.live_plot(robot.line.read, ["left", "right"], interval=0.05)

robot.close()

# ejemplo simple de movimiento sin control 

print(robot.motor.pwm(left=100, right=100))  # PWM directo a cada motor (sin control de velocidad)



'''
