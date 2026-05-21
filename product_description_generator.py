#!/usr/bin/env python3
"""
E-Commerce Product Description Generator
Uses Ollama (llama3.2) to generate compelling product titles and descriptions.
"""

import requests
import json
import sys
import os
from datetime import datetime

# ─── Configuration ────────────────────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "llama3.2"

TONES = {
    "1": ("Professional", "formal, authoritative, and trustworthy — ideal for B2B or technical products"),
    "2": ("Casual",       "friendly, conversational, and approachable — great for everyday consumer goods"),
    "3": ("Luxury",       "elegant, exclusive, and aspirational — perfect for premium or high-end products"),
    "4": ("Playful",      "fun, energetic, and witty — best for lifestyle, kids, or trendy products"),
}

# ─── Styling Helpers ──────────────────────────────────────────────────────────

def clr(code: str, text: str) -> str:
    """Wrap text in ANSI color code."""
    codes = {
        "cyan":   "\033[96m",
        "green":  "\033[92m",
        "yellow": "\033[93m",
        "red":    "\033[91m",
        "bold":   "\033[1m",
        "dim":    "\033[2m",
        "reset":  "\033[0m",
    }
    return f"{codes.get(code, '')}{text}{codes['reset']}"

def banner():
    print()
    print(clr("cyan", "╔══════════════════════════════════════════════════════╗"))
    print(clr("cyan", "║") + clr("bold", "   🛍️  E-Commerce Product Description Generator      ") + clr("cyan", "║"))
    print(clr("cyan", "║") + clr("dim",  "        Powered by Ollama · llama3.2                 ") + clr("cyan", "║"))
    print(clr("cyan", "╚══════════════════════════════════════════════════════╝"))
    print()

def divider(label: str = ""):
    width = 56
    if label:
        pad = (width - len(label) - 2) // 2
        print(clr("dim", "─" * pad + f" {label} " + "─" * (width - pad - len(label) - 2)))
    else:
        print(clr("dim", "─" * width))

def prompt_input(label: str, required: bool = True, hint: str = "") -> str:
    hint_str = clr("dim", f"  ({hint})") if hint else ""
    star = clr("red", "*") if required else clr("dim", " ")
    while True:
        value = input(f"  {star} {clr('bold', label)}{hint_str}\n    › ").strip()
        if value or not required:
            return value
        print(clr("yellow", "    This field is required. Please enter a value.\n"))

# ─── Ollama Check ─────────────────────────────────────────────────────────────

def check_ollama(model: str) -> bool:
    """Verify Ollama is running and the model is available."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code != 200:
            return False
        models = [m["name"].split(":")[0] for m in r.json().get("models", [])]
        return model in models
    except requests.exceptions.ConnectionError:
        return False

# ─── Prompt Builder ───────────────────────────────────────────────────────────

def build_prompt(name: str, category: str, features: list[str],
                 audience: str, tone_label: str, tone_desc: str) -> str:
    features_str = "\n".join(f"  - {f}" for f in features) if features else "  - (none provided)"
    return f"""You are an expert e-commerce copywriter. Generate a compelling product listing for the following item.

PRODUCT DETAILS:
- Name: {name}
- Category: {category}
- Key Features:
{features_str}
- Target Audience: {audience if audience else 'General consumers'}
- Tone: {tone_label} — {tone_desc}

YOUR TASK:
Write the following two sections, clearly labeled:

**PRODUCT TITLE:**
A concise, SEO-friendly title (60–80 characters). Should include the product name and a key differentiator.

**PRODUCT DESCRIPTION:**
A compelling description of 3–5 sentences. Lead with the primary benefit. Weave in the key features naturally. End with a subtle call-to-action. Match the specified tone throughout.

