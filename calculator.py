import sys
import tkinter as tk

class BasicCalculator(tk.Tk):
    def __init__(self, title="Basic Calculator"):
        super().__init__()
        self.title(title)
        self.geometry("320x420")
        self.resizable(False, False)

        self.expr = tk.StringVar()

        entry = tk.Entry(self, textvariable=self.expr, font=("Segoe UI", 18), bd=4, relief=tk.RIDGE, justify='right')
        entry.pack(fill=tk.BOTH, padx=8, pady=(10,0), ipady=10)

        btns = [
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.','=','+'),
        ]

        for row in btns:
            frame = tk.Frame(self)
            frame.pack(expand=True, fill=tk.BOTH, padx=8, pady=4)
            for ch in row:
                b = tk.Button(frame, text=ch, font=("Segoe UI", 16), command=lambda c=ch: self.on_press(c))
                b.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)

        clear = tk.Button(self, text='C', font=("Segoe UI", 14), command=self.clear, bg='#f44336', fg='white')
        clear.pack(fill=tk.BOTH, padx=8, pady=(6,10))

        self.bind_all('<Return>', lambda e: self.on_press('='))
        self.bind_all('<KP_Enter>', lambda e: self.on_press('='))

    def on_press(self, ch):
        if ch == '=':
            self.evaluate()
        else:
            current = self.expr.get()
            self.expr.set(current + ch)

    def clear(self):
        self.expr.set('')

    def evaluate(self):
        try:
            # replace unicode operators if present
            expression = self.expr.get().replace('×', '*').replace('÷', '/')
            # safe-ish eval: only allow digits and operators
            result = eval(expression, {"__builtins__": None}, {})
            self.expr.set(str(result))
        except Exception:
            self.expr.set('Error')

def main(argv):
    title = "Basic Calculator"
    if len(argv) > 1 and argv[1]:
        title = f"Basic Calculator — {argv[1]}"
    app = BasicCalculator(title=title)
    app.mainloop()

if __name__ == '__main__':
    main(sys.argv)
