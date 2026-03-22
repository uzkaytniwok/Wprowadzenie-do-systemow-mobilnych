import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading


class BaseStationSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Symulator Stacji Bazowej - Dynamika Rzeczywista")

        self.params = {
            "S": tk.IntVar(value=5),
            "lambda": tk.DoubleVar(value=0.8),
            "N": tk.DoubleVar(value=10.0),
            "sigma": tk.DoubleVar(value=2.0),
            "min": tk.DoubleVar(value=1.0),
            "max": tk.DoubleVar(value=30.0),
            "queue_len": tk.IntVar(value=10),
            "sim_time": tk.IntVar(value=60)
        }

        self.running = False
        self.active_calls = []
        self.waiting_queue = []

        self.history_ro = []
        self.history_q = []
        self.history_w = []
        self.time_axis = []

        self.setup_ui()

    def setup_ui(self):
        side_panel = tk.LabelFrame(self.root, text="Parametry", padx=10, pady=10)
        side_panel.pack(side=tk.LEFT, fill=tk.Y)

        for i, (key, var) in enumerate(self.params.items()):
            tk.Label(side_panel, text=f"{key}:").grid(row=i, column=0, sticky="w")
            tk.Entry(side_panel, textvariable=var, width=8).grid(row=i, column=1)

        self.btn_start = tk.Button(side_panel, text="START", command=self.start_sim, bg="green", fg="white", height=2)
        self.btn_start.grid(row=9, columnspan=2, pady=10, sticky="ew")

        self.chan_frame = tk.LabelFrame(self.root, text="Zajętość kanałów", padx=5, pady=5)
        self.chan_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.canvas_status = tk.Canvas(self.chan_frame, width=120, height=400, bg="#f0f0f0")
        self.canvas_status.pack()

        self.fig, (self.ax_ro, self.ax_q, self.ax_w) = plt.subplots(3, 1, figsize=(5, 7))
        self.fig.tight_layout(pad=2.0)
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas_plot.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def draw_channels(self, occupied):
        self.canvas_status.delete("all")
        s_max = self.params["S"].get()
        h = 380 / s_max
        for i in range(s_max):
            color = "#ff4444" if i < occupied else "#44ff44"
            self.canvas_status.create_rectangle(10, i * h + 5, 110, (i + 1) * h - 2, fill=color, outline="black")
            status_txt = "ZAJĘTY" if i < occupied else "WOLNY"
            self.canvas_status.create_text(60, i * h + h / 2, text=f"K{i + 1}: {status_txt}", font=("Arial", 8))

    def start_sim(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.run_logic, daemon=True).start()

    def run_logic(self):
        s_max = self.params["S"].get()
        q_max = self.params["queue_len"].get()
        t_max = self.params["sim_time"].get()
        lam = self.params["lambda"].get()

        self.active_calls = []
        self.waiting_queue = []
        self.history_ro, self.history_q, self.history_w, self.time_axis = [], [], [], []

        total_wait_time = 0
        calls_processed = 0
        start_t = time.time()

        with open("wyniki_symulacji.txt", "w") as f:
            f.write(f"SYMULACJA - Parametry: S={s_max}, L={lam}, N={self.params['N'].get()}\n")
            f.write("Sekunda | Ro | Q | W\n")

            for sec in range(t_max + 1):
                if not self.running: break

                self.active_calls = [end for end in self.active_calls if end > sec]

                num_new = np.random.poisson(lam)
                for _ in range(num_new):
                    dur = np.random.normal(self.params["N"].get(), self.params["sigma"].get())
                    dur = max(self.params["min"].get(), min(self.params["max"].get(), dur))

                    if len(self.active_calls) < s_max:
                        self.active_calls.append(sec + dur)
                        calls_processed += 1
                    elif len(self.waiting_queue) < q_max:
                        self.waiting_queue.append((sec, dur))

                while len(self.active_calls) < s_max and self.waiting_queue:
                    arr_t, dur = self.waiting_queue.pop(0)
                    wait = sec - arr_t
                    total_wait_time += wait
                    calls_processed += 1
                    self.active_calls.append(sec + dur)

                ro = len(self.active_calls) / s_max if s_max > 0 else 0
                q_now = len(self.waiting_queue)
                w_avg = total_wait_time / calls_processed if calls_processed > 0 else 0

                self.time_axis.append(sec)
                self.history_ro.append(ro)
                self.history_q.append(q_now)
                self.history_w.append(w_avg)

                f.write(f"{sec} | {ro:.2f} | {q_now} | {w_avg:.2f}\n")

                self.root.after(0, lambda r=ro, o=len(self.active_calls): [self.update_plots(), self.draw_channels(o)])

                time.sleep(max(0, (start_t + sec + 1) - time.time()))

        self.running = False
        messagebox.showinfo("Koniec", "Zakończono symulację a wyniki zostaly zapisane w pliku txt.")

    def update_plots(self):
        # Wykres Ro
        self.ax_ro.clear()
        self.ax_ro.plot(self.time_axis, self.history_ro, 'g-')
        self.ax_ro.set_ylabel("Ro (Zajętość)")
        self.ax_ro.set_ylim(-0.1, 1.1)

        self.ax_q.clear()
        self.ax_q.step(self.time_axis, self.history_q, 'r-', where='post')
        self.ax_q.set_ylabel("Q (Kolejka)")

        self.ax_w.clear()
        self.ax_w.plot(self.time_axis, self.history_w, 'b-')
        self.ax_w.set_ylabel("W (Oczekiwanie)")

        self.canvas_plot.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseStationSimulator(root)
    root.mainloop()
