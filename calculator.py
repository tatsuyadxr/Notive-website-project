import sys
import tkinter as tk

class ModernButton(tk.Button):
    """Custom button with modern phone-style appearance"""
    def __init__(self, parent, text, command=None, is_operator=False, is_equals=False, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        self.is_operator = is_operator
        self.is_equals = is_equals
        self.normal_bg = kwargs.get('bg', '#FF9800' if is_operator else '#333333')
        self.hover_bg = kwargs.get('hover_bg', '#FFB74D' if is_operator else '#444444')
        
        if is_equals:
            self.normal_bg = '#4CAF50'
            self.hover_bg = '#66BB6A'
        elif is_operator:
            self.normal_bg = '#FF9800'
            self.hover_bg = '#FFB74D'
        
        self.config(
            bg=self.normal_bg,
            fg='white',
            font=("Segoe UI", 14, "bold"),
            bd=0,
            highlightthickness=0,
            activebackground=self.hover_bg,
            activeforeground='white',
            padx=10,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):
        self.config(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.config(bg=self.normal_bg)

class BasicCalculator(tk.Tk):
    def __init__(self, title="Basic Calculator"):
        super().__init__()
        self.title(title)
        self.geometry("360x540")
        self.resizable(False, False)
        
        # Modern dark theme
        self.config(bg='#1a1a1a')

        self.expr = tk.StringVar()

        # Display entry
        entry = tk.Entry(
            self, 
            textvariable=self.expr, 
            font=("Segoe UI", 32, "bold"), 
            bd=0, 
            relief=tk.FLAT, 
            justify='right',
            bg='#2a2a2a',
            fg='#ffffff',
            insertbackground='#ffffff'
        )
        entry.pack(fill=tk.BOTH, padx=12, pady=20, ipady=20)

        btns = [
            ('7','8','9','/'),
            ('4','5','6','*'),
            ('1','2','3','-'),
            ('0','.','=','+'),
        ]

        button_frame = tk.Frame(self, bg='#1a1a1a')
        button_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8,12))

        for row in btns:
            frame = tk.Frame(button_frame, bg='#1a1a1a')
            frame.pack(expand=True, fill=tk.BOTH, pady=6)
            for ch in row:
                is_op = ch in ('/', '*', '-', '+')
                is_eq = ch == '='
                b = ModernButton(
                    frame, 
                    text=ch, 
                    command=lambda c=ch: self.on_press(c),
                    is_operator=is_op,
                    is_equals=is_eq
                )
                b.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=4)

        clear = ModernButton(
            self, 
            text='C', 
            command=self.clear,
            bg='#f44336'
        )
        clear.config(bg='#f44336', hover_bg='#ef5350')
        clear.pack(fill=tk.BOTH, padx=8, pady=(0,12))

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
