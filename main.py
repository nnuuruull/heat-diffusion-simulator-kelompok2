# ===========================================================
# 🌡️ SIMULASI DIFUSI PANAS 1D (BTCS) 
# ===========================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox

# ===========================================================
# Thomas Algorithm (TDMA)
# ===========================================================
def thomas_algorithm(a, b, c, d):
    n = len(d)
    c_star = np.zeros(n-1)
    d_star = np.zeros(n)
    c_star[0] = c[0]/b[0]
    d_star[0] = d[0]/b[0]
    for i in range(1, n-1):
        denom = b[i] - a[i-1]*c_star[i-1]
        c_star[i] = c[i]/denom
        d_star[i] = (d[i]-a[i-1]*d_star[i-1])/denom
    d_star[-1] = (d[-1]-a[-1]*d_star[-2])/(b[-1]-a[-1]*c_star[-2])
    x = np.zeros(n)
    x[-1] = d_star[-1]
    for i in range(n-2, -1, -1):
        x[i] = d_star[i] - c_star[i]*x[i+1]
    return x

# ===========================================================
# BTCS solver
# ===========================================================
def heat_diffusion_btcs(L, Nx, alpha, dt, t_final, T_left, T_right, T_initial):
    dx = L / (Nx - 1)
    r = alpha * dt / dx**2
    Nt = int(t_final / dt)
    x = np.linspace(0, L, Nx)
    T = np.ones(Nx) * T_initial
    T[0], T[-1] = T_left, T_right

    a = -r * np.ones(Nx - 3)
    b = (1 + 2*r) * np.ones(Nx - 2)
    c = -r * np.ones(Nx - 3)

    T_history = [T.copy()]

    for n in range(Nt):
        d = T[1:-1].copy()
        d[0] += r * T_left
        d[-1] += r * T_right
        T_new = thomas_algorithm(a, b, c, d)
        T[1:-1] = T_new
        T_history.append(T.copy())

    return np.array(T_history), x, r, Nt

# ===========================================================
# Simulasi + Visualisasi
# ===========================================================
def run_simulation():
    try:
        L = float(entry_L.get())
        alpha = float(entry_alpha.get())
        Nx = int(entry_Nx.get())
        dt = float(entry_dt.get())
        t_final = float(entry_tfinal.get())
        T_left = float(entry_Tleft.get())
        T_right = float(entry_Tright.get())
        T_initial = float(entry_Tinit.get())

        progress_label.config(text="⏳ Simulasi sedang berjalan...")
        root.update()

        T_hist, x, r, Nt = heat_diffusion_btcs(L, Nx, alpha, dt, t_final, T_left, T_right, T_initial)
        times = np.linspace(0, t_final, len(T_hist))

        t_char = L**2 / alpha
        messagebox.showinfo("Hasil Simulasi",
                            f"Simulasi selesai!\n"
                            f"Rasio stabilitas r = {r:.4e}\n"
                            f"Waktu karakteristik difusi ≈ {t_char:.2f} s")

        progress_label.config(text="✅ Simulasi selesai!")

        # Bersihkan frame
        for f in [frame_plot1, frame_plot2, frame_plot3, frame_plot4]:
            for w in f.winfo_children():
                w.destroy()

        # -------------------------------------------------------
        # Plot 1: Profil Suhu
        fig1, ax1 = plt.subplots(figsize=(6,4))
        for i in np.linspace(0, len(times)-1, 6, dtype=int):
            ax1.plot(x, T_hist[i], label=f"t={times[i]:.1f}s")
        ax1.set_xlabel("Posisi (m)")
        ax1.set_ylabel("Suhu (°C)")
        ax1.set_title("Profil Suhu terhadap Posisi")
        ax1.legend()
        ax1.grid(True)
        canvas1 = FigureCanvasTkAgg(fig1, master=frame_plot1)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig1)

        # -------------------------------------------------------
        # Plot 2: Heatmap ΔT
        fig2, ax2 = plt.subplots(figsize=(6,4))
        im = ax2.imshow(T_hist - T_initial, aspect='auto', cmap='plasma',
                        extent=[0, L, t_final, 0])
        ax2.set_xlabel("Posisi (m)")
        ax2.set_ylabel("Waktu (s)")
        ax2.set_title("Evolusi Perubahan Suhu (ΔT)")
        plt.colorbar(im, ax=ax2, label="ΔT (°C)")
        canvas2 = FigureCanvasTkAgg(fig2, master=frame_plot2)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig2)

        # -------------------------------------------------------
        # Plot 3: Evolusi Suhu
        fig3, ax3 = plt.subplots(figsize=(6,4))
        idx1 = int(Nx*0.1)
        idx2 = int(Nx*0.5)
        idx3 = int(Nx*0.9)
        ax3.plot(times, T_hist[:, idx1], label=f"x={x[idx1]:.2f} m")
        ax3.plot(times, T_hist[:, idx2], label=f"x={x[idx2]:.2f} m")
        ax3.plot(times, T_hist[:, idx3], label=f"x={x[idx3]:.2f} m")
        ax3.set_xlabel("Waktu (s)")
        ax3.set_ylabel("Suhu (°C)")
        ax3.set_title("Evolusi Suhu di Beberapa Titik")
        ax3.legend()
        ax3.grid(True)
        canvas3 = FigureCanvasTkAgg(fig3, master=frame_plot3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig3)

        # -------------------------------------------------------
        # Plot 4: Analisis Stabilitas
        fig4, ax4 = plt.subplots(figsize=(6,4))
        energy = np.sum((T_hist - T_right)**2, axis=1)
        ax4.plot(times, energy/energy[0], '-o')
        ax4.set_xlabel("Waktu (s)")
        ax4.set_ylabel("Energi Relatif")
        ax4.set_title("Konvergensi / Stabilitas Energi Sistem")
        ax4.grid(True)
        canvas4 = FigureCanvasTkAgg(fig4, master=frame_plot4)
        canvas4.draw()
        canvas4.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig4)

    except Exception as e:
        messagebox.showerror("Error", f"Terjadi kesalahan:\n{e}")

