#!/usr/bin/env python3
"""
E-Commerce Product Description Generator — Desktop App
Tkinter dark-theme UI powered by Ollama (llama3.2)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import requests
import json
import os
from datetime import datetime

# ─── Constants ────────────────────────────────────────────────────────────────

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_TAGS  = "http://localhost:11434/api/tags"
DEFAULT_MODEL = "llama3.2"

TONES = ["Professional", "Casual", "Luxury", "Playful"]

TONE_HINTS = {
    "Professional": "Formal, authoritative, and trustworthy.",
    "Casual":       "Friendly, conversational, and approachable.",
    "Luxury":       "Elegant, exclusive, and aspirational.",
    "Playful":      "Fun, energetic, and witty.",
}

# ─── Dark Palette ─────────────────────────────────────────────────────────────

BG          = "#1a1a2e"   # deep navy background
BG2         = "#16213e"   # slightly darker panels
CARD        = "#0f3460"   # card / section bg
ACCENT      = "#e94560"   # primary accent (red-pink)
ACCENT2     = "#533483"   # secondary accent (purple)
FG          = "#eaeaea"   # primary text
FG2         = "#a0a0b0"   # secondary / muted text
INPUT_BG    = "#22223b"   # input field background
INPUT_FG    = "#f2f2f2"   # input text
BORDER      = "#2d2d4e"   # subtle border
GREEN       = "#2ec4b6"   # success / ready
YELLOW      = "#f4a261"   # warning
FONT_MAIN   = ("Segoe UI", 10)
FONT_BOLD   = ("Segoe UI", 10, "bold")
FONT_TITLE  = ("Segoe UI", 15, "bold")
FONT_LABEL  = ("Segoe UI", 9)
FONT_MONO   = ("Consolas", 10)

# ─── Helpers ──────────────────────────────────────────────────────────────────

def build_prompt(name, category, features, audience, tone):
    tone_desc = {
        "Professional": "formal, authoritative, and trustworthy — ideal for B2B or technical products",
        "Casual":       "friendly, conversational, and approachable — great for everyday consumer goods",
        "Luxury":       "elegant, exclusive, and aspirational — perfect for premium or high-end products",
        "Playful":      "fun, energetic, and witty — best for lifestyle, kids, or trendy products",
    }[tone]

    feats = "\n".join(f"  - {f.strip()}" for f in features if f.strip()) or "  - (none provided)"
    aud   = audience.strip() or "General consumers"

    return f"""You are an expert e-commerce copywriter. Generate a compelling product listing.

PRODUCT DETAILS:
- Name: {name}
- Category: {category}
- Key Features:
{feats}
- Target Audience: {aud}
- Tone: {tone} — {tone_desc}

YOUR TASK:
Write exactly two sections, clearly labeled:

PRODUCT TITLE:
A concise, SEO-friendly title (60–80 characters). Include the product name and a key differentiator.

PRODUCT DESCRIPTION:
3–5 sentences. Lead with the primary benefit, weave in key features naturally, end with a subtle call-to-action. Match the tone throughout.

