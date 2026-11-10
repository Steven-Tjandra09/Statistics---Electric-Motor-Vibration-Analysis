import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np


class KurtosisCalculatorApp:
    def __init__(self, parent_window):
        self.root = parent_window
        self.root.title("CSV Kurtosis Calculator")
        self.root.geometry("500x400")
        self.root.configure(padx=20, pady=20)

        self.df: pd.DataFrame | None = None

        self.btn_load = tk.Button(self.root, text="1. Load CSV File", command=self.load_csv, width=25)
        self.btn_load.pack(pady=5)

        self.lbl_file = tk.Label(self.root, text="No file selected", fg="gray")
        self.lbl_file.pack(pady=5)

        self.lbl_column = tk.Label(self.root, text="2. Select up to 3 Columns (Hold Ctrl/Cmd):")
        self.lbl_column.pack(pady=5)

        self.listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, height=6, width=40, state="disabled")
        self.listbox.pack(pady=5)

        self.btn_calc = tk.Button(self.root, text="3. Calculate Kurtosis", command=self.calculate_kurtosis,
                                  state="disabled", width=25)
        self.btn_calc.pack(pady=10)

        self.lbl_result = tk.Label(self.root, text="", font=("Arial", 10))
        self.lbl_result.pack(pady=5)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if not file_path or not isinstance(file_path, str):
            return

        try:
            temp_df = pd.read_csv(filepath_or_buffer=file_path)

            if isinstance(temp_df, pd.DataFrame):
                numeric_cols = temp_df.select_dtypes(include=[np.number]).columns.tolist()
                self.df = temp_df
            else:
                raise ValueError("Data could not be parsed as a DataFrame.")

            if not numeric_cols:
                messagebox.showerror("Error", "No numeric columns found in the CSV.")
                return

            self.lbl_file.config(text=file_path.split("/")[-1], fg="green")

            self.listbox.config(state="normal")
            self.listbox.delete(0, tk.END)
            for col in numeric_cols:
                self.listbox.insert(tk.END, col)

            self.btn_calc.config(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")

    def calculate_kurtosis(self):
        selected_indices = self.listbox.curselection()

        if not selected_indices:
            messagebox.showwarning("Warning", "Please select at least one column.")
            return

        if len(selected_indices) > 3:
            messagebox.showwarning("Limit Reached", "Please select a maximum of 3 columns.")
            return

        if self.df is None:
            return

        selected_cols = [self.listbox.get(i) for i in selected_indices]

        results_text = []

        try:
            for col_name in selected_cols:
                data = self.df[col_name].dropna().to_numpy(dtype=float)

                if len(data) < 4:
                    results_text.append(f"{col_name}: Not enough data")
                    continue

                mean = float(np.mean(data))
                m4 = float(np.mean((data - mean) ** 4))
                m2 = float(np.mean((data - mean) ** 2))

                if m2 == 0:
                    results_text.append(f"{col_name}: Zero variance")
                    continue

                pearson_kurtosis = m4 / (m2 ** 2)
                fisher_kurtosis = float(pearson_kurtosis - 3.0)

                if fisher_kurtosis > 0.5:
                    shape = "Leptokurtic"
                elif fisher_kurtosis < -0.5:
                    shape = "Platykurtic"
                else:
                    shape = "Mesokurtic"

                results_text.append(f"{col_name}: {fisher_kurtosis:.4f} ({shape})")

            # Update UI text with all selected column results
            self.lbl_result.config(text="\n".join(results_text))

        except Exception as e:
            messagebox.showerror("Calculation Error", f"An error occurred:\n{str(e)}")


if __name__ == "__main__":
    main_window = tk.Tk()
    app = KurtosisCalculatorApp(main_window)
    main_window.mainloop()