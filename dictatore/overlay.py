from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dictatore.events import EventBus


class Overlay:
    def __init__(self, bus: EventBus, config: dict) -> None:
        self._bus = bus
        self._config = config
        self._visible = False
        self._text = ""
        self._window: Any | None = None

    def show(self) -> None:
        if not self._config.get("SHOW_OVERLAY", True) or self._window is not None:
            return
        try:
            import tkinter as tk
            self._window = tk.Tk()
            self._window.overrideredirect(True)
            self._window.attributes("-topmost", True)
            self._window.attributes("-alpha", self._config.get("OVERLAY_OPACITY", 0.9))
            self._window.configure(bg="#222222")

            pos = self._config.get("OVERLAY_POSITION", "top-center")
            sw = self._window.winfo_screenwidth()
            win_w = min(sw - 40, self._config.get("OVERLAY_WIDTH", 60) * 10)
            win_h = 40
            x = (sw - win_w) // 2 if "center" in pos else 20
            y = 10 if "top" in pos else self._window.winfo_screenheight() - win_h - 10
            self._window.geometry(f"{int(win_w)}x{int(win_h)}+{int(x)}+{int(y)}")

            font_size = self._config.get("OVERLAY_FONT_SIZE", 14)
            self._label = tk.Label(
                self._window,
                text="Dictatore",
                fg="#cccccc",
                bg="#222222",
                font=("TkFixedFont", font_size),
                wraplength=win_w - 20,
                anchor="w",
            )
            self._label.pack(fill="both", expand=True, padx=10, pady=5)

            self._window.update()
        except ImportError:
            self._window = None

    def update_text(self, text: str) -> None:
        if self._window is not None and hasattr(self, "_label"):
            self._label.config(text=text)
            self._window.update_idletasks()

    def hide(self) -> None:
        if self._window is not None:
            try:
                self._window.destroy()
            except Exception:
                pass
            self._window = None
        self._text = ""
