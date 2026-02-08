import sys
import tkinter as tk
from tkinter import ttk
import threading
import os


def safe_eval(expression, extra_names=None):
    # Minimal safe eval for calculator preview. Only math operators and numbers allowed.
    try:
        expression = expression.replace('×', '*').replace('÷', '/')
        # restrict builtins
        res = eval(expression, {"__builtins__": None}, extra_names or {})
        return res
    except Exception:
        return None


class BasicCalculator(tk.Tk):
    def __init__(self, title="Basic Calculator"):
        super().__init__()
        self.title(title)
        self.geometry("720x420")
        self.resizable(False, False)

        # load icon from static folder
        try:
            base = os.path.dirname(__file__) or os.getcwd()
            icon_path = os.path.join(base, "static", "icon.png")
            if not os.path.isfile(icon_path):
                icon_path = os.path.join(os.getcwd(), "static", "icon.png")
            if os.path.isfile(icon_path):
                icon_surf = tk.PhotoImage(file=icon_path)
                self.iconphoto(False, icon_surf)
        except Exception:
            pass

        
        self.bg = "#0b1020"
        self.panel = "#071021"
        self.accent = "#ff2d95"   
        self.fg = "#f8fafc"
        self.btn_bg = "#0b1220"

        self.configure(bg=self.bg)

        self.expr = tk.StringVar()
        self.preview = tk.StringVar()
        self.history = []

        main_frame = tk.Frame(self, bg=self.bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Left: calculator
        calc_frame = tk.Frame(main_frame, bg=self.panel)
        calc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,8))

        entry = tk.Entry(calc_frame, textvariable=self.expr, font=("Inter", 26, 'bold'), bd=0, bg=self.btn_bg, fg=self.fg, insertbackground=self.fg, justify='right')
        entry.pack(fill=tk.X, padx=16, pady=(16,8), ipady=12)

        # keypad area
        keys = [
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.','=','+'),
        ]

        for row in keys:
            rowf = tk.Frame(calc_frame, bg=self.panel)
            rowf.pack(fill=tk.X, padx=12, pady=6)
            for ch in row:
                b = tk.Button(rowf, text=ch, font=("Inter", 18, 'bold'), bg=self.btn_bg, fg=self.fg, bd=0, activebackground=self.accent, activeforeground='#021026', command=lambda c=ch: self.on_press(c))
                b.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

        bottom = tk.Frame(calc_frame, bg=self.panel)
        bottom.pack(fill=tk.X, padx=12, pady=(8,16))
        clear = tk.Button(bottom, text='C', font=("Inter", 16, 'bold'), bg='#ff6b6b', fg='white', bd=0, command=self.clear)
        clear.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
        explain = tk.Button(bottom, text='Explain', font=("Inter", 14, 'bold'), bg=self.accent, fg='#021026', bd=0, command=self.explain_expression)
        explain.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

        # Right: assistant / history
        right = tk.Frame(main_frame, width=320, bg=self.panel)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(right, text='Assistant', bg=self.panel, fg=self.fg, font=("Inter", 16, 'bold')).pack(anchor='nw', padx=12, pady=(12,6))
        preview_lbl = tk.Label(right, textvariable=self.preview, bg=self.panel, fg='#ff94c2', font=("Inter", 14), wraplength=280, justify='left')
        preview_lbl.pack(anchor='nw', padx=12)

        tk.Label(right, text='History', bg=self.panel, fg=self.fg, font=("Inter", 12)).pack(anchor='nw', padx=12, pady=(12,4))
        self.history_lb = tk.Listbox(right, bg=self.btn_bg, fg=self.fg, bd=0, activestyle='none', font=("Inter", 12), highlightthickness=0)
        self.history_lb.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,12))
        self.history_lb.bind('<<ListboxSelect>>', self.on_history_select)

        # bindings
        self.bind_all('<Return>', lambda e: self.on_press('='))
        entry.bind('<KeyRelease>', lambda e: self.on_type())

    def on_press(self, ch):
        if ch == '=':
            self.evaluate()
        else:
            current = self.expr.get()
            self.expr.set(current + ch)
            # update preview
            self.update_preview()

    def on_type(self):
        # live preview updated on typing (run in thread to avoid UI freeze)
        threading.Thread(target=self.update_preview, daemon=True).start()

    def update_preview(self):
        expr = self.expr.get()
        if not expr.strip():
            self.preview.set('Type an expression to see a live preview')
            return
        res = safe_eval(expr)
        if res is None:
            self.preview.set('…')
        else:
            self.preview.set(f'Result preview: {res}')

    def clear(self):
        self.expr.set('')
        self.preview.set('')

    def evaluate(self):
        try:
            expression = self.expr.get().replace('×', '*').replace('÷', '/')
            result = safe_eval(expression)
            if result is None:
                self.expr.set('Error')
            else:
                self.history.insert(0, f"{expression} = {result}")
                self.history_lb.insert(0, f"{expression} = {result}")
                self.expr.set(str(result))
                self.preview.set(f'Result: {result}')
        except Exception:
            self.expr.set('Error')

    def explain_expression(self):
        expr = self.expr.get()
        res = safe_eval(expr)
        if res is None:
            self.preview.set('Could not evaluate expression to explain.')
            return
        # simple, non-AI explanation for transparency
        explanation = f'Computed value of "{expr}" is {res}. This used the built-in evaluator (no external AI).'
        self.preview.set(explanation)

    def on_history_select(self, ev):
        sel = ev.widget.curselection()
        if not sel:
            return
        text = ev.widget.get(sel[0])
        # load left side (expression) into input
        expr = text.split('=')[0].strip()
        self.expr.set(expr)
        self.update_preview()


def main(argv):
    title = "Basic Calculator"
    if len(argv) > 1 and argv[1]:
        title = f"Basic Calculator — {argv[1]}"
    app = BasicCalculator(title=title)
    app.mainloop()


if __name__ == '__main__':
    main(sys.argv)
