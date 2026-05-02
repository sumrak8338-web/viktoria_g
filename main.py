import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("800x550")
        
        # Данные: список тренировок
        self.trainings = []          # каждый элемент: dict с ключами id, date, type, duration
        self.max_id = 0
        
        # Файл по умолчанию для автосохранения
        self.default_file = "trainings.json"
        
        # Типы тренировок для выпадающего списка
        self.training_types = ["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Стретчинг", "Другое"]
        
        # Создание интерфейса
        self.create_widgets()
        
        # Загрузка данных из файла по умолчанию при старте
        self.load_from_file(self.default_file)
        self.refresh_display()
    
    def create_widgets(self):
        # --- Панель ввода новой тренировки ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=15, font=("Arial", 10))
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:", font=("Arial", 10)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(input_frame, textvariable=self.type_var, values=self.training_types, width=15, font=("Arial", 10))
        self.type_combobox.grid(row=0, column=3, padx=5, pady=5)
        self.type_combobox.set("Бег")
        
        # Длительность
        ttk.Label(input_frame, text="Длительность (мин):", font=("Arial", 10)).grid(row=0, column=4, sticky="e", padx=5, pady=5)
        self.duration_var = tk.StringVar()
        self.duration_entry = ttk.Entry(input_frame, textvariable=self.duration_var, width=10, font=("Arial", 10))
        self.duration_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка добавления
        self.add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training, width=15)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # --- Панель фильтрации ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по типу
        ttk.Label(filter_frame, text="Тип тренировки:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.filter_type_var = tk.StringVar()
        self.filter_type_combobox = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, values=["Все"] + self.training_types, width=15, font=("Arial", 10))
        self.filter_type_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.filter_type_combobox.set("Все")
        self.filter_type_combobox.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        self.filter_date_var = tk.StringVar()
        self.filter_date_entry = ttk.Entry(filter_frame, textvariable=self.filter_date_var, width=15, font=("Arial", 10))
        self.filter_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters, width=15)
        self.filter_btn.grid(row=0, column=4, padx=5, pady=5)
        
        self.reset_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters, width=15)
        self.reset_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # --- Таблица для отображения тренировок ---
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar_y = ttk.Scrollbar(tree_frame)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        columns = ("id", "date", "type", "duration")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                  yscrollcommand=scrollbar_y.set,
                                  xscrollcommand=scrollbar_x.set)
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)
        
        self.tree.pack(fill="both", expand=True)
        
        # --- Нижняя панель с кнопками ---
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.save_btn = ttk.Button(control_frame, text="Сохранить в JSON", command=self.save_to_file_dialog, width=15)
        self.save_btn.pack(side="left", padx=5)
        
        self.load_btn = ttk.Button(control_frame, text="Загрузить из JSON", command=self.load_from_file_dialog, width=15)
        self.load_btn.pack(side="left", padx=5)
        
        self.delete_btn = ttk.Button(control_frame, text="Удалить выбранную тренировку", command=self.delete_training, width=20)
        self.delete_btn.pack(side="right", padx=5)
        
        # Статистика
        self.stats_label = ttk.Label(control_frame, text="", font=("Arial", 9))
        self.stats_label.pack(side="right", padx=10)
        self.update_stats()
    
    # ---------- Работа с записями ----------
    def add_training(self):
        """Добавление новой тренировки с проверкой"""
        date_str = self.date_var.get().strip()
        training_type = self.type_var.get().strip()
        duration_str = self.duration_var.get().strip()
        
        # Проверка даты
        if not self.is_valid_date(date_str):
            messagebox.showerror("Ошибка", "Неверный формат даты.\nИспользуйте ГГГГ-ММ-ДД\nПример: 2024-12-25")
            return
        
        # Проверка длительности
        try:
            duration = float(duration_str)
            if duration <= 0:
                messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть числом")
            return
        
        # Генерация ID
        self.max_id += 1
        new_id = self.max_id
        
        # Создание записи
        training = {
            "id": new_id,
            "date": date_str,
            "type": training_type,
            "duration": duration
        }
        self.trainings.append(training)
        
        # Автосохранение в файл по умолчанию
        self.save_to_file(self.default_file)
        
        # Очистка полей ввода (дата и длительность)
        self.date_var.set("")
        self.duration_var.set("")
        
        # Обновление отображения
        self.refresh_display()
        self.update_stats()
        messagebox.showinfo("Успех", f"Тренировка добавлена:\n{training_type}, {duration} мин, {date_str}")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        item = self.tree.item(selected[0])
        record_id = item["values"][0]
        
        for i, tr in enumerate(self.trainings):
            if tr["id"] == record_id:
                confirm = messagebox.askyesno("Подтверждение",
                                             f"Удалить тренировку?\n{tr['type']}, {tr['duration']} мин, {tr['date']}")
                if confirm:
                    del self.trainings[i]
                break
        
        self.save_to_file(self.default_file)
        self.refresh_display()
        self.update_stats()
    
    # ---------- Фильтрация и отображение ----------
    def apply_filters(self):
        """Применяет фильтры и обновляет таблицу"""
        type_filter = self.filter_type_var.get().strip()
        date_filter = self.filter_date_var.get().strip()
        
        # Проверка даты фильтра
        if date_filter and not self.is_valid_date(date_filter):
            messagebox.showerror("Ошибка", "Неверный формат даты в фильтре.\nИспользуйте ГГГГ-ММ-ДД")
            return
        
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Фильтрация и отображение
        for tr in self.trainings:
            # Фильтр по типу
            if type_filter != "Все" and tr["type"] != type_filter:
                continue
            # Фильтр по дате
            if date_filter and tr["date"] != date_filter:
                continue
            
            self.tree.insert("", "end", values=(
                tr["id"],
                tr["date"],
                tr["type"],
                f"{tr['duration']}"
            ))
    
    def reset_filters(self):
        """Сброс всех фильтров"""
        self.filter_type_var.set("Все")
        self.filter_date_var.set("")
        self.apply_filters()
    
    def refresh_display(self):
        """Обновление отображения с учётом текущих фильтров"""
        self.apply_filters()
    
    def update_stats(self):
        """Обновление статистики (всего тренировок, общее время, среднее)"""
        total_count = len(self.trainings)
        if total_count > 0:
            total_duration = sum(tr["duration"] for tr in self.trainings)
            avg_duration = total_duration / total_count
            self.stats_label.config(text=f"Всего тренировок: {total_count} | Общее время: {total_duration:.0f} мин | Среднее: {avg_duration:.0f} мин")
        else:
            self.stats_label.config(text="Всего тренировок: 0")
    
    # ---------- Работа с JSON ----------
    def save_to_file(self, filename):
        """Сохранение данных в JSON"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
            return False
    
    def load_from_file(self, filename):
        """Загрузка данных из JSON"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.trainings = data
                # Восстановить максимальный ID
                if self.trainings:
                    self.max_id = max(tr.get("id", 0) for tr in self.trainings)
                else:
                    self.max_id = 0
                self.refresh_display()
                self.update_stats()
                return True
            else:
                messagebox.showwarning("Предупреждение", "Файл не содержит список тренировок")
                return False
        except FileNotFoundError:
            return False
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
            return False
    
    def save_to_file_dialog(self):
        """Диалог сохранения в выбранный файл"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.save_to_file(filename):
                messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
    
    def load_from_file_dialog(self):
        """Диалог загрузки из выбранного файла"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.load_from_file(filename):
                # Синхронизация с файлом по умолчанию
                self.save_to_file(self.default_file)
                messagebox.showinfo("Успех", f"Данные загружены из {filename}")
    
    # ---------- Вспомогательные функции ----------
    @staticmethod
    def is_valid_date(date_str):
        """Проверка формата даты ГГГГ-ММ-ДД"""
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
