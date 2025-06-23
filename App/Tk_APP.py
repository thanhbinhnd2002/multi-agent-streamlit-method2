# ✅ tk_app.py — Giao diện mô phỏng đẹp hơn với tkinter, hỗ trợ vẽ mạng và tô màu gene OncoKB

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import os
import sys
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import các thư viện nằm ngoài file chính
import os
import numpy as np
from joblib import Parallel, delayed
from multiprocessing import cpu_count

sys.path.append(os.path.abspath(".."))

from Simulate.Simulate_Model_Method_2 import import_network, simulate
from functions.Compare import match_with_oncokb_pubmed

if False:
    import matplotlib
    import matplotlib.backends.backend_tkagg
    import joblib
    import openpyxl
    import tqdm
    import PIL._tkinter_finder

# ✅ Cấu hình đường dẫn nếu chạy bằng file .exe
if getattr(sys, 'frozen', False):
    # Đường dẫn thực thi khi chạy exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FONT = ("Segoe UI", 10)
BTN_STYLE = {"font": FONT, "bg": "#E0E0E0", "activebackground": "#D0D0D0", "relief": "raised"}


class SimulationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-agent Outside Competitive Dynamics Model")
        self.root.geometry("1150x680")

        self.network_path = None
        self.network_graph = None
        self.result_df = None
        self.matched_df = None

        # Frame trái: điều khiển
        control_frame = tk.Frame(root, padx=15, pady=15, bg="#F5F5F5")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(control_frame, text="Chọn file mạng .txt", font=("Segoe UI", 11, "bold"), bg="#F5F5F5").pack(anchor="w", pady=(0, 3))
        tk.Button(control_frame, text="📂 Chọn file mạng", command=self.choose_file, **BTN_STYLE).pack(fill="x")
        self.file_label = tk.Label(control_frame, text="Chưa chọn file", fg="#1a73e8", font=FONT, bg="#F5F5F5")
        self.file_label.pack(anchor="w", pady=(0, 6))
        self.draw_btn = tk.Button(control_frame, text="📡 Vẽ mạng", command=self.draw_network, state=tk.DISABLED, **BTN_STYLE)
        self.draw_btn.pack(fill="x", pady=(0, 15))

        # Tham số
        tk.Label(control_frame, text="Tham số mô hình", font=("Segoe UI", 11, "bold"), bg="#F5F5F5").pack(anchor="w", pady=(5, 3))
        self.epsilon = self.add_param_slider(control_frame, "Epsilon", 0.05, 1.0, 0.1)
        self.delta = self.add_param_slider(control_frame, "Delta", 0.01, 1.0, 0.2)
        self.max_iter = self.add_param_entry(control_frame, "Max Iter", 50)
        self.tol = self.add_param_entry(control_frame, "Tolerance", 1e-4)
        self.n_beta = self.add_param_entry(control_frame, "N_Beta", 2)
        self.top_n = self.add_param_entry(control_frame, "Top N (lọc đối chiếu)", 100)

        # Nút chức năng
        tk.Button(control_frame, text="🚀 Chạy mô phỏng", command=self.run_simulation, **BTN_STYLE).pack(fill="x", pady=(15, 4))
        tk.Button(control_frame, text="💾 Lưu kết quả CSV", command=self.save_result, **BTN_STYLE).pack(fill="x")
        tk.Button(control_frame, text="🔍 Đối chiếu OncoKB / PubMed", command=self.match_results, **BTN_STYLE).pack(fill="x", pady=4)
        tk.Button(control_frame, text="📥 Lưu kết quả đối chiếu", command=self.save_matched, **BTN_STYLE).pack(fill="x")

        # Frame kết quả
        result_frame = tk.Frame(root, padx=10, pady=10)
        result_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(result_frame, text="📊 Kết quả mô phỏng", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10))

        self.tree = ttk.Treeview(result_frame, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def add_param_slider(self, parent, name, from_, to, default):
        tk.Label(parent, text=f"{name}:", font=FONT, bg="#F5F5F5").pack(anchor="w")
        var = tk.DoubleVar(value=default)
        tk.Scale(parent, from_=from_, to=to, resolution=0.01, orient=tk.HORIZONTAL, variable=var).pack(fill="x")
        return var

    def add_param_entry(self, parent, name, default):
        tk.Label(parent, text=f"{name}:", font=FONT, bg="#F5F5F5").pack(anchor="w")
        var = tk.StringVar(value=str(default))
        tk.Entry(parent, textvariable=var, font=FONT).pack(fill="x")
        return var

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if path:
            self.network_path = path
            self.network_graph = import_network(path)
            self.file_label.config(text=os.path.basename(path))
            self.draw_btn.config(state=tk.NORMAL)

    def run_simulation(self):
        if not self.network_path:
            messagebox.showwarning("Lỗi", "Vui lòng chọn file mạng.")
            return
        try:
            epsilon = float(self.epsilon.get())
            delta = float(self.delta.get())
            max_iter = int(self.max_iter.get())
            tol = float(self.tol.get())
            n_beta = int(self.n_beta.get())

            df = simulate(
                file_path=self.network_path,
                EPSILON=epsilon,
                DELTA=delta,
                MAX_ITER=max_iter,
                TOL=tol,
                N_BETA=n_beta,
                output_folder=None
            )
            self.result_df = df
            self.display_results(df)
        except Exception as e:
            messagebox.showerror("Lỗi mô phỏng", str(e))

    def display_results(self, df):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        for _, row in df.iterrows():
            tags = ("oncokb",) if "In OncoKB" in df.columns and row.get("In OncoKB", False) else ()
            self.tree.insert("", tk.END, values=list(row), tags=tags)

        self.tree.tag_configure("oncokb", background="#FFDDDD")

    def save_result(self):
        if self.result_df is None:
            messagebox.showwarning("Chưa có kết quả", "Bạn cần chạy mô phỏng trước.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.result_df.to_csv(path, index=False)
            messagebox.showinfo("Đã lưu", f"Đã lưu kết quả vào\n{path}")

    def save_matched(self):
        if self.matched_df is None:
            messagebox.showwarning("Chưa có đối chiếu", "Bạn cần thực hiện đối chiếu trước.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.matched_df.to_csv(path, index=False)
            messagebox.showinfo("Đã lưu", f"Đã lưu kết quả đối chiếu vào\n{path}")

    def match_results(self):
        if self.result_df is None:
            messagebox.showwarning("Chưa có kết quả", "Bạn cần chạy mô phỏng trước.")
            return
        try:
            top_n = int(self.top_n.get()) if self.top_n.get().isdigit() else None
            matched = match_with_oncokb_pubmed(self.result_df, top_n=top_n)
            if matched.empty:
                messagebox.showinfo("Đối chiếu", "Không tìm thấy gene nào khớp với OncoKB hoặc PubMed.")
            else:
                self.matched_df = matched
                self.display_results(matched)
        except Exception as e:
            messagebox.showerror("Lỗi đối chiếu", str(e))

    def draw_network(self):
        if self.network_graph is None:
            messagebox.showwarning("Chưa có mạng", "Vui lòng chọn file mạng trước.")
            return

        fig, ax = plt.subplots(figsize=(7, 6))
        pos = nx.spring_layout(self.network_graph, seed=42)
        nx.draw_networkx_nodes(self.network_graph, pos, node_size=20, node_color="#1f78b4", ax=ax)
        nx.draw_networkx_edges(self.network_graph, pos, edge_color="#cccccc", width=0.5, ax=ax)
        ax.set_title("Biểu diễn mạng gene", fontsize=12)
        ax.axis("off")

        top = tk.Toplevel(self.root)
        top.title("Biểu đồ mạng")
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()