Output only the two labeled sections — no extra commentary."""


def check_ollama(model):
    try:
        r = requests.get(OLLAMA_TAGS, timeout=4)
        if r.status_code != 200:
            return False, "Ollama not responding"
        names = [m["name"].split(":")[0] for m in r.json().get("models", [])]
        if model not in names:
            return False, f"Model '{model}' not found — run: ollama pull {model}"
        return True, "Ready"
    except requests.exceptions.ConnectionError:
        return False, "Ollama not running — start with: ollama serve"


# ─── Main App ─────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Product Description Generator")
        self.geometry("960x720")
        self.minsize(800, 600)
        self.configure(bg=BG)
        self._generating = False
        self._build_ui()
        self.after(300, self._check_status)

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self._style()

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG2, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🛍️  Product Description Generator",
                 font=FONT_TITLE, bg=BG2, fg=FG).pack(side="left", padx=20)

        # Status pill
        self.status_dot  = tk.Label(hdr, text="●", font=("Segoe UI", 12),
                                    bg=BG2, fg=YELLOW)
        self.status_dot.pack(side="right", padx=(0, 6))
        self.status_lbl  = tk.Label(hdr, text="Checking Ollama…",
                                    font=FONT_LABEL, bg=BG2, fg=FG2)
        self.status_lbl.pack(side="right")

        # Model selector
        tk.Label(hdr, text="Model:", font=FONT_LABEL, bg=BG2, fg=FG2).pack(
            side="right", padx=(16, 4))
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        model_entry = tk.Entry(hdr, textvariable=self.model_var,
                               width=14, bg=INPUT_BG, fg=INPUT_FG,
                               insertbackground=FG, relief="flat",
                               font=FONT_MAIN, bd=4)
        model_entry.pack(side="right")

        # ── Body: left form + right output ───────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=16, pady=12)
        body.columnconfigure(0, weight=4)
        body.columnconfigure(1, weight=5)
        body.rowconfigure(0, weight=1)

        self._build_form(body)
        self._build_output(body)

        # ── Status bar ────────────────────────────────────────────────────────
        bar = tk.Frame(self, bg=BG2, pady=5)
        bar.pack(fill="x", side="bottom")
        self.bar_lbl = tk.Label(bar, text="Fill in the form and click Generate.",
                                font=FONT_LABEL, bg=BG2, fg=FG2)
        self.bar_lbl.pack(side="left", padx=14)

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TCombobox",
                     fieldbackground=INPUT_BG,
                     background=INPUT_BG,
                     foreground=INPUT_FG,
                     selectbackground=ACCENT2,
                     selectforeground=FG,
                     arrowcolor=FG2)
        s.map("TCombobox", fieldbackground=[("readonly", INPUT_BG)])

    def _section(self, parent, title):
        """Labelled card section."""
        frame = tk.Frame(parent, bg=CARD, bd=0, relief="flat")
        tk.Label(frame, text=title, font=FONT_BOLD,
                 bg=CARD, fg=ACCENT).pack(anchor="w", padx=12, pady=(10, 4))
        sep = tk.Frame(frame, bg=ACCENT, height=1)
        sep.pack(fill="x", padx=12, pady=(0, 8))
        return frame

    def _label(self, parent, text, bg=None):
        bg = bg or CARD
        tk.Label(parent, text=text, font=FONT_LABEL,
                 bg=bg, fg=FG2).pack(anchor="w", padx=14, pady=(2, 0))

    def _entry(self, parent, var=None, **kw):
        e = tk.Entry(parent, textvariable=var,
                     bg=INPUT_BG, fg=INPUT_FG,
                     insertbackground=FG, relief="flat",
                     font=FONT_MAIN, bd=6, **kw)
        e.pack(fill="x", padx=14, pady=(2, 8), ipady=4)
        return e

    def _text(self, parent, height=4, **kw):
        t = tk.Text(parent, height=height,
                    bg=INPUT_BG, fg=INPUT_FG,
                    insertbackground=FG, relief="flat",
                    font=FONT_MAIN, bd=6,
                    wrap="word", **kw)
        t.pack(fill="x", padx=14, pady=(2, 8), ipady=4)
        return t

    # ── Form Panel ────────────────────────────────────────────────────────────

    def _build_form(self, parent):
        col = tk.Frame(parent, bg=BG)
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        col.rowconfigure(99, weight=1)   # spacer row

        # — Product details —
        sec1 = self._section(col, "📦  Product Details")
        sec1.pack(fill="x", pady=(0, 10))

        self._label(sec1, "Product Name *")
        self.name_var = tk.StringVar()
        self._entry(sec1, var=self.name_var)

        self._label(sec1, "Category *")
        self.cat_var = tk.StringVar()
        self._entry(sec1, var=self.cat_var)

        self._label(sec1, "Key Features  (one per line)")
        self.features_text = self._text(sec1, height=4)

        self._label(sec1, "Target Audience  (optional)")
        self.audience_var = tk.StringVar()
        self._entry(sec1, var=self.audience_var)

        # — Tone —
        sec2 = self._section(col, "🎨  Tone & Style")
        sec2.pack(fill="x", pady=(0, 10))

        self.tone_var = tk.StringVar(value="Professional")
        tone_row = tk.Frame(sec2, bg=CARD)
        tone_row.pack(fill="x", padx=14, pady=(0, 4))
        for i, t in enumerate(TONES):
            tone_row.columnconfigure(i, weight=1)
            rb = tk.Radiobutton(tone_row, text=t, variable=self.tone_var, value=t,
                                bg=CARD, fg=FG, selectcolor=ACCENT2,
                                activebackground=CARD, activeforeground=FG,
                                font=FONT_MAIN, indicatoron=0,
                                relief="flat", bd=0,
                                highlightthickness=0,
                                padx=6, pady=6,
                                cursor="hand2")
            rb.grid(row=0, column=i, sticky="ew", padx=3, pady=(0, 10))
            rb.bind("<Enter>",  lambda e, b=rb: b.configure(fg=ACCENT))
            rb.bind("<Leave>",  lambda e, b=rb: b.configure(fg=FG))

        self.tone_hint = tk.Label(sec2, text=TONE_HINTS["Professional"],
                                  font=FONT_LABEL, bg=CARD, fg=FG2,
                                  wraplength=300, justify="left")
        self.tone_hint.pack(anchor="w", padx=14, pady=(0, 10))
        self.tone_var.trace_add("write", self._update_tone_hint)

        # — Buttons —
        btn_row = tk.Frame(col, bg=BG)
        btn_row.pack(fill="x", pady=(4, 0))

        self.gen_btn = tk.Button(btn_row, text="✨  Generate",
                                 font=FONT_BOLD, bg=ACCENT, fg="white",
                                 activebackground="#c73652", activeforeground="white",
                                 relief="flat", bd=0, padx=20, pady=10,
                                 cursor="hand2", command=self._on_generate)
        self.gen_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.clear_btn = tk.Button(btn_row, text="↺  Clear",
                                   font=FONT_BOLD, bg=BG2, fg=FG2,
                                   activebackground=BORDER, activeforeground=FG,
                                   relief="flat", bd=0, padx=14, pady=10,
                                   cursor="hand2", command=self._on_clear)
        self.clear_btn.pack(side="left")

    # ── Output Panel ──────────────────────────────────────────────────────────

    def _build_output(self, parent):
        col = tk.Frame(parent, bg=BG)
        col.grid(row=0, column=1, sticky="nsew")
        col.rowconfigure(1, weight=1)
        col.columnconfigure(0, weight=1)

        sec = self._section(col, "📝  Generated Output")
        sec.grid(row=0, column=0, rowspan=2, sticky="nsew")
        sec.rowconfigure(2, weight=1)
        sec.columnconfigure(0, weight=1)

        # Output title label
        self.out_title = tk.Label(sec, text="", font=("Segoe UI", 11, "bold"),
                                  bg=CARD, fg=GREEN, wraplength=440,
                                  justify="left")
        self.out_title.pack(fill="x", padx=14, pady=(4, 2))

        sep2 = tk.Frame(sec, bg=BORDER, height=1)
        sep2.pack(fill="x", padx=14, pady=(0, 6))

        # Scrollable output text
        txt_frame = tk.Frame(sec, bg=CARD)
        txt_frame.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        scrollbar = tk.Scrollbar(txt_frame, bg=BG2, troughcolor=BG2,
                                 activebackground=ACCENT2, relief="flat", width=10)
        scrollbar.pack(side="right", fill="y")

        self.out_text = tk.Text(txt_frame, bg=INPUT_BG, fg=FG,
                                font=FONT_MONO, relief="flat", bd=6,
                                wrap="word", state="disabled",
                                insertbackground=FG,
                                yscrollcommand=scrollbar.set,
                                spacing1=2, spacing3=4)
        self.out_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.out_text.yview)

        # Tags for coloring
        self.out_text.tag_config("section", foreground=ACCENT,
                                 font=("Segoe UI", 10, "bold"))
        self.out_text.tag_config("title_val", foreground=GREEN,
                                 font=("Segoe UI", 11, "bold"))
        self.out_text.tag_config("body",  foreground=FG)
        self.out_text.tag_config("muted", foreground=FG2,
                                 font=("Segoe UI", 9, "italic"))

        # Action buttons
        act_row = tk.Frame(sec, bg=CARD)
        act_row.pack(fill="x", padx=14, pady=(0, 12))

        self.copy_btn = tk.Button(act_row, text="📋  Copy",
                                  font=FONT_BOLD, bg=ACCENT2, fg="white",
                                  activebackground="#3d2766", activeforeground="white",
                                  relief="flat", bd=0, padx=14, pady=7,
                                  cursor="hand2", command=self._copy_output,
                                  state="disabled")
        self.copy_btn.pack(side="left", padx=(0, 6))

        self.save_btn = tk.Button(act_row, text="💾  Save as TXT",
                                  font=FONT_BOLD, bg=BG2, fg=FG2,
                                  activebackground=BORDER, activeforeground=FG,
                                  relief="flat", bd=0, padx=14, pady=7,
                                  cursor="hand2", command=self._save_output,
                                  state="disabled")
        self.save_btn.pack(side="left")

        # History counter
        self.history_lbl = tk.Label(act_row, text="",
                                    font=FONT_LABEL, bg=CARD, fg=FG2)
        self.history_lbl.pack(side="right")

        self._history = []   # list of (name, full_text)

    # ── Logic ─────────────────────────────────────────────────────────────────

    def _update_tone_hint(self, *_):
        self.tone_hint.configure(text=TONE_HINTS.get(self.tone_var.get(), ""))

    def _check_status(self):
        def _worker():
            ok, msg = check_ollama(self.model_var.get())
            self.after(0, lambda: self._set_status(ok, msg))
        threading.Thread(target=_worker, daemon=True).start()

    def _set_status(self, ok, msg):
        self.status_dot.configure(fg=GREEN if ok else ACCENT)
        self.status_lbl.configure(text=msg)

    def _set_bar(self, msg, color=FG2):
        self.bar_lbl.configure(text=msg, fg=color)

    def _on_clear(self):
        self.name_var.set("")
        self.cat_var.set("")
        self.audience_var.set("")
        self.features_text.delete("1.0", "end")
        self.tone_var.set("Professional")
        self._clear_output()
        self._set_bar("Form cleared.")

    def _clear_output(self):
        self.out_text.configure(state="normal")
        self.out_text.delete("1.0", "end")
        self.out_text.configure(state="disabled")
        self.out_title.configure(text="")
        self.copy_btn.configure(state="disabled")
        self.save_btn.configure(state="disabled")

    def _on_generate(self):
        if self._generating:
            return

        name     = self.name_var.get().strip()
        category = self.cat_var.get().strip()
        features = self.features_text.get("1.0", "end").splitlines()
        audience = self.audience_var.get().strip()
        tone     = self.tone_var.get()
        model    = self.model_var.get().strip() or DEFAULT_MODEL

        if not name:
            messagebox.showwarning("Missing Field", "Please enter a Product Name.")
            return
        if not category:
            messagebox.showwarning("Missing Field", "Please enter a Category.")
            return

        self._generating = True
        self.gen_btn.configure(state="disabled", text="⏳  Generating…")
        self._clear_output()
        self._set_bar("Connecting to Ollama…", YELLOW)

        # Write placeholder
        self._write_output("muted", "Generating description — please wait…\n\n")

        prompt = build_prompt(name, category, features, audience, tone)
        threading.Thread(
            target=self._stream_generate,
            args=(prompt, model, name),
            daemon=True
        ).start()

    def _stream_generate(self, prompt, model, product_name):
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": 0.75, "top_p": 0.9},
        }
        full_text = []
        try:
            self.after(0, lambda: self._set_bar("Streaming response…", GREEN))
            with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as r:
                r.raise_for_status()
                # Clear placeholder once streaming starts
                first = True
                for line in r.iter_lines():
                    if not line:
                        continue
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        if first:
                            self.after(0, self._clear_output)
                            first = False
                        full_text.append(token)
                        self.after(0, lambda t=token: self._append_raw(t))
                    if chunk.get("done"):
                        break

            full = "".join(full_text).strip()
            self.after(0, lambda: self._finish(full, product_name))

        except requests.exceptions.ConnectionError:
            self.after(0, lambda: self._error(
                "Cannot connect to Ollama.\nMake sure it's running: ollama serve"))
        except requests.exceptions.HTTPError as e:
            self.after(0, lambda: self._error(f"Ollama error: {e}"))
        except Exception as e:
            self.after(0, lambda: self._error(str(e)))

    def _append_raw(self, token):
        """Append a raw streaming token to the output box."""
        self.out_text.configure(state="normal")
        self.out_text.insert("end", token)
        self.out_text.see("end")
        self.out_text.configure(state="disabled")

    def _finish(self, full_text, product_name):
        """Called when generation is complete. Re-render with colours."""
        self._clear_output()
        self._render_output(full_text)
        self._history.append((product_name, full_text))
        count = len(self._history)
        self.history_lbl.configure(text=f"{count} generated this session")
        self.copy_btn.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.gen_btn.configure(state="normal", text="✨  Generate")
        self._generating = False
        self._set_bar("Done! Edit inputs and generate again, or save your result.", GREEN)
        self._check_status()

    def _render_output(self, text):
        """Parse and colour the PRODUCT TITLE / PRODUCT DESCRIPTION blocks."""
        self.out_text.configure(state="normal")
        self.out_text.delete("1.0", "end")

        lines = text.splitlines()
        mode  = None
        desc_lines = []
        title_val  = ""

        for line in lines:
            stripped = line.strip()
            upper    = stripped.upper().replace("**", "").replace(":", "")

            if "PRODUCT TITLE" in upper:
                mode = "title"
                self.out_text.insert("end", "PRODUCT TITLE\n", "section")
                continue
            elif "PRODUCT DESCRIPTION" in upper:
                mode = "desc"
                self.out_text.insert("end", "\nPRODUCT DESCRIPTION\n", "section")
                continue

            if mode == "title" and stripped:
                title_val = stripped.lstrip(":-").strip()
                self.out_text.insert("end", title_val + "\n\n", "title_val")
                self.out_title.configure(text=f"🏷  {title_val}")
                mode = None   # only one title line
            elif mode == "desc":
                self.out_text.insert("end", line + "\n", "body")

        self.out_text.configure(state="disabled")

    def _error(self, msg):
        self._clear_output()
        self._write_output("muted", f"⚠  {msg}")
        self.gen_btn.configure(state="normal", text="✨  Generate")
        self._generating = False
        self._set_bar(msg, ACCENT)

    def _write_output(self, tag, text):
        self.out_text.configure(state="normal")
        self.out_text.insert("end", text, tag)
        self.out_text.configure(state="disabled")

    def _copy_output(self):
        text = self.out_text.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._set_bar("Copied to clipboard!", GREEN)

    def _save_output(self):
        text = self.out_text.get("1.0", "end").strip()
        if not text:
            return
        name = self.name_var.get().strip() or "product"
        safe = "".join(c if c.isalnum() or c in " -_" else "_" for c in name).strip()
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{safe}_{ts}.txt"

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Description",
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"Product: {name}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(text)
            self._set_bar(f"Saved → {os.path.basename(path)}", GREEN)


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
