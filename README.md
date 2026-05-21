# 🛍️ Product Description Generator

An AI-powered e-commerce product description generator built with Python and [Ollama](https://ollama.com). Available as both a **desktop GUI app** (Tkinter) and a **command-line script**.

---

## ✨ Features

- **AI-generated titles & descriptions** using local Ollama models (default: `llama3.2`)
- **Desktop GUI** with a dark theme — no browser needed
- **CLI script** for quick terminal use or batch workflows
- Four writing tones: **Professional**, **Casual**, **Luxury**, **Playful**
- Accepts: product name, category, key features, target audience
- Live streaming output — see text generate token by token
- Copy to clipboard or save as `.txt` with one click
- Ollama connection status indicator with helpful error messages
- Fully local — no API keys, no internet required

---

## 📸 Screenshot

> Desktop app (dark theme)

```
╔══════════════════════════════════════════════════════╗
║   🛍️  Product Description Generator                  ║
║        Powered by Ollama · llama3.2                  ║
╚══════════════════════════════════════════════════════╝
```

---

## 🚀 Quick Start

### 1. Install Ollama

Download from [ollama.com](https://ollama.com) and pull the default model:

```bash
ollama pull llama3.2
ollama serve
```

### 2. Clone this repo

```bash
git clone https://github.com/vivekjangiir/product-description-generator.git
cd product-description-generator
```

### 3. Install Python dependency

```bash
pip install requests
```

> Tkinter is included with Python. No other dependencies needed.

---

## 🖥️ Desktop App

```bash
python app.py
```

**How to use:**

1. Fill in **Product Name** and **Category** (required)
2. Add **Key Features** — one per line
3. Optionally enter a **Target Audience**
4. Choose a **Tone** using the radio buttons
5. Click **✨ Generate**
6. Copy or save the result using the buttons on the right

The model name in the header can be edited to use any model you have installed in Ollama (e.g. `mistral`, `gemma3`).

---

## 💻 CLI Script

```bash
python product_description_generator.py
```

The script guides you through each input interactively and streams the output to your terminal. After generation you can optionally save the result to a `.txt` file.

---

## 📁 Project Structure

```
product-description-generator/
├── app.py                            # Desktop GUI (Tkinter, dark theme)
├── product_description_generator.py  # CLI script
└── README.md
```

---

## ⚙️ Configuration

| Setting | Where to change | Default |
|---|---|---|
| Ollama model | `DEFAULT_MODEL` at top of either file | `llama3.2` |
| Temperature | `options` dict in `generate()` / `_stream_generate()` | `0.75` |
| Ollama host | `OLLAMA_URL` constant | `http://localhost:11434` |

---

## 🔧 Supported Models

Any model available in Ollama works. Recommended options:

| Model | Best for |
|---|---|
| `llama3.2` | Fast, well-rounded (default) |
| `mistral` | Structured, precise copy |
| `gemma3` | Creative, natural-sounding text |
| `phi3` | Lightweight, fast on lower-end hardware |

---

## 📋 Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally
- `requests` library (`pip install requests`)
- Tkinter (bundled with Python on Windows and macOS)

---

## 📄 License

MIT — free to use, modify, and distribute.
