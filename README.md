# JSON Base64 Smart Comparator

A desktop application for intelligently comparing JSON and **Base64-encoded JSON** with a clean side-by-side diff interface.

Designed specifically for datasets such as lists of objects, catalogs, and structured entities where order should be ignored and only real differences should matter.

---

## ✨ Features

### 🔍 JSON & Base64 Input Support

- Accepts **plain JSON** or **Base64-encoded JSON** in both input fields.
- Automatically detects and **decodes Base64** when needed.
- Validates JSON and shows **clear error messages** if parsing fails.

### 🧠 Smart Structural Comparison

- Ignores **key order** in objects.
- Normalizes JSON while preserving structural readability.
- Detects lists of objects and chooses the best **join key** automatically (e.g. `id`, `uuid`, `code`, etc.).
- Aligns objects in lists **by key instead of index**, even when the order differs.

### 🎯 Precise Line-Level Highlighting

- Highlights only the **exact lines** that differ.
- Marks missing elements on either side.
- No “full-block red highlighting”: only the specific keys/fields that differ are emphasized.

### 🪟 WinMerge-like Side-by-Side View

- Displays both normalized JSON documents in **separate panes**.
- Highlights differences using a **soft red background**.
- Very easy to visually compare two large datasets.

### 🖥️ Simple Desktop GUI

- Built with **Tkinter** (no external dependencies).
- Paste JSON or Base64 in the top section, click **Compare**, view the diff below.
- Fully **offline** and lightweight.

---

## 🚀 How It Works

### 1. Input Processing

For each input:

1. Tries to parse it as JSON.
2. If that fails, tries to treat it as **Base64**:
   - Base64 is decoded.
   - The decoded text is then parsed as JSON.
3. If both attempts fail, an error dialog explains what went wrong.

### 2. Normalization

The app normalizes both structures before comparing them:

- **Objects**
  - Keys are sorted alphabetically.
- **Lists**
  - Elements are normalized recursively.
  - Lists are sorted using a stable structural representation (a “hash”-like freeze) so order does not matter.

### 3. Smart List Matching

When a list contains dictionaries/objects:

- The comparator tries to detect a **unique join key** (e.g. `id`, `uuid`, `code`, etc.).
- If found, this key is used to **align objects across lists**, regardless of position.
- This makes it ideal for catalogs and entity lists where items have a logical identifier.

If no suitable join key is found, the tool falls back to **index-based comparison**.

### 4. Bidirectional Diffing

The diff engine:

- Compares matched objects **recursively**.
- Tracks elements missing on the **left** and on the **right**.
- Produces two sets of **diff paths**:
  - Left-side differences.
  - Right-side differences.

### 5. Visual Highlighting

- Diff paths are mapped to the **exact line numbers** in the formatted output.
- Only those lines are highlighted in the bottom panes.
- Missing elements are clearly marked on the side where they are absent.

---

## 📦 Requirements

- **Python 3.8+**
- **Tkinter**
  - Included by default on Windows and macOS.
  - On some Linux distributions, you may need to install it separately (e.g. `sudo apt install python3-tk`).

No third-party Python packages are required.

---

## 🏁 Installation

Clone the repository:

```bash
git clone https://github.com/yourname/json-base64-smart-comparator.git
cd json-base64-smart-comparator
