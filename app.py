"""
app.py
------
Smart RAM Manager: Dynamic Memory Allocation Simulator

A clean, professional, LIGHT-THEME Streamlit dashboard that simulates
how an Operating System allocates RAM to running applications using
First Fit, Best Fit and Worst Fit.

Run with:
    streamlit run app.py
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from memory_algorithms import ALGORITHMS
from utils import InputError, parse_blocks, parse_processes, format_mb, format_pct


# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Smart RAM Manager",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------------------
# BRAND / THEME CONSTANTS
# Keep this to ONE accent color (blue) plus neutral greys, matching
# .streamlit/config.toml. Do not introduce extra bright colors.
# ----------------------------------------------------------------------
ACCENT = "#2563EB"          # primary blue accent (buttons, highlights)
ACCENT_DARK = "#1D4ED8"
ACCENT_LIGHT = "#DBEAFE"    # very light blue for subtle backgrounds
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
BORDER = "#E5E7EB"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F5F7FA"
WARN_MUTED = "#F59E0B"      # single muted tone used ONLY for fragmentation
ERROR_MUTED = "#DC2626"     # single muted tone used ONLY for failures


# ----------------------------------------------------------------------
# CUSTOM CSS
# Forces a pure white / light-grey professional look regardless of the
# viewer's OS/browser dark-mode setting, and overrides Streamlit's
# defaults with a clean SaaS-dashboard style.
# ----------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        /* ---- Force light backgrounds, ignore system dark mode ----
           NOTE: we only touch BACKGROUND on top-level containers here.
           We deliberately do NOT force `color` on generic tags like
           div/span/label/*, because that cascades into Streamlit's own
           widgets (buttons, dropdown menus, dataframe toolbar, etc.)
           and silently overrides text colors those widgets set on
           themselves for contrast -- e.g. it was turning the white
           text on the blue "Run Simulation" button dark-on-blue, and
           could do the same inside the algorithm dropdown. The
           .streamlit/config.toml theme already gives every native
           Streamlit widget correct light-mode text color on its own. */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
            background-color: {SURFACE} !important;
        }}
        [data-testid="stHeader"] {{
            background-color: {SURFACE} !important;
        }}
        [data-testid="stSidebar"] {{
            background-color: {SURFACE_ALT} !important;
            border-right: 1px solid {BORDER};
        }}

        /* ---- Spacing ---- */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1300px;
        }}

        /* ---- Card ---- */
        .card {{
            background-color: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1.1rem;
        }}
        .card h4 {{
            margin-top: 0;
            margin-bottom: 0.6rem;
            font-size: 1rem;
            font-weight: 600;
            color: {TEXT_PRIMARY};
        }}

        /* ---- KPI metric card ---- */
        .kpi-card {{
            background-color: {SURFACE_ALT};
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 1.1rem 1.3rem;
            text-align: left;
        }}
        .kpi-label {{
            font-size: 0.75rem;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: {TEXT_SECONDARY};
            margin-bottom: 0.35rem;
            font-weight: 600;
        }}
        .kpi-value {{
            font-size: 1.65rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
        }}

        /* ---- Section heading ---- */
        .section-title {{
            font-size: 1.05rem;
            font-weight: 600;
            color: {TEXT_PRIMARY};
            margin-bottom: 0.75rem;
        }}
        .section-sub {{
            font-size: 0.85rem;
            color: {TEXT_SECONDARY};
            margin-top: -0.5rem;
            margin-bottom: 0.9rem;
        }}

        /* ---- Memory bar ---- */
        .mem-wrap {{
            display: flex;
            width: 100%;
            height: 76px;
            gap: 4px;
            border-radius: 8px;
            overflow: hidden;
            background-color: {SURFACE_ALT};
            padding: 4px;
            border: 1px solid {BORDER};
        }}
        .mem-block {{
            display: flex;
            border-radius: 5px;
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.04);
        }}
        .mem-seg {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 2px 4px;
            font-size: 0.68rem;
            font-weight: 600;
            text-align: center;
            line-height: 1.15;
            white-space: nowrap;
            overflow: hidden;
        }}

        /* ---- Legend ---- */
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.8rem;
            color: {TEXT_SECONDARY};
        }}
        .legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 3px;
            display: inline-block;
            border: 1px solid rgba(0,0,0,0.08);
        }}

        /* ---- Status badges ---- */
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-ok {{ background-color: {ACCENT_LIGHT}; color: {ACCENT_DARK}; }}
        .badge-bad {{ background-color: #FEE2E2; color: {ERROR_MUTED}; }}

        /* ---- Insight rows (no emoji, color + left border communicate status) ---- */
        .insight-row {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 0.6rem;
            font-size: 0.9rem;
            background-color: {SURFACE_ALT};
            border: 1px solid {BORDER};
        }}
        .insight-tag {{
            flex-shrink: 0;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: 5px;
            white-space: nowrap;
        }}
        .insight-warn  .insight-tag {{ background-color: #FEF3C7; color: #92400E; }}
        .insight-bad   .insight-tag {{ background-color: #FEE2E2; color: {ERROR_MUTED}; }}
        .insight-good  .insight-tag {{ background-color: {ACCENT_LIGHT}; color: {ACCENT_DARK}; }}
        .insight-info  .insight-tag {{ background-color: #EEF2FF; color: #4338CA; }}
        .insight-warn  {{ border-left: 3px solid {WARN_MUTED}; }}
        .insight-bad   {{ border-left: 3px solid {ERROR_MUTED}; }}
        .insight-good  {{ border-left: 3px solid {ACCENT}; }}
        .insight-info  {{ border-left: 3px solid #6366F1; }}

        /* ---- Highlight callout (replaces default green success box) ---- */
        .highlight-card {{
            background-color: {ACCENT_LIGHT};
            border: 1px solid #BFDBFE;
            border-left: 4px solid {ACCENT};
            border-radius: 8px;
            padding: 0.9rem 1.1rem;
            font-size: 0.92rem;
            color: {ACCENT_DARK};
            margin: 0.75rem 0 1rem 0;
        }}

        /* ---- Streamlit buttons: single blue accent ----
           `!important` + targeting every nested element (button, its
           inner p/span/div) so the white label text always wins,
           regardless of selector order elsewhere on the page. */
        div.stButton > button {{
            background-color: {ACCENT} !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }}
        div.stButton > button, div.stButton > button * {{
            color: #FFFFFF !important;
        }}
        div.stButton > button:hover {{
            background-color: {ACCENT_DARK} !important;
        }}
        div.stButton > button:hover * {{
            color: #FFFFFF !important;
        }}

        /* ---- Inputs (closed state) ---- */
        [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {{
            background-color: {SURFACE} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 6px !important;
            color: {TEXT_PRIMARY} !important;
        }}
        /* ---- Selectbox (the "Allocation Algorithm" fit picker) ----
           BaseWeb renders several nested divs/spans for the closed
           control, each carrying its own dark-theme background/color
           via inline CSS-in-JS. A single shallow selector isn't enough
           to beat all of them, so we force every layer inside the
           control (and its dropdown arrow icon) to the light palette.
           This is scoped to [data-baseweb="select"] only, so it can't
           leak into buttons or anything else on the page. */
        [data-testid="stSelectbox"] [data-baseweb="select"],
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stSelectbox"] [data-baseweb="select"] div,
        [data-testid="stSelectbox"] [data-baseweb="select"] span {{
            background-color: {SURFACE} !important;
            color: {TEXT_PRIMARY} !important;
            border-color: {BORDER} !important;
        }}
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
            border: 1px solid {BORDER} !important;
            border-radius: 6px !important;
        }}
        [data-testid="stSelectbox"] [data-baseweb="select"] svg {{
            fill: {TEXT_SECONDARY} !important;
        }}

        /* ---- Dropdown / listbox popover (the opened menu of options) ----
           This menu is rendered in a portal, so it needs its own
           explicit light background + dark text -- otherwise it can
           inherit mismatched colors and become unreadable. Same
           "override every nested layer" approach as above. */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] div,
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] span {{
            background-color: {SURFACE} !important;
            color: {TEXT_PRIMARY} !important;
        }}
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] li[aria-selected="true"] {{
            background-color: {ACCENT_LIGHT} !important;
            color: {ACCENT_DARK} !important;
        }}

        /* ---- Tabs ---- */
        button[data-baseweb="tab"] {{
            font-weight: 600;
            color: {TEXT_SECONDARY} !important;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            color: {ACCENT} !important;
        }}
        [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
            background-color: {ACCENT};
        }}

        /* ---- Dataframes / tables ----
           Force a light, bordered wrapper so the grid never renders on
           a mismatched (dark) background; text color inside the grid
           itself is drawn by Streamlit directly from config.toml. */
        [data-testid="stDataFrame"] {{
            background-color: {SURFACE} !important;
            border: 1px solid {BORDER};
            border-radius: 8px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# COLOR PALETTE for the RAM visualization
# Neutral: shades of the single blue accent for allocated apps,
# one muted amber for internal fragmentation, light grey for free space.
# ----------------------------------------------------------------------
PROCESS_COLORS = ["#2563EB", "#3B82F6", "#60A5FA", "#1D4ED8", "#93C5FD", "#1E40AF"]
FRAG_COLOR = WARN_MUTED
FRAG_TEXT_COLOR = "#5B3A00"
FREE_COLOR = "#E5E7EB"
FREE_TEXT_COLOR = TEXT_SECONDARY
PROCESS_SEG_TEXT_COLOR = "#FFFFFF"


# ----------------------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------------------
if "ran" not in st.session_state:
    st.session_state.ran = False
if "blocks" not in st.session_state:
    st.session_state.blocks = []
if "processes" not in st.session_state:
    st.session_state.processes = []
if "algorithm" not in st.session_state:
    st.session_state.algorithm = "First Fit"
if "allocation" not in st.session_state:
    st.session_state.allocation = []
if "block_status" not in st.session_state:
    st.session_state.block_status = []


# ----------------------------------------------------------------------
# CORE METRIC / ANALYSIS HELPERS
# ----------------------------------------------------------------------
def compute_metrics(blocks, processes, allocation):
    """
    Given the original blocks, the process list and the allocation result,
    work out every number the dashboard needs: used memory, free memory,
    efficiency, internal fragmentation, per-process details, etc.
    """
    total_memory = sum(blocks)
    used_memory = 0
    internal_frag_total = 0
    rows = []

    for i, (name, size) in enumerate(processes):
        block_idx = allocation[i]
        if block_idx is None:
            rows.append({
                "Application": name,
                "Requested (MB)": size,
                "Allocated Block": "Not Allocated",
                "Block Size (MB)": "-",
                "Internal Fragmentation (MB)": "-",
                "Status": "Failed",
            })
        else:
            block_size = blocks[block_idx]
            frag = block_size - size
            used_memory += size
            internal_frag_total += frag
            rows.append({
                "Application": name,
                "Requested (MB)": size,
                "Allocated Block": f"Block {block_idx + 1}",
                "Block Size (MB)": block_size,
                "Internal Fragmentation (MB)": frag,
                "Status": "Allocated",
            })

    free_memory = total_memory - used_memory
    efficiency = (used_memory / total_memory * 100) if total_memory else 0
    unallocated = [r["Application"] for r in rows if r["Status"] == "Failed"]

    untouched_free_blocks = [
        blocks[j] for j in range(len(blocks))
        if j not in [a for a in allocation if a is not None]
    ]

    return {
        "total_memory": total_memory,
        "used_memory": used_memory,
        "free_memory": free_memory,
        "efficiency": efficiency,
        "internal_frag_total": internal_frag_total,
        "rows": rows,
        "unallocated": unallocated,
        "untouched_free_blocks": untouched_free_blocks,
    }


def render_memory_bar(blocks, processes, allocation):
    """Build the segmented HTML/CSS RAM visualization bar (neutral palette)."""
    owner = {}
    for p_idx, b_idx in enumerate(allocation):
        if b_idx is not None:
            owner[b_idx] = p_idx

    segments_html = ""
    for j, block_size in enumerate(blocks):
        if j in owner:
            p_idx = owner[j]
            name, psize = processes[p_idx]
            frag = block_size - psize
            color = PROCESS_COLORS[p_idx % len(PROCESS_COLORS)]

            inner = (
                f'<div class="mem-seg" style="flex:{psize}; background-color:{color}; '
                f'color:{PROCESS_SEG_TEXT_COLOR};">{name}<br>{psize} MB</div>'
            )
            if frag > 0:
                inner += (
                    f'<div class="mem-seg" style="flex:{frag}; background-color:{FRAG_COLOR}; '
                    f'color:{FRAG_TEXT_COLOR};">{frag} MB<br>unused</div>'
                )
            segments_html += f'<div class="mem-block" style="flex:{block_size};">{inner}</div>'
        else:
            segments_html += (
                f'<div class="mem-block" style="flex:{block_size};">'
                f'<div class="mem-seg" style="flex:{block_size}; background-color:{FREE_COLOR}; '
                f'color:{FREE_TEXT_COLOR};">Free<br>{block_size} MB</div></div>'
            )

    return f'<div class="mem-wrap">{segments_html}</div>'


def run_all_algorithms(blocks, processes):
    """Run First Fit, Best Fit and Worst Fit on the same input and
    return a comparison-ready list of metric dictionaries."""
    results = []
    for algo_name, algo_func in ALGORITHMS.items():
        allocation, _ = algo_func(blocks, processes)
        metrics = compute_metrics(blocks, processes, allocation)
        results.append({
            "Algorithm": algo_name,
            "Used Memory (MB)": metrics["used_memory"],
            "Efficiency (%)": round(metrics["efficiency"], 1),
            "Wasted / Fragmented (MB)": metrics["internal_frag_total"],
            "Unallocated Apps": len(metrics["unallocated"]),
        })
    return results


def kpi_card(label, value):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------
# SIDEBAR — single source of input for the whole app
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Smart RAM Manager")
    st.caption("Dynamic Memory Allocation Simulator")
    st.divider()

    st.markdown("**Memory Blocks (MB)**")
    blocks_input = st.text_input(
        "Comma-separated block sizes",
        value="100,500,200,300,600",
        label_visibility="collapsed",
        help="Example: 100,500,200",
    )

    st.markdown("**Applications (Name:Size)**")
    processes_input = st.text_area(
        "Comma-separated Name:Size pairs",
        value="Chrome:300, VSCode:200, Docker:450, Slack:150",
        label_visibility="collapsed",
        help="Example: Chrome:300, VSCode:200",
        height=90,
    )

    st.markdown("**Allocation Algorithm**")
    algorithm = st.selectbox(
        "Algorithm",
        options=list(ALGORITHMS.keys()),
        label_visibility="collapsed",
    )

    st.divider()
    run_clicked = st.button("Run Simulation", use_container_width=True, type="primary")

    st.divider()
    st.caption("Streamlit dashboard - First Fit / Best Fit / Worst Fit")


# ----------------------------------------------------------------------
# HANDLE THE "RUN SIMULATION" CLICK  (input is read ONLY here)
# ----------------------------------------------------------------------
if run_clicked:
    try:
        blocks = parse_blocks(blocks_input)
        processes = parse_processes(processes_input)
        algo_func = ALGORITHMS[algorithm]
        allocation, block_status = algo_func(blocks, processes)

        st.session_state.blocks = blocks
        st.session_state.processes = processes
        st.session_state.algorithm = algorithm
        st.session_state.allocation = allocation
        st.session_state.block_status = block_status
        st.session_state.ran = True

    except InputError as e:
        st.session_state.ran = False
        st.sidebar.error(str(e))


# ----------------------------------------------------------------------
# MAIN AREA — HEADER
# ----------------------------------------------------------------------
st.markdown("## Smart RAM Manager")
st.caption("A dynamic memory allocation simulator for First Fit, Best Fit and Worst Fit strategies")

if not st.session_state.ran:
    st.info("Enter your memory blocks and applications in the sidebar, then click Run Simulation to begin.")
    st.stop()

# Pull the current simulation data out of session state
blocks = st.session_state.blocks
processes = st.session_state.processes
algorithm = st.session_state.algorithm
allocation = st.session_state.allocation
metrics = compute_metrics(blocks, processes, allocation)


# ----------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------
tab_sim, tab_analytics, tab_compare, tab_insights = st.tabs(
    ["Simulation", "Analytics", "Comparison", "Insights"]
)

# ======================================================================
# TAB 1 — SIMULATION
# ======================================================================
with tab_sim:
    st.markdown(f'<div class="section-title">Allocation Result — {algorithm}</div>', unsafe_allow_html=True)

    df_alloc = pd.DataFrame(metrics["rows"])
    st.dataframe(df_alloc, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title" style="margin-top:1.2rem;">RAM Visualization</div>', unsafe_allow_html=True)
    st.markdown(render_memory_bar(blocks, processes, allocation), unsafe_allow_html=True)

    # Legend
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    legend_cols = st.columns(len(processes) + 2)
    for i, (name, _size) in enumerate(processes):
        with legend_cols[i % len(legend_cols)]:
            color = PROCESS_COLORS[i % len(PROCESS_COLORS)]
            st.markdown(
                f'<div class="legend-item"><span class="legend-dot" '
                f'style="background-color:{color};"></span>{name}</div>',
                unsafe_allow_html=True,
            )
    with legend_cols[-2]:
        st.markdown(
            f'<div class="legend-item"><span class="legend-dot" '
            f'style="background-color:{FRAG_COLOR};"></span>Internal Fragmentation</div>',
            unsafe_allow_html=True,
        )
    with legend_cols[-1]:
        st.markdown(
            f'<div class="legend-item"><span class="legend-dot" '
            f'style="background-color:{FREE_COLOR};"></span>Free Block</div>',
            unsafe_allow_html=True,
        )

# ======================================================================
# TAB 2 — ANALYTICS
# ======================================================================
with tab_analytics:
    st.markdown(f'<div class="section-title">Memory Analytics — {algorithm}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Memory", format_mb(metrics["total_memory"]))
    with c2:
        kpi_card("Used Memory", format_mb(metrics["used_memory"]))
    with c3:
        kpi_card("Free Memory", format_mb(metrics["free_memory"]))
    with c4:
        kpi_card("Efficiency", format_pct(metrics["efficiency"]))

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    colA, colB = st.columns([1.3, 1])

    with colA:
        st.markdown('<div class="card"><h4>Memory Usage Breakdown</h4>', unsafe_allow_html=True)
        st.progress(min(metrics["efficiency"] / 100, 1.0))
        st.caption(
            f"{format_mb(metrics['used_memory'])} used  |  "
            f"{format_mb(metrics['internal_frag_total'])} lost to internal fragmentation  |  "
            f"{format_mb(metrics['free_memory'] - metrics['internal_frag_total'])} fully free"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with colB:
        st.markdown('<div class="card"><h4>Fragmentation Explained</h4>', unsafe_allow_html=True)
        st.markdown(
            """
            **Internal Fragmentation** happens when a process is placed inside a
            block that is larger than it needs. The leftover space inside that
            block is wasted, because it belongs to the process's block but the
            process isn't using it.

            **External Fragmentation** happens when there is enough total free
            memory to run a process, but it's scattered across several blocks
            instead of one block big enough on its own.
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

