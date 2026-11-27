import re, math
import numpy as np
import matplotlib.pyplot as plt

ARCHIVO = "salida2.txt"

pat_ini = re.compile(r"yaw0=(-?[\d.]+)\s+giro=(-?[\d.]+)\s+dist=(-?[\d.]+)")
pat = re.compile(
    r"([\d.]+)s\s+hecho=\s*(-?[\d.]+)\s+yaw_err=\s*(-?[\d.]+)"
    r"\s+integ=\s*(-?[\d.]+)\s+L=\s*(-?[\d.]+)\s+R=\s*(-?[\d.]+)"
)
pat_fin = re.compile(r"avance listo:\s*(-?[\d.]+) mm, yaw=(-?[\d.]+) \(target (-?[\d.]+)\)")

# --- separar corridas ---
corridas = []
with open(ARCHIVO, encoding="utf-8") as f:
    for linea in f:
        m = pat_ini.search(linea)
        if m:
            corridas.append({"head": float(m[2]), "dist": float(m[3]), "filas": [], "fin": None})
            continue
        if not corridas:
            continue
        m = pat.search(linea)
        if m:
            corridas[-1]["filas"].append([float(g) for g in m.groups()])
        m = pat_fin.search(linea)
        if m:
            corridas[-1]["fin"] = [float(g) for g in m.groups()]

def procesar(c):
    t, hecho, yaw_err = np.array(c["filas"])[:, :3].T
    if c["fin"]:
        t = np.append(t, t[-1] + 0.5)
        hecho = np.append(hecho, c["fin"][0])
        yaw_err = np.append(yaw_err, c["fin"][2] - c["fin"][1])  # target - yaw

    head = math.radians(c["head"])
    th = head - np.radians(yaw_err)          # rumbo en el marco inicial (+ = izquierda)
    dd = np.diff(hecho, prepend=hecho[0])
    x = np.cumsum(dd * np.cos(th))
    y = np.cumsum(dd * np.sin(th))

    gx, gy = c["dist"] * math.cos(head), c["dist"] * math.sin(head)
    e_ct = -x * math.sin(head) + y * math.cos(head)        # error transversal (perpendicular a la ruta)
    e_lg = c["dist"] - (x * math.cos(head) + y * math.sin(head))  # lo que falta a lo largo de la ruta
    return dict(t=t, x=x, y=y, gx=gx, gy=gy, e_ct=e_ct, e_lg=e_lg, yaw_err=yaw_err)

res = [procesar(c) for c in corridas]

# --- resumen ---
for i, (c, r) in enumerate(zip(corridas, res), 1):
    print(f"Corrida {i}: meta=({r['gx']:.0f}, {r['gy']:.0f})  "
          f"final=({r['x'][-1]:.1f}, {r['y'][-1]:.1f})  "
          f"err_x={r['gx']-r['x'][-1]:.1f}  err_y={r['gy']-r['y'][-1]:.1f}  "
          f"max|e_transversal|={np.max(np.abs(r['e_ct'])):.2f} mm")

# --- graficas ---
fig = plt.figure(figsize=(14, 8))
ax0 = fig.add_subplot(2, 2, (1, 3))
colores = ["tab:red", "tab:blue"]
for i, r in enumerate(res):
    ax0.plot([0, r["gx"]], [0, r["gy"]], "k--", label="esperado" if i == 0 else None)
    ax0.plot(r["x"], r["y"], color=colores[i % 2], label=f"real, corrida {i+1}")
    ax0.plot(r["gx"], r["gy"], "kx")
ax0.set(xlabel="x [mm]", ylabel="y [mm]", title="Trayectoria en el plano")
ax0.axis("equal"); ax0.legend(); ax0.grid(True)

ax1 = fig.add_subplot(2, 2, 2)
for i, r in enumerate(res):
    ax1.plot(r["t"], r["e_ct"], color=colores[i % 2], label=f"corrida {i+1}")
ax1.axhline(0, color="k", ls="--")
ax1.set(xlabel="t [s]", ylabel="error transversal [mm]", title="Desviacion respecto a la recta esperada")
ax1.legend(); ax1.grid(True)

ax2 = fig.add_subplot(2, 2, 4)
for i, r in enumerate(res):
    ax2.plot(r["t"], r["e_lg"], color=colores[i % 2], label=f"corrida {i+1}")
ax2.axhline(0, color="k", ls="--")
ax2.set(xlabel="t [s]", ylabel="falta por recorrer [mm]", title="Error longitudinal")
ax2.legend(); ax2.grid(True)

plt.tight_layout()
plt.show()