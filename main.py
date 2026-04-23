import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime

import api
import utils

# Константы
HISTORY_FILE = 'history.json'

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.rates = {}
        self.currencies = []

        # Создание интерфейса
        self.create_widgets()

        # Загрузка истории
        self.load_history()

        # Получение курсов валют
        self.update_rates()

    def create_widgets(self):
        # Ввод суммы
        tk.Label(self.root, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.amount_var = tk.StringVar()
        self.entry_amount = tk.Entry(self.root, textvariable=self.amount_var)
        self.entry_amount.grid(row=0, column=1, padx=5, pady=5)

        # Валюта "из"
        tk.Label(self.root, text="Из:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.currency_from_var = tk.StringVar()
        self.cb_from = ttk.Combobox(self.root, textvariable=self.currency_from_var, state='readonly')
        self.cb_from.grid(row=1, column=1, padx=5, pady=5)

        # Валюта "в"
        tk.Label(self.root, text="В:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.currency_to_var = tk.StringVar()
        self.cb_to = ttk.Combobox(self.root, textvariable=self.currency_to_var, state='readonly')
        self.cb_to.grid(row=2, column=1, padx=5, pady=5)

        # Кнопка конвертации
        self.btn_convert = tk.Button(self.root, text="Конвертировать", command=self.convert_currency)
        self.btn_convert.grid(row=3, column=0, columnspan=2, pady=10)

        # Результат
        self.result_label = tk.Label(self.root, text="")
        self.result_label.grid(row=4, column=0, columnspan=2)

        # Таблица истории
        tk.Label(self.root, text="История:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.tree = ttk.Treeview(self.root, columns=("date", "from", "to", "amount", "result"), show='headings')
        self.tree.heading("date", text="Дата")
        self.tree.heading("from", text="Из")
        self.tree.heading("to", text="В")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("result", text="Результат")
        self.tree.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        # Чтобы таблица расширялась
        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def load_history(self):
        historico = utils.загрузить_историю(HISTORY_FILE)
        for item in historico:
            self.tree.insert('', 'end', values=(item['date'], item['from'], item['to'], item['amount'], item['result']))

    def update_rates(self):
        # Обновляем курсы в отдельном потоке, чтобы не "заморозить" интерфейс
        threading.Thread(target=self._fetch_rates).start()

    def _fetch_rates(self):
        rates = api.get_rates()
        if rates:
            self.rates = rates
            self.currencies = sorted(rates.keys())
            self.cb_from['values'] = self.currencies
            self.cb_to['values'] = self.currencies
            # Устанавливаем по умолчанию
            self.cb_from.current(0)
            self.cb_to.current(1)
        else:
            messagebox.showerror("Ошибка", "Не удалось получить курсы валют. Проверьте подключение к интернету.")

    def convert_currency(self):
        amount_str = self.amount_var.get()
        from_curr = self.currency_from_var.get()
        to_curr = self.currency_to_var.get()

        # Валидация
        if not utils.валидировать_сумму(amount_str):
            messagebox.showerror("Ошибка", "Введите положительное число для суммы.")
            return

        if from_curr not in self.rates or to_curr not in self.rates:
            messagebox.showerror("Ошибка", "Выберите валюты из списка.")
            return

        amount = float(amount_str)
        rate_from = self.rates[from_curr]
        rate_to = self.rates[to_curr]

        # Конвертация
        result = amount * (rate_to / rate_from)

        # Обновляем интерфейс
        self.result_label.config(text=f"{amount} {from_curr} = {result:.4f} {to_curr}")

        # Запись в историю
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        запись = {
            'date': now_str,
            'from': from_curr,
            'to': to_curr,
            'amount': amount,
            'result': f"{result:.4f}"
        }
        utils.добавить_в_историю(запись, HISTORY_FILE)
        self.tree.insert('', 'end', values=(запись['date'], from_curr, to_curr, amount, f"{result:.4f}"))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()