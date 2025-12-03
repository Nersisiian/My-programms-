import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class DembelTimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Дембель Таймер")
        
        self.label = tk.Label(master, text="Введите дату окончания службы (ГГГГ-ММ-ДД):")
        self.label.pack(pady=10)

        self.entry = tk.Entry(master)
        self.entry.pack(pady=10)

        self.button = tk.Button(master, text="Посчитать", command=self.calculate_remaining_days)
        self.button.pack(pady=10)

        self.result_label = tk.Label(master, text="")
        self.result_label.pack(pady=10)

    def calculate_remaining_days(self):
        end_date_str = self.entry.get()
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            today = datetime.now()
            remaining_days = (end_date - today).days

            if remaining_days < 0:
                self.result_label.config(text="Вы уже демобилизованы!")
            else:
                self.result_label.config(text=f"Осталось {remaining_days} дней до дембеля.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную дату в формате ГГГГ-ММ-ДД.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DembelTimerApp(root)
    root.mainloop()
