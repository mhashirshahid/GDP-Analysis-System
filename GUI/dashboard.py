from __future__ import annotations
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from typing import List

_BG      = "#0d1117"
_SURFACE = "#161b22"
_BORDER  = "#30363d"
_TEXT    = "#e6edf3"
_SUBTEXT = "#8b949e"
_ACCENT  = "#58a6ff"


class GUIDashboard(tk.Tk):
    def __init__(self, figures: List[tuple]) -> None:
        super().__init__()
        self._figures = figures
        self._index   = 0
        self._total   = len(figures)
        self._setup_window()
        self._build_ui()
        self._show_chart(0)

    def _setup_window(self) -> None:
        self.title("GDP Analysis System — Dashboard")
        self.configure(bg=_BG)
        self.geometry("1200x750")
        self.minsize(900, 600)
        self.resizable(True, True)
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 1200) // 2
        y = (self.winfo_screenheight() - 750)  // 2
        self.geometry(f"1200x750+{x}+{y}")

    def _build_ui(self) -> None:
        # Header
        header = tk.Frame(self, bg=_SURFACE, pady=10)
        header.pack(fill=tk.X, side=tk.TOP)
        tk.Label(header, text="GDP Analysis Dashboard",
                 font=("DejaVu Sans", 16, "bold"),
                 bg=_SURFACE, fg=_ACCENT).pack(side=tk.LEFT, padx=20)

        self._counter_var = tk.StringVar(value=f"1 / {self._total}")
        tk.Label(header, textvariable=self._counter_var,
                 font=("DejaVu Sans", 12),
                 bg=_SURFACE, fg=_SUBTEXT).pack(side=tk.RIGHT, padx=20)

        # Title bar
        title_bar = tk.Frame(self, bg=_BG, pady=6)
        title_bar.pack(fill=tk.X, side=tk.TOP)
        self._title_var = tk.StringVar(value="")
        tk.Label(title_bar, textvariable=self._title_var,
                 font=("DejaVu Sans", 13, "bold"),
                 bg=_BG, fg=_TEXT).pack(side=tk.LEFT, padx=24)

        #Canvas area
        self._canvas_frame = tk.Frame(self, bg=_BG)
        self._canvas_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 4))
        self._canvas_widget = None

        #Bottom navigation
        nav = tk.Frame(self, bg=_SURFACE, pady=10)
        nav.pack(fill=tk.X, side=tk.BOTTOM)

        btn_cfg = dict(font=("DejaVu Sans", 13, "bold"),
                       bg=_SURFACE, fg=_ACCENT,
                       activebackground=_BORDER, activeforeground=_TEXT,
                       bd=0, padx=18, pady=6, cursor="hand2", relief=tk.FLAT)

        self._prev_btn = tk.Button(nav, text="◀  Previous",
                                   command=self._prev, **btn_cfg)
        self._prev_btn.pack(side=tk.LEFT, padx=30)

        self._next_btn = tk.Button(nav, text="Next  ▶",
                                   command=self._next, **btn_cfg)
        self._next_btn.pack(side=tk.RIGHT, padx=30)

        #Dot indicators
        self._dot_frame = tk.Frame(nav, bg=_SURFACE)
        self._dot_frame.pack(side=tk.TOP, expand=True)
        self._dots = []
        self._build_dots()

        #Keyboard bindings
        self.bind("<Left>",  lambda _: self._prev())
        self.bind("<Right>", lambda _: self._next())
        self.bind("<Escape>", lambda _: self.destroy())

    def _build_dots(self) -> None:
        for i in range(self._total):
            dot = tk.Label(self._dot_frame, text="●",
                           font=("DejaVu Sans", 10), bg=_SURFACE,
                           fg=_ACCENT if i == 0 else _BORDER, cursor="hand2")
            dot.pack(side=tk.LEFT, padx=3)
            dot.bind("<Button-1>", lambda e, idx=i: self._show_chart(idx))
            self._dots.append(dot)

    def _show_chart(self, index: int) -> None:
        if not self._figures:
            return
        index = max(0, min(index, self._total - 1))
        self._index = index
        title, fig = self._figures[index]

        if self._canvas_widget:
            self._canvas_widget.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=self._canvas_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.configure(bg=_BG, highlightthickness=0)
        widget.pack(fill=tk.BOTH, expand=True)
        self._canvas_widget = canvas

        self._title_var.set(title)
        self._counter_var.set(f"{index + 1} / {self._total}")
        self._update_dots(index)
        self._update_buttons(index)

    def _update_dots(self, active: int) -> None:
        list(map(lambda pair: pair[0].configure(
                     fg=_ACCENT if pair[1] == active else _BORDER),
                 zip(self._dots, range(self._total))))

    def _update_buttons(self, index: int) -> None:
        self._prev_btn.configure(
            fg=_ACCENT if index > 0 else _BORDER,
            state=tk.NORMAL if index > 0 else tk.DISABLED)
        self._next_btn.configure(
            fg=_ACCENT if index < self._total - 1 else _BORDER,
            state=tk.NORMAL if index < self._total - 1 else tk.DISABLED)

    def _prev(self) -> None:
        if self._index > 0:
            self._show_chart(self._index - 1)

    def _next(self) -> None:
        if self._index < self._total - 1:
            self._show_chart(self._index + 1)