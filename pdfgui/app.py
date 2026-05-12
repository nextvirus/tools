"""主窗口：Notebook + 各功能标签页挂载。"""

from __future__ import annotations

import sys
import threading
from typing import Literal, cast
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .pdf_to_img import pdf_to_images
from .photo_bg import default_output_path, replace_photo_background, warmup_rembg_session
from .watermark_pdf import add_watermark

from . import theme
from .tabs import mount_all_tabs


class PdfToolsApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("tools")
        self.minsize(560, 420)
        self.geometry("820x780")
        self.configure(bg=theme.U_BG)

        try:
            self.call("tk", "scaling", 1.22)
        except tk.TclError:
            pass

        theme.apply_ttk_theme(self)

        top_wrap = ttk.Frame(self, style="TFrame", padding=(16, 12, 16, 0))
        top_wrap.pack(fill=tk.X)

        top = ttk.Frame(top_wrap, style="TitleBar.TFrame", padding=(20, 16, 20, 16))
        top.pack(fill=tk.X)
        accent = tk.Frame(top, bg=theme.U_PRIMARY, width=4)
        accent.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 14))
        titles = tk.Frame(top, bg=theme.U_CARD)
        titles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(titles, text="tools", font=theme.FONT_TITLE, fg=theme.U_TEXT, bg=theme.U_CARD).pack(anchor=tk.W)
        tk.Label(
            titles,
            text="为 PDF 添加水印、导出页面为图片，或更换照片底色",
            font=theme.FONT_SUB,
            fg=theme.U_TEXT_SEC,
            bg=theme.U_CARD,
        ).pack(anchor=tk.W, pady=(6, 0))

        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, padx=16, pady=(8, 0))

        body = ttk.Frame(self, padding=(16, 12, 16, 16))
        body.pack(fill=tk.BOTH, expand=True)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        nb = ttk.Notebook(body)
        nb.grid(row=0, column=0, sticky=tk.NSEW)

        mount_all_tabs(self, nb)

        def _warm_rembg() -> None:
            def _run() -> None:
                try:
                    warmup_rembg_session()
                except Exception:
                    pass

            threading.Thread(target=_run, daemon=True).start()

        self.after(600, _warm_rembg)

    def attach_scale_resize(self, parent: tk.Misc, reserve: int = 200) -> None:
        """改 Scale.length 会连锁触发 Configure；用防抖 + 子控件快照 + 宽度去抖，避免重入与 RecursionError。"""
        last_w = [-1]
        debounce_id: list[int | None] = [None]

        def _apply() -> None:
            debounce_id[0] = None
            try:
                W = int(parent.winfo_width())
            except (tk.TclError, ValueError):
                return
            if W < reserve + 48:
                return
            if abs(W - last_w[0]) < 3:
                return
            last_w[0] = W
            L = max(W - reserve - 20, 72)
            try:
                kids = list(parent.winfo_children())
            except tk.TclError:
                return
            for ch in kids:
                if isinstance(ch, tk.Scale):
                    try:
                        ch.configure(length=L)
                    except tk.TclError:
                        pass

        def _on_configure(_event: object | None = None) -> None:
            if debounce_id[0] is not None:
                try:
                    self.after_cancel(debounce_id[0])
                except tk.TclError:
                    pass
            debounce_id[0] = self.after(50, _apply)

        parent.bind("<Configure>", _on_configure, add="+")
        self.after_idle(_on_configure)

    def slider_row(
        self,
        parent: ttk.Frame,
        row: int,
        var: tk.DoubleVar | tk.IntVar,
        from_: float,
        to: float,
        resolution: float,
        label_fmt,
    ) -> None:
        from . import widgets

        parent.columnconfigure(0, minsize=190, weight=0)
        parent.columnconfigure(1, weight=1)

        lab = ttk.Label(parent, anchor=tk.W, style="SliderLab.TLabel")
        lab.grid(row=row, column=0, sticky=tk.W, padx=(0, 10), pady=6)

        def _on_slide(_e: tk.Event | None = None) -> None:
            sc.configure(activebackground=theme.U_SLIDER_THUMB_HI)

        def _on_release(_e: tk.Event | None = None) -> None:
            sc.configure(activebackground=theme.U_SLIDER_THUMB)

        sc = tk.Scale(
            parent,
            variable=var,
            from_=from_,
            to=to,
            orient=tk.HORIZONTAL,
            resolution=resolution,
            length=280,
            showvalue=0,
            bg=theme.U_CARD,
            fg="#0d1117",
            troughcolor=theme.U_SLIDER_TROUGH,
            highlightthickness=1,
            highlightbackground=theme.U_BORDER_STRONG,
            highlightcolor=theme.U_SLIDER_THUMB,
            activebackground=theme.U_SLIDER_THUMB,
            bd=0,
            sliderrelief=tk.RAISED,
            width=22,
            sliderlength=26,
            font=theme.FONT_UI,
        )
        sc.bind("<ButtonPress-1>", _on_slide)
        sc.bind("<ButtonRelease-1>", _on_release)
        sc.grid(row=row, column=1, sticky=tk.EW, pady=6)
        widgets.bind_slider_label(var, lab, label_fmt)

    def form_row(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        widget,
        *,
        btn=None,
        btn_sticky=tk.E + tk.N + tk.S,
        entry_sticky=tk.EW,
        entry_colspan: int = 1,
    ) -> int:
        ttk.Label(parent, text=label, style="Card.TLabel", anchor=tk.W).grid(
            row=row, column=0, sticky=tk.W, pady=10, padx=(0, 8)
        )
        widget.grid(
            row=row,
            column=1,
            columnspan=entry_colspan,
            sticky=entry_sticky,
            padx=(0, 8),
            pady=10,
        )
        if btn is not None:
            btn.grid(row=row, column=2, sticky=btn_sticky, padx=(4, 0), pady=10)
        return row + 1

    def config_form_columns(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, minsize=120, weight=0)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, minsize=108, weight=0)

    def scroll_tab_shell(self, nb: ttk.Notebook) -> tuple[ttk.Frame, tk.Canvas, ttk.Frame]:
        shell = ttk.Frame(nb)
        shell.columnconfigure(0, weight=1)
        shell.rowconfigure(0, weight=1)
        canvas = tk.Canvas(shell, highlightthickness=0, bg=theme.U_CARD, bd=0)
        vsb = ttk.Scrollbar(shell, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        inner = ttk.Frame(canvas, style="Card.TFrame", padding=(24, 20, 24, 16))
        inner_id = canvas.create_window((0, 0), window=inner, anchor=tk.NW)

        def _on_inner_configure(_event: tk.Event | None = None) -> None:
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox)

        inner.bind("<Configure>", _on_inner_configure)

        def _on_canvas_configure(event: tk.Event) -> None:
            w = max(int(event.width), 200)
            canvas.itemconfigure(inner_id, width=w)
            canvas.after_idle(_on_inner_configure)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)

        def _canvas_wheel_win(event: tk.Event) -> None:
            d = getattr(event, "delta", 0) or 0
            if d:
                canvas.yview_scroll(int(-1 * (d / 120)), "units")

        if sys.platform == "darwin":
            canvas.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * e.delta), "units"))
        elif sys.platform.startswith("linux"):
            canvas.bind("<Button-4>", lambda _e: canvas.yview_scroll(-1, "units"))
            canvas.bind("<Button-5>", lambda _e: canvas.yview_scroll(1, "units"))
        else:
            canvas.bind("<MouseWheel>", _canvas_wheel_win)

        return shell, canvas, inner

    def bind_scroll_wheel(self, widget: tk.Misc, canvas: tk.Canvas) -> None:
        def _wheel_win(event: tk.Event) -> None:
            d = getattr(event, "delta", 0) or 0
            if d:
                canvas.yview_scroll(int(-1 * (d / 120)), "units")

        if sys.platform == "darwin":
            widget.bind("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * e.delta), "units"), add="+")
        elif sys.platform.startswith("linux"):
            widget.bind("<Button-4>", lambda _e: canvas.yview_scroll(-1, "units"), add="+")
            widget.bind("<Button-5>", lambda _e: canvas.yview_scroll(1, "units"), add="+")
        else:
            widget.bind("<MouseWheel>", _wheel_win, add="+")
        for ch in widget.winfo_children():
            self.bind_scroll_wheel(ch, canvas)

    def pick_wm_in(self) -> None:
        from . import widgets

        widgets.browse_pdf(self.wm_in)
        p = self.wm_in.get().strip()
        if p and not self.wm_out.get().strip():
            src = Path(p)
            self.wm_out.set(str(src.parent / f"{src.stem}_watermarked.pdf"))

    def pick_im_in(self) -> None:
        from . import widgets

        widgets.browse_pdf(self.im_in)
        p = self.im_in.get().strip()
        if p and not self.im_out.get().strip():
            src = Path(p)
            self.im_out.set(str(src.parent / f"{src.stem}_images"))

    def _maybe_fill_photo_out(self) -> None:
        inp = self.ph_in.get().strip()
        if not inp or not Path(inp).is_file():
            return
        bg = self.ph_color.get().strip().lower()
        if bg not in ("red", "blue", "white"):
            return
        out = self.ph_out.get().strip()
        cur = default_output_path(inp, cast(Literal["red", "blue", "white"], bg))
        presets = [
            default_output_path(inp, "red"),
            default_output_path(inp, "blue"),
            default_output_path(inp, "white"),
        ]
        if not out:
            self.ph_out.set(cur)
        elif out in presets:
            self.ph_out.set(cur)

    def pick_ph_in(self) -> None:
        from . import widgets

        p = widgets.pick_raster_image_path()
        if not p:
            return
        self.ph_in.set(p)
        self._maybe_fill_photo_out()

    def fill_simfang(self) -> None:
        if theme._WIN_SIMFANG.is_file():
            self.wm_fontfile.set(str(theme._WIN_SIMFANG))
        else:
            messagebox.showinfo("提示", "未找到仿宋字体，请手动选择。")

    def fill_msyh(self) -> None:
        if theme._WIN_MSYH.is_file():
            self.wm_fontfile.set(str(theme._WIN_MSYH))
        else:
            messagebox.showinfo("提示", "未找到微软雅黑，请手动选择。")

    def run_watermark(self) -> None:
        def job() -> None:
            inp = self.wm_in.get().strip()
            outp = self.wm_out.get().strip()
            if not inp or not outp:
                raise ValueError("请选择输入 PDF 并指定输出路径。")
            ff = self.wm_fontfile.get().strip() or None
            g = max(0.0, min(1.0, float(self.wm_gray.get())))
            color = (g, g, g)
            add_watermark(
                inp,
                outp,
                self.wm_text.get(),
                fontname="helv",
                fontfile=ff,
                fontsize=float(self.wm_size.get()),
                opacity=max(0.0, min(1.0, float(self.wm_opacity.get()))),
                angle=float(self.wm_angle.get()),
                color=color,
                gap_x=float(self.wm_gapx.get()),
                gap_y=float(self.wm_gapy.get()),
            )
            self.after(0, lambda p=outp: self._done_wm(p))

        self._wm_btn.configure(state=tk.DISABLED)

        def wrap() -> None:
            try:
                job()
            except Exception as e:
                self.after(0, lambda err=e: self._fail("水印失败", err, self._wm_btn))

        threading.Thread(target=wrap, daemon=True).start()

    def _done_wm(self, outp: str) -> None:
        messagebox.showinfo("完成", f"已保存:\n{outp}")
        self._wm_btn.configure(state=tk.NORMAL)

    def run_image(self) -> None:
        def job() -> None:
            inp = self.im_in.get().strip()
            outd = self.im_out.get().strip()
            if not inp or not outd:
                raise ValueError("请选择输入 PDF 与输出目录。")
            pages = self.im_pages.get().strip() or None
            paths = pdf_to_images(
                inp,
                outd,
                image_format=self.im_fmt.get().strip().lower(),
                dpi=float(self.im_dpi.get()),
                pages_spec=pages,
                jpg_quality=int(self.im_jpgq.get()),
            )
            self.after(0, lambda d=outd, n=len(paths): self._done_im(d, n))

        self._im_btn.configure(state=tk.DISABLED)

        def wrap() -> None:
            try:
                job()
            except Exception as e:
                self.after(0, lambda err=e: self._fail("导出失败", err, self._im_btn))

        threading.Thread(target=wrap, daemon=True).start()

    def _done_im(self, outd: str, n: int) -> None:
        messagebox.showinfo("完成", f"共 {n} 张\n输出目录:\n{outd}")
        self._im_btn.configure(state=tk.NORMAL)

    def run_photo_bg(self) -> None:
        def job() -> None:
            inp = self.ph_in.get().strip()
            if not inp:
                raise ValueError("请选择照片。")
            bg = self.ph_color.get().strip().lower()
            if bg not in ("red", "blue", "white"):
                raise ValueError("请选择底色：红 / 蓝 / 白。")
            bg_key = cast(Literal["red", "blue", "white"], bg)
            outp = self.ph_out.get().strip()
            if not outp:
                outp = default_output_path(inp, bg_key)
            else:
                p = Path(outp)
                if not p.suffix:
                    outp = str(p.with_suffix(".png"))
            replace_photo_background(inp, outp, bg_key)
            self.after(0, lambda p=outp: self._done_ph(p))

        self._ph_btn.configure(state=tk.DISABLED)

        def wrap() -> None:
            try:
                job()
            except Exception as e:
                self.after(0, lambda err=e: self._fail("换底失败", err, self._ph_btn))

        threading.Thread(target=wrap, daemon=True).start()

    def _done_ph(self, outp: str) -> None:
        messagebox.showinfo("完成", f"已保存:\n{outp}")
        self._ph_btn.configure(state=tk.NORMAL)

    def _fail(self, title: str, err: Exception, btn: ttk.Button) -> None:
        btn.configure(state=tk.NORMAL)
        messagebox.showerror(title, str(err))


def main() -> None:
    app = PdfToolsApp()
    app.mainloop()
