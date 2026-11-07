import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SensorDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Data Analysis")
        self.root.geometry("1200x600")

        self.df = None
        self.required_cols = ['AccX', 'AccY', 'AccZ']
        self.colors = ['#4c72b0', '#dd8452', '#55a868']

        # Setup the control panel (Top)
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.load_btn = tk.Button(control_frame, text="Load CSV File", command=self.load_file, width=15)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        self.chart_type = tk.StringVar(value="Histograms")
        tk.Radiobutton(control_frame, text="Histograms", variable=self.chart_type, value="Histograms",
                       command=self.update_chart).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(control_frame, text="Box Plots", variable=self.chart_type, value="Box Plots",
                       command=self.update_chart).pack(side=tk.LEFT, padx=5)

        self.download_btn = tk.Button(control_frame, text="Download PNG", command=self.download_image,
                                      state=tk.DISABLED, width=15)
        self.download_btn.pack(side=tk.LEFT, padx=20)

        self.status_label = tk.Label(control_frame, text="Status: Awaiting file upload...", fg="gray")
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Setup the Matplotlib figure canvas (Bottom)
        self.fig, self.axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return

        try:
            temp_df = pd.read_csv(filepath)
            if not all(col in temp_df.columns for col in self.required_cols):
                messagebox.showerror("Error", f"CSV must contain columns: {self.required_cols}")
                return

            self.df = temp_df
            self.download_btn.config(state=tk.NORMAL)
            self.status_label.config(text=f"Status: Loaded {filepath.split('/')[-1]}", fg="green")
            self.update_chart()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{str(e)}")

    def update_chart(self):
        if self.df is None:
            return

        # Clear previous charts
        for ax in self.axes:
            ax.clear()

        current_type = self.chart_type.get()

        for i, col in enumerate(self.required_cols):
            data = self.df[col].dropna()

            if current_type == "Histograms":
                self.axes[i].hist(data, bins=50, color=self.colors[i], edgecolor='black', alpha=0.7)
                self.axes[i].set_title(f'{col} Histogram')
                self.axes[i].set_ylabel('Frequency')
            else:
                self.axes[i].boxplot(data, vert=True, patch_artist=True,
                                     boxprops=dict(facecolor=self.colors[i], color='black'),
                                     medianprops=dict(color='red', linewidth=2),
                                     flierprops=dict(marker='o', markerfacecolor='black', markersize=2, alpha=0.3))
                self.axes[i].set_title(f'{col} Box Plot')
                self.axes[i].set_xticks([1])
                self.axes[i].set_xticklabels([col])

            self.axes[i].grid(axis='y', alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

    def download_image(self):
        if self.df is None:
            return

        default_name = f"sensor_{self.chart_type.get().lower().replace(' ', '_')}.png"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG Image", "*.png")]
        )

        if filepath:
            try:
                self.fig.savefig(filepath, format="png", bbox_inches="tight")
                messagebox.showinfo("Success", "Image saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorDashboard(root)
    root.mainloop()