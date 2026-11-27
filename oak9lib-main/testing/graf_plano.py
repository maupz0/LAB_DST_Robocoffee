import re
import numpy as np
import matplotlib.pyplot as plt

ARCHIVO = "salida.txt"
DIST_META = 1000.0  # mm

pat = re.compile(
    r"([\d.]+)s\s+hecho=\s*(-?[\d.]+)\s+yaw_err=\s*(-?[\d.]+)"
    r"\s+integ=\s*(-?[\d.]+)\s+L=\s*(-?[\d.]+)\s+R=\s*(-?[\d.]+)"
)
pat_fin = re.compile(r"avance listo:\s*(-?[\d.]+) mm, yaw=(-?[\d.]+) \(target (-?[\d.]+)\)")

filas, fin = [], None
with open(ARCHIVO, encoding="utf-8") as f:
    for linea in f:
        m = pat.search(linea)
        if m:
            filas.append([float(g) for g in m.groups()])
        m = pat_fin.search(linea)
        if m:
            fin = [float(g) for g in m.groups()]

d = np.array(filas)
t, hecho, yaw_err, integ, L, R = d.T

# Punto final (despues del frenado): distancia real y error de yaw final
if fin:
    t = np.append(t, t[-1] + 0.5)
    hecho = np.append(hecho, fin[0])
    yaw_err = np.append(yaw_err, fin[2] - fin[1])   # target - yaw

# Rumbo relativo a la ruta (+ = izquierda, +y): yaw - target = -yaw_err
th = np.radians(-yaw_err)

# Odometria: integra la distancia avanzada con el rumbo
dd = np.diff(hecho, prepend=hecho[0])
x = np.cumsum(dd * np.cos(th))
y = np.cumsum(dd * np.sin(th))

# Error respecto a la ruta esperada (linea y=0, x de 0 a meta)
err_y = y                      # desviacion lateral
err_x = DIST_META - x          # lo que falta para la meta

print(f"Posicion final estimada: x={x[-1]:.1f} mm, y={y[-1]:.1f} mm")
print(f"Error final: ex={err_x[-1]:.1f} mm, ey={err_y[-1]:.2f} mm")
print(f"Max |ey| = {np.max(np.abs(err_y)):.2f} mm")

fig, ax = plt.subplots(2, 2, figsize=(13, 8))

ax[0, 0].plot([0, DIST_META], [0, 0], "k--", label="esperado")
ax[0, 0].plot(x, y, "r.-", label="real (odometria)")
ax[0, 0].set(xlabel="x [mm]", ylabel="y [mm]", title="Trayectoria (y ampliada)")
ax[0, 0].legend(); ax[0, 0].grid(True)

ax[0, 1].plot(x, err_y)
ax[0, 1].axhline(0, color="k", ls="--")
ax[0, 1].set(xlabel="x [mm]", ylabel="error y [mm]", title="Desviacion lateral vs posicion")
ax[0, 1].grid(True)

ax[1, 0].plot(t, x, label="x real")
ax[1, 0].axhline(DIST_META, color="k", ls="--", label="meta")
ax[1, 0].set(xlabel="t [s]", ylabel="x [mm]", title="Avance en x vs tiempo")
ax[1, 0].legend(); ax[1, 0].grid(True)

ax[1, 1].plot(t[:len(yaw_err)], yaw_err)
ax[1, 1].axhline(0, color="k", ls="--")
ax[1, 1].set(xlabel="t [s]", ylabel="yaw_err [deg]", title="Error de yaw")
ax[1, 1].grid(True)

plt.suptitle("Recorrido a (1000, 0)")
plt.tight_layout()
plt.show()