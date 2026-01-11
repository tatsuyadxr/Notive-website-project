import sys
import math
import tkinter as tk

class ScientificCalculator(tk.Tk):
    def __init__(self, title="Scientific Calculator"):
        super().__init__()
        self.title(title)
        self.geometry("420x520")
        self.resizable(False, False)

        self.expr = tk.StringVar()

        entry = tk.Entry(self, textvariable=self.expr, font=("Segoe UI", 18), bd=4, relief=tk.RIDGE, justify='right')
        entry.pack(fill=tk.BOTH, padx=8, pady=(10,0), ipady=10)

        rows = [
            ('sin','cos','tan','pi'),
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.','=','+'),
        ]

        for row in rows:
            frame = tk.Frame(self)
            frame.pack(expand=True, fill=tk.BOTH, padx=8, pady=4)
            for ch in row:
                b = tk.Button(frame, text=ch, font=("Segoe UI", 14), command=lambda c=ch: self.on_press(c))
                b.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)

        extra = tk.Frame(self)
        extra.pack(fill=tk.BOTH, padx=8, pady=(6,10))
        pow_btn = tk.Button(extra, text='pow', font=("Segoe UI", 12), command=lambda: self.on_press('**'))
        log_btn = tk.Button(extra, text='log', font=("Segoe UI", 12), command=lambda: self.on_press('log('))
        sqrt_btn = tk.Button(extra, text='sqrt', font=("Segoe UI", 12), command=lambda: self.on_press('sqrt('))
        clr = tk.Button(extra, text='C', font=("Segoe UI", 12), bg='#f44336', fg='white', command=self.clear)
        pow_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)
        log_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)
        sqrt_btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)
        clr.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)

        self.bind_all('<Return>', lambda e: self.on_press('='))

    def on_press(self, ch):
        if ch == '=':
            self.evaluate()
            return
        if ch in ('sin','cos','tan','log','sqrt'):
            # function calls
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

    def evaluate(self):
        try:
            expression = self.expr.get()
            # provide safe names: math functions
            safe_names = {k: getattr(math, k) for k in dir(math) if not k.startswith('_')}
            # add aliases
            safe_names['sqrt'] = math.sqrt
            safe_names['log'] = math.log
            result = eval(expression, {"__builtins__": None}, safe_names)
            self.expr.set(str(result))
        except Exception:
            self.expr.set('Error')

def main(argv):
    title = "Scientific Calculator"
    if len(argv) > 1 and argv[1]:
        title = f"Scientific Calculator — {argv[1]}"
    app = ScientificCalculator(title=title)
    app.mainloop()

if __name__ == '__main__':
    main(sys.argv)
