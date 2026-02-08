import sys
import math
import tkinter as tk
from tkinter import ttk
import threading


def safe_eval_scientific(expression):
    try:
        expression = expression.replace('×', '*').replace('÷', '/')
        safe_names = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
        safe_names['sqrt'] = math.sqrt
        safe_names['log'] = math.log
        res = eval(expression, {"__builtins__": None}, safe_names)
        return res
    except Exception:
        return None


class ScientificCalculator(tk.Tk):
    def __init__(self, title="Scientific Calculator"):
        super().__init__()
        self.title(title)
        self.geometry("920x520")
        self.resizable(False, False)

        # theme (vibrant)
        self.bg = "#0b1020"
        self.panel = "#071021"
        self.accent = "#ff2d95"
        self.fg = "#f8fafc"
        self.btn_bg = "#081025"

        self.configure(bg=self.bg)

        self.expr = tk.StringVar()
        self.preview = tk.StringVar()
        self.history = []

        main_frame = tk.Frame(self, bg=self.bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        calc_frame = tk.Frame(main_frame, bg=self.panel)
        calc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,8))

        entry = tk.Entry(calc_frame, textvariable=self.expr, font=("Inter", 26, 'bold'), bd=0, bg=self.btn_bg, fg=self.fg, insertbackground=self.fg, justify='right')
        entry.pack(fill=tk.X, padx=16, pady=(16,8), ipady=12)

        # rows of buttons
        rows = [
            ('sin','cos','tan','pi'),
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.','=','+'),
        ]

        for row in rows:
            rf = tk.Frame(calc_frame, bg=self.panel)
            rf.pack(fill=tk.X, padx=12, pady=6)
            for ch in row:
                b = tk.Button(rf, text=ch, font=("Inter", 14, 'bold'), bg=self.btn_bg, fg=self.fg, bd=0, activebackground=self.accent, activeforeground='#021026', command=lambda c=ch: self.on_press(c))
                b.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

        extra = tk.Frame(calc_frame, bg=self.panel)
        extra.pack(fill=tk.X, padx=12, pady=(8,12))
        pow_btn = tk.Button(extra, text='pow', font=("Inter", 12, 'bold'), bg=self.btn_bg, fg=self.fg, bd=0, command=lambda: self.on_press('**'))
        log_btn = tk.Button(extra, text='log', font=("Inter", 12, 'bold'), bg=self.btn_bg, fg=self.fg, bd=0, command=lambda: self.on_press('log('))
        sqrt_btn = tk.Button(extra, text='sqrt', font=("Inter", 12, 'bold'), bg=self.btn_bg, fg=self.fg, bd=0, command=lambda: self.on_press('sqrt('))
        clr = tk.Button(extra, text='C', font=("Inter", 12, 'bold'), bg='#ff6b6b', fg='white', bd=0, command=self.clear)
        pow_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
        log_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
        sqrt_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
        clr.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

        # right assistant
        right = tk.Frame(main_frame, width=360, bg=self.panel)
        right.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(right, text='Assistant', bg=self.panel, fg=self.fg, font=("Inter", 16, 'bold')).pack(anchor='nw', padx=12, pady=(12,6))
        tk.Label(right, textvariable=self.preview, bg=self.panel, fg='#ff94c2', font=("Inter", 14), wraplength=320, justify='left').pack(anchor='nw', padx=12)

        tk.Label(right, text='History', bg=self.panel, fg=self.fg, font=("Inter", 12)).pack(anchor='nw', padx=12, pady=(12,4))
        self.history_lb = tk.Listbox(right, bg=self.btn_bg, fg=self.fg, bd=0, activestyle='none', font=("Inter", 12), highlightthickness=0)
        self.history_lb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,12))
        self.history_lb.bind('<<ListboxSelect>>', self.on_history_select)

        entry.bind('<KeyRelease>', lambda e: threading.Thread(target=self.update_preview, daemon=True).start())
        self.bind_all('<Return>', lambda e: self.on_press('='))

    def on_press(self, ch):
        if ch == '=':
            self.evaluate()
            return
        if ch in ('sin','cos','tan','log','sqrt'):
            if ch == 'log':
                token = 'log('
            elif ch == 'sqrt':
                token = 'sqrt('
            else:
                token = f"{ch}("
            self.expr.set(self.expr.get() + token)
            return
        if ch == 'pi':
            self.expr.set(self.expr.get() + str(math.pi))
            return
        self.expr.set(self.expr.get() + ch)

    def clear(self):
        self.expr.set('')
        self.preview.set('')

    def update_preview(self):
        expr = self.expr.get()
        if not expr.strip():
            self.preview.set('Type an expression to see preview and tips')
            return
        res = safe_eval_scientific(expr)
        if res is None:
            self.preview.set('…')
        else:
            self.preview.set(f'Preview: {res}')

    def evaluate(self):
        expr = self.expr.get()
        res = safe_eval_scientific(expr)
        if res is None:
            self.expr.set('Error')
            return
        self.history.insert(0, f"{expr} = {res}")
        self.history_lb.insert(0, f"{expr} = {res}")
        self.expr.set(str(res))
        self.preview.set(f'Result: {res}')

    def on_history_select(self, ev):
        sel = ev.widget.curselection()
        if not sel:
            return
        text = ev.widget.get(sel[0])
        expr = text.split('=')[0].strip()
        self.expr.set(expr)
        self.update_preview()


def main(argv):
    title = "Scientific Calculator"
    if len(argv) > 1 and argv[1]:
        title = f"Scientific Calculator — {argv[1]}"
    app = ScientificCalculator(title=title)
    app.mainloop()


if __name__ == '__main__':
    main(sys.argv)