Do not add any extra commentary, preamble, or notes — output only the two labeled sections above.
"""

# ─── Ollama Call ──────────────────────────────────────────────────────────────

def generate(prompt: str, model: str) -> str:
    """Stream response from Ollama and return the full text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.75,
            "top_p": 0.9,
        }
    }
    print()
    print(clr("dim", "  Generating"), end="", flush=True)
    full_response = []
    with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if line:
                chunk = json.loads(line)
                token = chunk.get("response", "")
                full_response.append(token)
                print(clr("dim", "·"), end="", flush=True)
                if chunk.get("done"):
                    break
    print()
    return "".join(full_response).strip()

# ─── Save Output ──────────────────────────────────────────────────────────────

def save_output(product_name: str, result: str) -> str:
    """Save the generated description to a .txt file."""
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in product_name).strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}.txt"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Product: {product_name}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(result)
        f.write("\n")
    return filepath

# ─── Main Flow ────────────────────────────────────────────────────────────────

def collect_inputs() -> dict:
    divider("Product Details")
    print()

    name     = prompt_input("Product Name",
                             hint="e.g. Wireless Noise-Cancelling Headphones")
    print()
    category = prompt_input("Product Category",
                             hint="e.g. Electronics, Skincare, Apparel")
    print()

    print(f"  {clr('dim', ' ')} {clr('bold', 'Key Features')}" +
          clr("dim", "  (one per line, blank line to finish)"))
    features = []
    while True:
        feat = input(f"    › Feature {len(features)+1}: ").strip()
        if not feat:
            if features:
                break
            print(clr("yellow", "    Enter at least one feature.\n"))
        else:
            features.append(feat)
    print()

    audience = prompt_input("Target Audience",
                             required=False,
                             hint="e.g. Remote workers aged 25–40, or leave blank")
    print()

    divider("Tone")
    print()
    for key, (label, desc) in TONES.items():
        print(f"    {clr('cyan', key)}. {clr('bold', label):12s} — {clr('dim', desc)}")
    print()

    tone_key = ""
    while tone_key not in TONES:
        tone_key = input("    › Choose a tone [1-4]: ").strip()
    tone_label, tone_desc = TONES[tone_key]

    return dict(name=name, category=category, features=features,
                audience=audience, tone_label=tone_label, tone_desc=tone_desc)

def main():
    banner()

    # ── Model selection ──────────────────────────────────────────────────────
    model = DEFAULT_MODEL
    print(clr("dim", f"  Using model: {model}  (edit DEFAULT_MODEL at top of script to change)\n"))

    # ── Check Ollama ─────────────────────────────────────────────────────────
    print(clr("dim", "  Checking Ollama connection..."), end="", flush=True)
    if not check_ollama(model):
        print()
        print(clr("red", "\n  ✗ Cannot connect to Ollama or model not found."))
        print(clr("yellow", "    • Make sure Ollama is running:  ollama serve"))
        print(clr("yellow", f"    • Pull the model if needed:     ollama pull {model}\n"))
        sys.exit(1)
    print(clr("green", " ✓ Ready\n"))

    while True:
        # ── Gather inputs ────────────────────────────────────────────────────
        inputs = collect_inputs()

        # ── Build prompt & generate ──────────────────────────────────────────
        prompt = build_prompt(**inputs)
        divider("Generating")
        result = generate(prompt, model)

        # ── Display result ───────────────────────────────────────────────────
        print()
        divider("Result")
        print()
        for line in result.splitlines():
            if line.startswith("**") and line.endswith("**"):
                print("  " + clr("cyan", clr("bold", line.replace("**", ""))))
            else:
                print("  " + line)
        print()

        # ── Save option ──────────────────────────────────────────────────────
        save = input("  Save output to file? [y/N]: ").strip().lower()
        if save == "y":
            path = save_output(inputs["name"], result)
            print(clr("green", f"\n  ✓ Saved → {path}\n"))

        # ── Loop ─────────────────────────────────────────────────────────────
        divider()
        again = input("\n  Generate another product? [y/N]: ").strip().lower()
        if again != "y":
            print(clr("cyan", "\n  Done. Happy selling! 🛍️\n"))
            break
        print()

if __name__ == "__main__":
    main()
