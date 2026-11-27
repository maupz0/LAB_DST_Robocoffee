import re
import numpy as np
import matplotlib.pyplot as plt

# 1. FILE CONFIGURATION
FILE_NAME = "salida.txt" 

# 2. DATA EXTRACTION & PROCESSING
pat = re.compile(
    r"\s*([\d.]+)s hecho=\s*(-?\d+) yaw_err=\s*(-?[\d.]+) "
    r"integ=\s*(-?[\d.]+) L=\s*(-?[\d.]+) R=\s*(-?[\d.]+)"
)

data = []
try:
    with open(FILE_NAME, encoding="utf-8") as f:
        for line in f:
            m = pat.match(line)
            if m:
                data.append([float(g) for g in m.groups()])
except FileNotFoundError:
    print(f"❌ Error: File '{FILE_NAME}' not found. Please ensure it is in the working directory.")
    exit()

# Transpose data into independent arrays
t, distance, yaw_error, integral, v_left, v_right = np.array(data).T

# 3. TYPOGRAPHY & LAYOUT CONFIGURATION
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

# 2x2 Subplot Grid Layout
fig, axes = plt.subplots(2, 2, figsize=(11, 7.5))
ax = axes.flatten()  

# Palette: Clean, professional flat design colors
colors = ["#E63946", "#457B9D", "#1D3557", "#8338EC"]

# --- Subplot 1: Heading Tracking (Yaw Error) ---
ax[0].plot(t, yaw_error, color=colors[0], lw=2)
ax[0].axhline(0, color="#666666", lw=1, linestyle="--")
ax[0].set_title("Heading Stability", fontsize=12, fontweight='bold', pad=10)
ax[0].set_ylabel("Yaw Error (°)")
ax[0].set_xlabel("Time (s)")

# --- Subplot 2: Actuator Command (Wheel Velocities) ---
ax[1].plot(t, v_left, color=colors[1], lw=2, label="Left Motor")
ax[1].plot(t, v_right, color=colors[1], lw=2, linestyle=":", label="Right Motor")
ax[1].set_title("Wheel Angular Velocity", fontsize=12, fontweight='bold', pad=10)
ax[1].set_ylabel("Velocity (°/s)")
ax[1].set_xlabel("Time (s)")
ax[1].legend(frameon=True, facecolor='white', edgecolor='none')

# --- Subplot 3: Odometer (Distance Traveled) ---
ax[2].plot(t, distance, color=colors[2], lw=2.5)
ax[2].set_title("Odometer Progress", fontsize=12, fontweight='bold', pad=10)
ax[2].set_ylabel("Distance (mm)")
ax[2].set_xlabel("Time (s)")

# --- Subplot 4: PID Controller (Integral Term) ---
ax[3].plot(t, integral, color=colors[3], lw=2)
ax[3].set_title("PID Integral Term Response", fontsize=12, fontweight='bold', pad=10)
ax[3].set_ylabel("Integral Value")
ax[3].set_xlabel("Time (s)")

# 4. VISUAL OPTIMIZATIONS & STYLING
for a in ax:
    # Subtle background grid lines
    a.grid(True, linestyle=":", alpha=0.5, color="#CCCCCC") 
    
    # Remove top and right borders for a modern, clean look
    a.spines['top'].set_visible(False)
    a.spines['right'].set_visible(False)
    
    # Slightly offset the axes from the data area
    a.spines['left'].set_position(('outward', 5))
    a.spines['bottom'].set_position(('outward', 5))

# Global Figure Title
fig.suptitle("Telemetry Analysis: Straight-Line PID Control", 
             fontsize=15, fontweight='bold', color="#1D3557", y=0.98)

# Layout adjustments and saving options
fig.tight_layout()
fig.savefig("pid_telemetry_analysis.png", dpi=300, bbox_inches='tight')
plt.show()

# 5. CLEAN CONSOLE REPORT
print(f"📊 CONTROL LOOP PERFORMANCE METRICS:")
print(f"  • Yaw Error RMS:        {np.sqrt(np.mean(yaw_error**2)):.2f}°")
print(f"  • Max Absolute Error:   {np.max(np.abs(yaw_error)):.2f}°")
print(f"  • Final Odometer Read:  {distance[-1]:.0f} mm")
