import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Константы
API_KEY = 'YOUR_API_KEY_HERE'  # Вставьте свой API-ключ
API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD'
HISTORY_FILE = 'history.json'


class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.currencies = []
        self.load_currencies()
        self.history = []

        self.create_widgets()
        self.load_history()

    def load_currencies(self):
        # Получение списка валют (можно взять из API или задать вручную)
        try:
            response = requests.get(API_URL)
            data = response.json()
            self.currencies = list(data['conversion_rates'].keys())
        except Exception:
            # В случае ошибки, задать стандартный список валют
            self.currencies = ['USD', 'EUR', 'GBP', 'RUB', 'JPY']
    
    def create_widgets(self):
        # Ввод суммы
        ttk.Label(self.root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        # Валюта из
        ttk.Label(self.root, text="Из:").grid(row=1, column=0, padx=5, pady=5)
        self.currency_from = ttk.Combobox(self.root, values=self.currencies, state='readonly')
        self.currency_from.current(0)
        self.currency_from.grid(row=1, column=1, padx=5, pady=5)

        # Валюта в
        ttk.Label(self.root, text="В:").grid(row=2, column=0, padx=5, pady=5)
        self.currency_to = ttk.Combobox(self.root, values=self.currencies, state='readonly')
        self.currency_to.current(1)
        self.currency_to.grid(row=2, column=1, padx=5, pady=5)

        # Конвертировать кнопка
        self.convert_button = ttk.Button(self.root, text="Конвертировать", command=self.convert_currency)
        self.convert_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Результат
        self.result_label = ttk.Label(self.root, text="Результат: ")
        self.result_label.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        # Таблица истории
        self.tree = ttk.Treeview(self.root, columns=('from', 'to', 'amount', 'result'), show='headings')
        self.tree.heading('from', text='Из валюты')
        self.tree.heading('to', text='В валюту')
        self.tree.heading('amount', text='Сумма')
        self.tree.heading('result', text='Результат')
        self.tree.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        # Очистить историю
        self.clear_button = ttk.Button(self.root, text="Очистить историю", command=self.clear_history)
        self.clear_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    def load_history(self):
        # Загрузка истории из файла
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                self.history = json.load(f)
            for item in self.history:
                self.tree.insert('', 'end', values=(item['from'], item['to'], item['amount'], item['result']))

    def save_history(self):
        # Сохранение истории в файл
        with open(HISTORY_FILE, 'w') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def convert_currency(self):
        amount_str = self.amount_entry.get()
        # Проверка корректности ввода
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительное число")
            return

        from_curr = self.currency_from.get()
        to_curr = self.currency_to.get()

        # Получение курса
        try:
            response = requests.get(API_URL)
            data = response.json()
            rate_from = data['conversion_rates'][from_curr]
            rate_to = data['conversion_rates'][to_curr]
        except Exception:
            messagebox.showerror("Ошибка", "Не удалось получить курс валют")
            return

        # Конвертация
        result = amount * rate_to / rate_from
        self.result_label.config(text=f"Результат: {result:.2f} {to_curr}")

        # Добавление в историю
        entry = {
            'from': from_curr,
            'to': to_curr,
            'amount': amount,
            'result': round(result, 2)
        }
        self.history.append(entry)
        self.tree.insert('', 'end', values=(from_curr, to_curr, amount, round(result, 2)))
        self.save_history()

    def clear_history(self):
        self.history.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()