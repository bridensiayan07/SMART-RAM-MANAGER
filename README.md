# 🧠 Smart RAM Manager — Dynamic Memory Allocation Simulator

A professional, Streamlit-based dashboard that simulates how an Operating
System allocates RAM to running applications, using three classic memory
allocation strategies: **First Fit**, **Best Fit**, and **Worst Fit**.

It visualizes memory usage as segmented RAM blocks, analyzes internal
fragmentation, and compares all three algorithms side-by-side on the same
input so you can see which strategy performs best.

---

## ✨ Features

- **Single control panel** — all input (memory blocks, applications,
  algorithm choice) lives in the sidebar and is read only once per run.
- **🟢 Simulation tab** — allocation table + a segmented, color-coded RAM
  visualization showing allocated apps, internal fragmentation, and free space.
- **🟡 Analytics tab** — total / used / free memory, efficiency %, and a
  plain-English explanation of internal vs. external fragmentation.
- **🔵 Comparison tab** — runs First Fit, Best Fit and Worst Fit on the exact
  same input, shows a comparison table (with the best algorithm highlighted)
  and a dark-themed efficiency bar chart.
- **🟣 Insights tab** — smart, human-readable system messages such as
  "Fragmentation detected", "Process cannot be allocated", or
  "Best Fit performs better than First Fit for this input".
- **Clean, professional light-theme UI** — pure white background, light-grey
  sidebar, subtle bordered cards, and a single blue accent color
  (`#2563EB`), styled with `.streamlit/config.toml` plus CSS that forces
  the light look regardless of the viewer's system dark-mode setting.
  No emojis, no gradients, no extra bright colors — built to read like a
  SaaS/system-monitoring dashboard rather than a student demo.

---

## 📁 Project Structure

```
smart_ram_manager/
│── app.py                  # Main Streamlit app (UI, tabs, sidebar)
│── memory_algorithms.py    # First Fit / Best Fit / Worst Fit implementations
│── utils.py                # Input parsing, validation, formatting helpers
│── requirements.txt        # Python dependencies
│── README.md                # This file
│
└── .streamlit/
    └── config.toml          # Light theme configuration (white / blue accent)
```

---

## 🚀 How to Run

1. **Open the project folder in VS Code.**

2. **(Recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS / Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   streamlit run app.py
   ```

5. Your browser will open automatically at `http://localhost:8501`.

---

## 🧩 Input Format

- **Memory Blocks (MB):** comma-separated whole numbers
  `100,500,200,300,600`

- **Applications (Name:Size):** comma-separated `Name:Size` pairs
  `Chrome:300, VSCode:200, Docker:450, Slack:150`

Click **Run Simulation** in the sidebar to generate results across all tabs.

---

## 🧠 How the Algorithms Work

Each memory block can hold **at most one application** (the standard
fixed-partition model used to teach these algorithms):

| Algorithm  | Rule |
|------------|------|
| First Fit  | Place the app in the **first** block big enough for it |
| Best Fit   | Place the app in the **smallest** block that still fits it |
| Worst Fit  | Place the app in the **largest** available block |

Any leftover space inside an allocated block is counted as **internal
fragmentation** — memory reserved but unused.

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) — UI framework
- [Pandas](https://pandas.pydata.org/) — data tables
- [Matplotlib](https://matplotlib.org/) — comparison chart