# ======================================================================
# TAB 3 — COMPARISON
# ======================================================================
with tab_compare:
    st.markdown('<div class="section-title">Algorithm Comparison — Same Input, All 3 Strategies</div>', unsafe_allow_html=True)

    comparison_results = run_all_algorithms(blocks, processes)
    df_compare = pd.DataFrame(comparison_results)

    best_row = df_compare.loc[df_compare["Efficiency (%)"].idxmax()]
    best_algo = best_row["Algorithm"]

    def highlight_best(row):
        if row["Algorithm"] == best_algo:
            return [f"background-color: {ACCENT_LIGHT}; font-weight: 600;"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_compare.style.apply(highlight_best, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        f'<div class="highlight-card"><strong>{best_algo}</strong> achieves the best efficiency '
        f'for this input ({best_row["Efficiency (%)"]}%).</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title" style="margin-top:0.8rem;">Efficiency Comparison Chart</div>', unsafe_allow_html=True)

    fig, ax = plt.subplots(figsize=(6, 3.2))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    bar_colors = [ACCENT if a == best_algo else "#D1D5DB" for a in df_compare["Algorithm"]]
    bars = ax.bar(df_compare["Algorithm"], df_compare["Efficiency (%)"], color=bar_colors, width=0.5)

    ax.set_ylabel("Efficiency (%)", color=TEXT_SECONDARY)
    ax.set_ylim(0, 100)
    ax.tick_params(colors=TEXT_SECONDARY)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.grid(axis="y", color=BORDER, linewidth=0.8, alpha=0.9)

    for bar, val in zip(bars, df_compare["Efficiency (%)"]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 2, f"{val}%",
                ha="center", color=TEXT_PRIMARY, fontsize=9, fontweight="bold")

    st.pyplot(fig, use_container_width=True)

# ======================================================================
# TAB 4 — INSIGHTS
# ======================================================================
with tab_insights:
    st.markdown(f'<div class="section-title">Smart Insights — {algorithm}</div>', unsafe_allow_html=True)

    insights = []

    # Fragmentation insight
    if metrics["internal_frag_total"] > 0:
        insights.append((
            "warn", "Warning",
            f"Fragmentation detected: {format_mb(metrics['internal_frag_total'])} of internal "
            f"fragmentation across allocated blocks."
        ))
    else:
        insights.append((
            "good", "OK",
            "No internal fragmentation — every allocated block was used perfectly."
        ))

    # Unallocated processes insight
    if metrics["unallocated"]:
        names = ", ".join(metrics["unallocated"])
        insights.append((
            "bad", "Error",
            f"Process(es) could not be allocated: {names}. No block was large enough for them."
        ))
    else:
        insights.append((
            "good", "OK",
            "All applications were successfully allocated to memory."
        ))

    # Efficiency insight
    if metrics["efficiency"] >= 90:
        insights.append((
            "good", "OK",
            f"Excellent efficiency: {format_pct(metrics['efficiency'])} of total memory is in use."
        ))
    elif metrics["efficiency"] < 50:
        insights.append((
            "warn", "Warning",
            f"Low efficiency: only {format_pct(metrics['efficiency'])} of total memory is being used."
        ))

    # Best algorithm insight (computed by comparing all 3 on the same input)
    comparison_results = run_all_algorithms(blocks, processes)
    df_compare = pd.DataFrame(comparison_results)
    best_row = df_compare.loc[df_compare["Efficiency (%)"].idxmax()]
    if best_row["Algorithm"] != algorithm:
        insights.append((
            "info", "Info",
            f"{best_row['Algorithm']} performs better than {algorithm} for this exact input "
            f"({best_row['Efficiency (%)']}% vs {format_pct(metrics['efficiency'])})."
        ))
    else:
        insights.append((
            "info", "Info",
            f"{algorithm} is already the best-performing strategy for this input."
        ))

    # Untouched free blocks insight (possible external fragmentation)
    if len(metrics["untouched_free_blocks"]) > 1:
        total_untouched = sum(metrics["untouched_free_blocks"])
        insights.append((
            "info", "Info",
            f"External fragmentation risk: {len(metrics['untouched_free_blocks'])} separate free "
            f"blocks ({format_mb(total_untouched)} total) are unused but scattered instead of contiguous."
        ))

    css_class = {
        "warn": "insight-warn",
        "bad": "insight-bad",
        "good": "insight-good",
        "info": "insight-info",
    }

    for level, tag, text in insights:
        st.markdown(
            f'<div class="insight-row {css_class[level]}">'
            f'<span class="insight-tag">{tag}</span><span>{text}</span></div>',
            unsafe_allow_html=True,
        )
