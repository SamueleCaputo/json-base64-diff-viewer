📘 JSON Base64 Smart Comparator

A desktop application for intelligently comparing JSON and Base64-encoded JSON with a clean side-by-side diff interface.
Designed specifically for datasets such as lists of objects, catalogs, and structured entities where order should be ignored and only real differences should matter.

✨ Features
🔍 JSON & Base64 Input Support

Accepts plain JSON or Base64-encoded JSON in both input fields.

Automatically detects and decodes Base64 when needed.

Validates JSON with clear error messages.

🧠 Smart Structural Comparison

Ignores key order in objects.

Normalizes JSON while preserving structural readability.

Detects list objects and chooses the best join key automatically (e.g., id, uuid, codPrestazione, code, etc.).

Aligns objects in lists by key instead of index, even when the order differs.

🎯 Precise Line-Level Highlighting

Highlights only the exact lines that differ.

Marks missing elements on either side.

No “full-block red highlighting”: only the specific keys/fields that differ.

🪟 WinMerge-like Side-by-Side View

Displays both normalized JSON documents in separate panes.

Highlights differences using a soft red background.

Very easy to visually compare two large datasets.

🖥️ Simple Desktop GUI

Built with Tkinter (no external dependencies).

Paste JSON or Base64 in the top section, click Compare, view the diff below.

Fully offline and lightweight.

🚀 How It Works

Input Processing

Each input is checked:

If Base64 → decoded → parsed as JSON

If JSON → parsed directly

Normalization

Objects: keys sorted alphabetically

Lists: elements normalized and sorted using a stable structural hash

Smart List Matching

If the list contains dicts, the comparator tries to detect a unique join key.

The chosen key is used to align objects correctly across the two lists.

Bidirectional Diffing

Compares matched objects recursively.

Tracks missing left/right elements.

Produces two sets of “diff paths”: left-side differences and right-side differences.

Visual Highlighting

Paths are mapped to the exact line numbers.

Only those lines are highlighted in the output panes.

📦 Requirements

Python 3.8+

Tkinter (included by default on Windows/macOS; may require installation on some Linux distros)

No third-party packages required.

🏁 Installation

Clone the repository:

git clone https://github.com/yourname/json-base64-smart-comparator.git
cd json-base64-smart-comparator


Run the script:

python json_comparator.py


or

python3 json_comparator.py


The GUI will open immediately.

🧪 Example Use Case
Comparing lists of “prestazioni” by codPrestazione

Even if:

the order differs,

some items exist only in one list,

some fields differ while others match,

…the comparator will:

align items by codPrestazione,

highlight only the changed fields,

show missing entries only on the side where they are absent,

report the difference in list size.

This makes it ideal for:

medical procedure catalogs

product lists

configuration sets

any dataset with identifiable objects

📁 Repository Structure
/json-base64-smart-comparator
│
├── json_comparator.py     # main application (GUI + diff engine)
├── README.md              # project documentation
└── LICENSE                # optional license file

⚠️ Known Limitations

If a list does not contain any unique or consistent key, the tool falls back to index-based comparison.

Base64 decoding requires the encoded content to be strictly valid JSON.

Extremely large JSON files may impact Tkinter performance.

🤝 Contributing

Contributions are welcome!
You can propose:

new join-key strategies,

dark/light themes,

export to HTML/PDF,

filters (show only differences),

performance improvements.

Open an issue or submit a pull request.
