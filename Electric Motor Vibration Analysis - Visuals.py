import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SensorDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor Data Analysis (Comparison Mode)")
        self.root.geometry("1200x600")

        # Storing two dataframes for comparison
        self.df1 = None
        self.df2 = None
        self.file1_name = ""
        self.file2_name = ""

        self.required_cols = ['AccX', 'AccY', 'AccZ']
        # File 1 is Blue, File 2 is now Red
        self.file_colors = ['#4c72b0', '#d62728']

        # Setup the control panel (Top)
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(side="top", fill="x")

        # Two load buttons
        self.load_btn1 = tk.Button(control_frame, text="Load File 1", command=lambda: self.load_file(1), width=10)
        self.load_btn1.pack(side="left", padx=2)

        self.load_btn2 = tk.Button(control_frame, text="Load File 2", command=lambda: self.load_file(2), width=10)
        self.load_btn2.pack(side="left", padx=10)

        self.chart_type = tk.StringVar(value="Histograms")
        tk.Radiobutton(control_frame, text="Histograms", variable=self.chart_type, value="Histograms",
                       command=self.update_chart).pack(side="left", padx=5)
        tk.Radiobutton(control_frame, text="Box Plots", variable=self.chart_type, value="Box Plots",
                       command=self.update_chart).pack(side="left", padx=5)
        tk.Radiobutton(control_frame, text="Combined Box Plot", variable=self.chart_type, value="Combined Box Plot",
                       command=self.update_chart).pack(side="left", padx=5)

        # Toggle for Square Download
        self.force_square_var = tk.BooleanVar(value=True)
        self.square_chk = tk.Checkbutton(control_frame, text="Force Square", variable=self.force_square_var)
        self.square_chk.pack(side="left", padx=10)

        self.download_btn = tk.Button(control_frame, text="Download PNG", command=self.download_image,
                                      state="disabled", width=15)
        self.download_btn.pack(side="left", padx=5)

        self.status_label = tk.Label(control_frame, text="Status: Awaiting files...", fg="gray")
        self.status_label.pack(side="right", padx=10)

        # Setup the Matplotlib figure canvas (Bottom)
        self.fig = plt.figure(figsize=(12.0, 5.0))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side="bottom", fill="both", expand=True)

    def load_file(self, file_num):
        filepath = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filepath:
            return

        try:
            temp_df: pd.DataFrame = pd.read_csv(filepath)

            if not all(col in temp_df.columns for col in self.required_cols):
                messagebox.showerror("Error", f"CSV must contain columns: {self.required_cols}")
                return

            filename = filepath.split('/')[-1]
            if file_num == 1:
                self.df1 = temp_df
                self.file1_name = filename
            else:
                self.df2 = temp_df
                self.file2_name = filename

            self.download_btn.config(state="normal")

            # Update status text to show both files if they exist
            status_text = []
            if self.df1 is not None: status_text.append(f"F1: {self.file1_name}")
            if self.df2 is not None: status_text.append(f"F2: {self.file2_name}")
            self.status_label.config(text=" | ".join(status_text), fg="green")

            self.update_chart()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{str(e)}")

    def update_chart(self):
        if self.df1 is None and self.df2 is None:
            return

        self.fig.clear()
        current_type = self.chart_type.get()

        # Build dynamic lists based on which files are loaded
        dfs = []
        labels = []
        if self.df1 is not None:
            dfs.append(self.df1)
            labels.append("File 1")
        if self.df2 is not None:
            dfs.append(self.df2)
            labels.append("File 2")

        if current_type == "Combined Box Plot":
            ax = self.fig.add_subplot(111)
            data_to_plot = []
            tick_labels = []
            box_colors = []

            for col in self.required_cols:
                for j, df in enumerate(dfs):
                    data_to_plot.append(df[col].dropna())
                    tick_labels.append(f"{col}\n({labels[j]})")
                    box_colors.append(self.file_colors[j])

            bplot = ax.boxplot(data_to_plot, vert=True, patch_artist=True,
                               medianprops=dict(color='black', linewidth=2),
                               flierprops=dict(marker='o', markerfacecolor='black', markersize=2, alpha=0.3))

            ax.set_xticklabels(tick_labels)

            for patch, color in zip(bplot['boxes'], box_colors):
                patch.set_facecolor(color)

            ax.set_title('Combined Accelerometer Box Plots')
            ax.grid(axis='y', alpha=0.3)

        else:
            axes = self.fig.subplots(nrows=1, ncols=3)

            for i, col in enumerate(self.required_cols):
                if current_type == "Histograms":
                    for j, df in enumerate(dfs):
                        axes[i].hist(df[col].dropna(), bins=50, color=self.file_colors[j],
                                     edgecolor='black', alpha=0.6, label=labels[j])
                    axes[i].set_title(f'{col} Histogram')
                    axes[i].set_ylabel('Frequency')
                    if len(dfs) > 1:
                        axes[i].legend()

                elif current_type == "Box Plots":
                    data_list = [df[col].dropna() for df in dfs]
                    bplot = axes[i].boxplot(data_list, vert=True, patch_artist=True,
                                            medianprops=dict(color='black', linewidth=2),
                                            flierprops=dict(marker='o', markerfacecolor='black', markersize=2,
                                                            alpha=0.3))
                    axes[i].set_title(f'{col} Box Plot')
                    axes[i].set_xticks(range(1, len(labels) + 1))
                    axes[i].set_xticklabels(labels)

                    for j, patch in enumerate(bplot['boxes']):
                        patch.set_facecolor(self.file_colors[j])

                axes[i].grid(axis='y', alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

    def download_image(self):
        if self.df1 is None and self.df2 is None:
            return

        default_name = f"sensor_{self.chart_type.get().lower().replace(' ', '_')}.png"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG Image", "*.png")]
        )

        if filepath:
            try:
                original_size = self.fig.get_size_inches()
                is_square = self.force_square_var.get()

                # Apply square dimensions if checked
                if is_square:
                    self.fig.set_size_inches(8.0, 8.0)

                self.fig.savefig(filepath, format="png", bbox_inches="tight")

                # Revert immediately to prevent UI stretching
                if is_square:
                    self.fig.set_size_inches(original_size)
                    self.canvas.draw()

                msg = "Square image saved successfully." if is_square else "Image saved successfully."
                messagebox.showinfo("Success", msg)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorDashboard(root)
    root.mainloop()