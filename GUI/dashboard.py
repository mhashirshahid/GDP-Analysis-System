from __future__ import annotations

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List

_C = {
    "bg":        "#010308",
    "surface":   "#030610",
    "sidebar":   "#020508",
    "card":      "#060d18",
    "border":    "#0d1e30",
    "text":      "#ddeeff",
    "subtext":   "#3a5878",
    "muted":     "#162030",
    "accent":    "#00aaff",
    "accent2":   "#ff6a35",
    "active_bg": "#07182a",
    "hover_bg":  "#051420",
}

_ICONS = ["🏆", "🧊", "🏎", "🌍", "🌌", "🔥", "⚠", "🎼"]
_HINTS = [
    "Top performers by GDP",
    "Lowest GDP countries",
    "Growth rate over range",
    "Continental averages",
    "Global GDP over time",
    "Fastest growing region",
    "Declining economies",
    "Share of world GDP",
]


class GUIDashboard(tk.Tk):
    def __init__(self, figures: List[tuple]) -> None:
        super().__init__()
        self._figures      = figures
        self._index        = 0
        self._total        = len(figures)
        self._canvas_ref   = None
        self._item_widgets = []
        self._setup_window()
        self._build_ui()
        if self._figures:
            self._show_chart(0)

    def _setup_window(self) -> None:
        self.title("GDP Analysis System — Phase 2")
        self.configure(bg=_C["bg"])
        self.geometry("1320x820")
        self.minsize(1000, 640)
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 1320) // 2
        y = (self.winfo_screenheight() - 820)  // 2
        self.geometry(f"1320x820+{x}+{y}")

    def _build_ui(self) -> None:
        self._build_topbar()
        body = tk.Frame(self, bg=_C["bg"])
        body.pack(fill=tk.BOTH, expand=True)
        self._build_sidebar(body)
        tk.Frame(body, bg=_C["border"], width=1).pack(fill=tk.Y, side=tk.LEFT)
        self._build_canvas_area(body)
        self._bind_keys()

    # Top bar

    def _build_topbar(self) -> None:
        bar = tk.Frame(self, bg=_C["sidebar"], height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="◈",
                 font=("DejaVu Sans", 18, "bold"),
                 bg=_C["sidebar"], fg=_C["accent"]).pack(side=tk.LEFT, padx=(18, 6))

        tk.Label(bar, text="GDP Analysis System",
                 font=("DejaVu Sans", 13, "bold"),
                 bg=_C["sidebar"], fg=_C["text"]).pack(side=tk.LEFT)

        tk.Label(bar, text="  ·  Phase 2",
                 font=("DejaVu Sans", 10),
                 bg=_C["sidebar"], fg=_C["subtext"]).pack(side=tk.LEFT)

        tk.Label(bar, text="← →  navigate    1–8  jump    Esc  close",
                 font=("DejaVu Sans", 8),
                 bg=_C["sidebar"], fg=_C["subtext"]).pack(side=tk.RIGHT, padx=22)

        tk.Frame(self, bg=_C["border"], height=1).pack(fill=tk.X)

    # Sidebar

    def _build_sidebar(self, parent: tk.Frame) -> None:
        sidebar = tk.Frame(parent, bg=_C["sidebar"], width=256)
        sidebar.pack(fill=tk.Y, side=tk.LEFT)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="CHARTS",
                 font=("DejaVu Sans", 7, "bold"),
                 bg=_C["sidebar"], fg=_C["subtext"]).pack(anchor=tk.W, padx=18, pady=(16, 4))

        tk.Frame(sidebar, bg=_C["border"], height=1).pack(fill=tk.X, padx=14, pady=(0, 6))

        list_frame = tk.Frame(sidebar, bg=_C["sidebar"])
        list_frame.pack(fill=tk.BOTH, expand=True)
        list(map(lambda i: self._build_item(list_frame, i), range(self._total)))

        tk.Frame(sidebar, bg=_C["border"], height=1).pack(fill=tk.X, padx=14, pady=6)
        self._build_nav(sidebar)

    def _build_item(self, parent: tk.Frame, i: int) -> None:
        title = self._figures[i][0] if i < len(self._figures) else f"Chart {i+1}"
        short = (title[:28] + "…") if len(title) > 28 else title
        icon  = _ICONS[i] if i < len(_ICONS) else "📊"
        hint  = _HINTS[i] if i < len(_HINTS) else ""

        row = tk.Frame(parent, bg=_C["sidebar"], cursor="hand2")
        row.pack(fill=tk.X, padx=6, pady=1)

        num = tk.Label(row, text=f"{i+1:02d}",
                       font=("DejaVu Sans Mono", 8),
                       bg=_C["sidebar"], fg=_C["subtext"],
                       width=3, anchor=tk.W)
        num.pack(side=tk.LEFT, padx=(10, 2), pady=8)

        ico = tk.Label(row, text=icon,
                       font=("DejaVu Sans", 12),
                       bg=_C["sidebar"], fg=_C["muted"])
        ico.pack(side=tk.LEFT, padx=(0, 8))

        texts = tk.Frame(row, bg=_C["sidebar"])
        texts.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=5)

        lbl = tk.Label(texts, text=short,
                       font=("DejaVu Sans", 8, "bold"),
                       bg=_C["sidebar"], fg=_C["text"],
                       anchor=tk.W, justify=tk.LEFT)
        lbl.pack(anchor=tk.W)

        sub = tk.Label(texts, text=hint,
                       font=("DejaVu Sans", 7),
                       bg=_C["sidebar"], fg=_C["subtext"],
                       anchor=tk.W)
        sub.pack(anchor=tk.W)

        widgets = [row, num, ico, texts, lbl, sub]
        self._item_widgets.append(widgets)

        def _bind(w, idx=i):
            w.bind("<Button-1>", lambda e: self._show_chart(idx))
            w.bind("<Enter>",    lambda e: self._hover(idx, True))
            w.bind("<Leave>",    lambda e: self._hover(idx, False))
        list(map(_bind, widgets))

    def _build_nav(self, parent: tk.Frame) -> None:
        nav = tk.Frame(parent, bg=_C["sidebar"])
        nav.pack(fill=tk.X, padx=12, pady=(2, 4))

        btn = dict(font=("DejaVu Sans", 13, "bold"),
                   bg=_C["card"], activebackground=_C["active_bg"],
                   bd=0, padx=0, pady=10, relief=tk.FLAT, cursor="hand2")

        self._prev_btn = tk.Button(nav, text="◀", fg=_C["subtext"],
                                   activeforeground=_C["text"],
                                   command=self._prev, **btn)
        self._prev_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self._next_btn = tk.Button(nav, text="▶", fg=_C["accent"],
                                   activeforeground=_C["text"],
                                   command=self._next, **btn)
        self._next_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        self._counter = tk.StringVar(value=f"1 / {self._total}")
        tk.Label(parent, textvariable=self._counter,
                 font=("DejaVu Sans", 8),
                 bg=_C["sidebar"], fg=_C["subtext"]).pack(pady=(6, 14))

    # Canvas area

    def _build_canvas_area(self, parent: tk.Frame) -> None:
        area = tk.Frame(parent, bg=_C["bg"])
        area.pack(fill=tk.BOTH, expand=True)

        titlebar = tk.Frame(area, bg=_C["bg"])
        titlebar.pack(fill=tk.X, pady=(8, 0))

        self._title_var = tk.StringVar()
        tk.Label(titlebar, textvariable=self._title_var,
                 font=("DejaVu Sans", 11, "bold"),
                 bg=_C["bg"], fg=_C["text"]).pack(side=tk.LEFT, padx=18)

        self._canvas_frame = tk.Frame(area, bg=_C["bg"])
        self._canvas_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 12))

    # State updates

    def _show_chart(self, index: int) -> None:
        if not self._figures:
            return
        index = max(0, min(index, self._total - 1))
        self._index = index
        title, fig  = self._figures[index]

        if self._canvas_ref:
            self._canvas_ref.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=self._canvas_frame)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.configure(bg=_C["bg"], highlightthickness=0)
        widget.pack(fill=tk.BOTH, expand=True)
        self._canvas_ref = canvas

        self._title_var.set(title)
        self._counter.set(f"{index + 1} / {self._total}")
        self._update_sidebar(index)
        self._update_nav(index)

    def _update_sidebar(self, active: int) -> None:
        def _apply(pair):
            i, ws = pair
            on  = i == active
            bg  = _C["active_bg"] if on else _C["sidebar"]
            ws[0].configure(bg=bg)
            ws[1].configure(bg=bg, fg=_C["accent"]  if on else _C["subtext"])
            ws[2].configure(bg=bg, fg=_C["accent2"] if on else _C["muted"])
            ws[3].configure(bg=bg)
            ws[4].configure(bg=bg, fg=_C["accent"]  if on else _C["text"])
            ws[5].configure(bg=bg, fg=_C["subtext"])
        list(map(_apply, enumerate(self._item_widgets)))

    def _hover(self, i: int, entering: bool) -> None:
        if i == self._index:
            return
        bg = _C["hover_bg"] if entering else _C["sidebar"]
        list(map(lambda w: w.configure(bg=bg), self._item_widgets[i]))

    def _update_nav(self, index: int) -> None:
        can_prev = index > 0
        can_next = index < self._total - 1
        self._prev_btn.configure(
            fg=_C["accent"] if can_prev else _C["subtext"],
            state=tk.NORMAL if can_prev else tk.DISABLED)
        self._next_btn.configure(
            fg=_C["accent"] if can_next else _C["subtext"],
            state=tk.NORMAL if can_next else tk.DISABLED)

    def _bind_keys(self) -> None:
        self.bind("<Left>",   lambda _: self._prev())
        self.bind("<Right>",  lambda _: self._next())
        self.bind("<Escape>", lambda _: self.destroy())
        list(map(
            lambda i: self.bind(str(i + 1), lambda e, idx=i: self._show_chart(idx)),
            range(min(self._total, 9)),
        ))

    def _prev(self) -> None:
        if self._index > 0:
            self._show_chart(self._index - 1)

    def _next(self) -> None:
        if self._index < self._total - 1:
            self._show_chart(self._index + 1)