# ===========================================================
# GUI Setup
# ===========================================================
root = tk.Tk()
root.title("🌡️ Simulasi Difusi Panas 1D - BTCS Method")
root.geometry("1200x700")
root.configure(bg="#f3f6fa")

tk.Label(root, text="Simulasi Difusi Panas 1D (BTCS)",
         font=("Segoe UI", 18, "bold"), bg="#f3f6fa", fg="#1f3c88").pack(pady=10)

main_frame = tk.Frame(root, bg="#f3f6fa")
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Input Panel
input_frame = tk.LabelFrame(main_frame, text="Parameter Simulasi",
                            bg="#f3f6fa", fg="#1f3c88", font=("Segoe UI", 11, "bold"))
input_frame.pack(side="left", fill="y", padx=10, pady=5)

def add_input(label, default):
    tk.Label(input_frame, text=label, bg="#f3f6fa").pack(anchor="w", pady=2)
    entry = ttk.Entry(input_frame, width=15)
    entry.insert(0, default)
    entry.pack(pady=2)
    return entry

entry_L = add_input("Panjang batang (m)", "0.1")
entry_alpha = add_input("Difusivitas (α) [m²/s]", "1.172e-5")
entry_Nx = add_input("Jumlah titik grid (Nx)", "50")
entry_dt = add_input("Langkah waktu (Δt) [s]", "0.05")
entry_tfinal = add_input("Waktu total (s)", "500")
entry_Tleft = add_input("Suhu kiri (°C)", "100")
entry_Tright = add_input("Suhu kanan (°C)", "0")
entry_Tinit = add_input("Suhu awal (°C)", "25")

ttk.Button(input_frame, text="▶ Jalankan Simulasi", command=run_simulation).pack(pady=15)
progress_label = tk.Label(input_frame, text="", bg="#f3f6fa", fg="gray")
progress_label.pack(pady=5)

# Output Tabs
output_frame = tk.LabelFrame(main_frame, text="Visualisasi Hasil",
                             bg="#f3f6fa", fg="#1f3c88", font=("Segoe UI", 11, "bold"))
output_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

tabs = ttk.Notebook(output_frame)
tabs.pack(fill="both", expand=True)

frame_plot1 = tk.Frame(tabs, bg="#f9f9fb")
frame_plot2 = tk.Frame(tabs, bg="#f9f9fb")
frame_plot3 = tk.Frame(tabs, bg="#f9f9fb")
frame_plot4 = tk.Frame(tabs, bg="#f9f9fb")

tabs.add(frame_plot1, text="📈 Profil Suhu")
tabs.add(frame_plot2, text="🌡️ Heatmap ΔT")
tabs.add(frame_plot3, text="🕒 Evolusi Waktu")
tabs.add(frame_plot4, text="⚙️ Analisis Stabilitas")

for f in [frame_plot1, frame_plot2, frame_plot3, frame_plot4]:
    f.pack_propagate(False)

tk.Label(root, text="© 2025 Fisika Komputasi II | BTCS Heat Diffusion Simulator",
         bg="#f3f6fa", fg="gray", font=("Segoe UI", 9)).pack(side="bottom", pady=5)

root.mainloop()