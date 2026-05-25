import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuantLab",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
.block-container { padding-top: 0.8rem; padding-bottom: 1rem; max-width: 1440px; }

/* ─ Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #080c14 !important;
    border-right: 1px solid #0f1829;
}
[data-testid="stSidebar"] label { font-size: 0.78rem !important; color: #4a5a7a !important; }
[data-testid="stSidebarContent"] { padding-top: 1.4rem; }

/* ─ Logo ────────────────────────────────────────────────────────────────── */
.ql-logo {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 0.15rem;
}
.ql-logo-accent {
    background: linear-gradient(135deg, #00d4aa, #4a9eff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.ql-tagline { font-size: 0.7rem; color: #2d3a52; letter-spacing: 0.5px; margin-bottom: 1rem; }

/* ─ Page header ─────────────────────────────────────────────────────────── */
.page-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 0.1rem;
}
.page-title {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    line-height: 1.2;
    font-family: 'JetBrains Mono', monospace;
    color: #e2e8f0;
}
.page-sub { font-size: 0.75rem; color: #2d3a52; letter-spacing: 0.3px; margin-bottom: 1.2rem; }

/* ─ Metric cards ─────────────────────────────────────────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 8px;
    margin-bottom: 1.2rem;
}
.metric-card {
    background: #0c1120;
    border: 1px solid #111d33;
    border-radius: 10px;
    padding: 14px 16px 12px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s;
}
.metric-card:hover { border-color: rgba(0,212,170,0.3); }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00d4aa33, #4a9eff33);
}
.mc-label {
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #2d3a52;
    margin-bottom: 7px;
    white-space: nowrap;
}
.mc-value {
    font-size: 1.3rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
    color: #c8d8f0;
    line-height: 1;
    margin-bottom: 6px;
}
.mc-value.pos { color: #00d4aa; }
.mc-value.neg { color: #ff4b6e; }
.mc-delta {
    font-size: 0.65rem;
    font-family: 'JetBrains Mono', monospace;
    color: #2d3a52;
    line-height: 1;
}
.mc-delta.pos { color: rgba(0,212,170,0.6); }
.mc-delta.neg { color: rgba(255,75,110,0.6); }

/* ─ Section label ────────────────────────────────────────────────────────── */
.section-label {
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #1e2d47;
    margin: 0.2rem 0 0.7rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #0d1828;
}

/* ─ Signal badge ─────────────────────────────────────────────────────────── */
.signal-wrap { display: flex; align-items: center; gap: 14px; margin: 1rem 0 0.4rem; }
.signal-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 1.5px; color: #2d3a52; }
.signal-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 14px;
    border-radius: 100px;
    font-weight: 600;
    font-size: 0.78rem;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}
.badge-long  { background: rgba(0,212,170,0.08); color:#00d4aa; border:1px solid rgba(0,212,170,0.25); }
.badge-short { background: rgba(255,75,110,0.08); color:#ff4b6e; border:1px solid rgba(255,75,110,0.25); }
.badge-flat  { background: rgba(74,90,122,0.08);  color:#4a5a7a; border:1px solid rgba(74,90,122,0.25); }

/* ─ Portfolio summary ────────────────────────────────────────────────────── */
.port-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-bottom: 1.2rem; }
.port-card {
    background: #0c1120;
    border: 1px solid #111d33;
    border-radius: 10px;
    padding: 18px 20px 14px;
    position: relative;
    overflow: hidden;
}
.port-card.highlight::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00d4aa, #4a9eff);
}
.port-card.highlight-neg::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #ff4b6e, #ff8c42);
}
.pc-label { font-size: 0.62rem; text-transform: uppercase; letter-spacing: 1.5px; color: #2d3a52; margin-bottom: 6px; }
.pc-value { font-size: 1.9rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; line-height: 1.1; }
.pc-sub   { font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; margin-top: 4px; color: #2d3a52; }

/* ─ Divider ──────────────────────────────────────────────────────────────── */
hr { border-color: #0d1828 !important; }

/* ─ Tab pills ────────────────────────────────────────────────────────────── */
[data-testid="stTab"] > div { font-size: 0.8rem !important; font-weight: 500 !important; letter-spacing: 0.3px; }

/* ─ Scrollbar ────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #080c14; }
::-webkit-scrollbar-thumb { background: #111d33; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Palette & shared chart base ────────────────────────────────────────────────
TEAL  = "#00d4aa"
RED   = "#ff4b6e"
BLUE  = "#4a9eff"
MUTED = "#1e2d47"
BG    = "#080c14"
CARD  = "#0c1120"

# NOTE: no margin here — each chart sets its own to avoid the duplicate-kwarg error
PLOT_BASE = dict(
    template="plotly_dark",
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(family="'JetBrains Mono', 'Inter', monospace", size=11, color="#4a5a7a"),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
        bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#8899bb"),
    ),
)

# ── Cached runners ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _run_momentum(ticker, start, end, sw, lw):
    from engine.backtester import run_momentum
    return run_momentum(ticker, start, end, sw, lw)

@st.cache_data(show_spinner=False)
def _run_pairs(ta, tb, start, end, zw, entry, exit_t):
    from engine.backtester import run_pairs
    return run_pairs(ta, tb, start, end, zw, entry, exit_t)

@st.cache_data(show_spinner=False)
def _paper_momentum(ticker, sw, lw, cap, start):
    from engine.paper_trader import run_momentum_paper
    return run_momentum_paper(ticker, sw, lw, cap, start)

@st.cache_data(show_spinner=False)
def _paper_pairs(ta, tb, zw, entry, exit_t, cap, start):
    from engine.paper_trader import run_pairs_paper
    return run_pairs_paper(ta, tb, zw, entry, exit_t, cap, start)

# ── Chart builders ─────────────────────────────────────────────────────────────
def equity_drawdown_chart(s_curve, bh_curve, label):
    sc   = s_curve  / s_curve.iloc[0]
    bc   = bh_curve / bh_curve.iloc[0]
    s_dd = (sc / sc.cummax() - 1) * 100
    b_dd = (bc / bc.cummax() - 1) * 100

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.65, 0.35],
        vertical_spacing=0.025,
        subplot_titles=("", ""),
    )

    # strategy equity — filled gradient area
    fig.add_trace(go.Scatter(
        x=sc.index, y=sc.values, name=label,
        fill="tozeroy",
        fillcolor="rgba(0,212,170,0.04)",
        line=dict(color=TEAL, width=2),
        hovertemplate="<span style='color:#4a5a7a'>%{x|%b %d, %Y}</span><br><b style='color:#00d4aa'>%{y:.3f}</b><extra></extra>",
    ), row=1, col=1)

    # buy & hold
    fig.add_trace(go.Scatter(
        x=bc.index, y=bc.values, name="Buy & Hold",
        line=dict(color=BLUE, width=1.5, dash="dash"),
        opacity=0.6,
        hovertemplate="<span style='color:#4a5a7a'>%{x|%b %d, %Y}</span><br><b style='color:#4a9eff'>%{y:.3f}</b><extra></extra>",
    ), row=1, col=1)

    # strategy drawdown
    fig.add_trace(go.Scatter(
        x=s_dd.index, y=s_dd.values,
        fill="tozeroy", fillcolor="rgba(255,75,110,0.12)",
        line=dict(color=RED, width=1),
        showlegend=False,
        hovertemplate="<span style='color:#4a5a7a'>%{x|%b %d, %Y}</span><br><b style='color:#ff4b6e'>%{y:.1f}%</b><extra></extra>",
    ), row=2, col=1)

    # b&h drawdown
    fig.add_trace(go.Scatter(
        x=b_dd.index, y=b_dd.values,
        line=dict(color=BLUE, width=1, dash="dash"),
        opacity=0.4,
        showlegend=False,
        hovertemplate="<span style='color:#4a5a7a'>%{x|%b %d, %Y}</span><br><b style='color:#4a9eff'>%{y:.1f}%</b><extra></extra>",
    ), row=2, col=1)

    GRID = dict(gridcolor="#0d1828", gridwidth=1, zerolinecolor="#111d33")

    fig.update_layout(
        **PLOT_BASE,
        height=520,
        margin=dict(l=4, r=4, t=8, b=4),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0c1120", bordercolor="#111d33", font_size=12),
        yaxis =dict(**GRID, title="", tickfont=dict(size=10), tickformat=".2f"),
        yaxis2=dict(**GRID, title="", ticksuffix="%", tickfont=dict(size=10)),
        xaxis =dict(**GRID, showspikes=True, spikecolor="#1e2d47", spikethickness=1),
        xaxis2=dict(
            **GRID,
            showspikes=True, spikecolor="#1e2d47", spikethickness=1,
            rangeslider=dict(visible=True, bgcolor="#0c1120", bordercolor="#111d33", thickness=0.03),
        ),
    )
    # Row labels via annotations
    fig.add_annotation(text="EQUITY", x=0.01, y=0.98, xref="paper", yref="paper",
                       showarrow=False, font=dict(size=9, color="#1e2d47"), xanchor="left")
    fig.add_annotation(text="DRAWDOWN", x=0.01, y=0.32, xref="paper", yref="paper",
                       showarrow=False, font=dict(size=9, color="#1e2d47"), xanchor="left")
    return fig


def monthly_heatmap(equity_curve, title="Monthly Returns"):
    monthly = equity_curve.resample("ME").last().pct_change().dropna()
    if len(monthly) < 2:
        return go.Figure()

    df = monthly.to_frame("ret")
    df["year"]  = df.index.year
    df["month"] = df.index.month
    pivot   = df.pivot(index="year", columns="month", values="ret")
    present = [m for m in range(1, 13) if m in pivot.columns]
    z       = pivot[present].values * 100
    xlbls   = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    xlbls   = [xlbls[m-1] for m in present]
    ylbls   = [str(y) for y in pivot.index]
    text    = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z]

    scale = [
        [0.00, "#5c0a1a"], [0.30, "#1f1018"],
        [0.48, "#0c1120"], [0.52, "#0c1120"],
        [0.70, "#091c15"], [1.00, "#005533"],
    ]
    fig = go.Figure(go.Heatmap(
        z=z, x=xlbls, y=ylbls, text=text,
        texttemplate="%{text}",
        textfont=dict(size=10, family="JetBrains Mono, monospace"),
        colorscale=scale, zmid=0, showscale=False,
        hovertemplate="%{y} %{x}: <b>%{z:.2f}%</b><extra></extra>",
        xgap=2, ygap=2,
    ))
    fig.update_layout(
        **PLOT_BASE,
        height=max(160, len(ylbls) * 26 + 55),
        margin=dict(l=4, r=4, t=44, b=4),
        title=dict(text=title, font=dict(size=11, color="#2d3a52"), x=0, xanchor="left"),
        xaxis=dict(side="top", gridcolor="rgba(0,0,0,0)", tickfont=dict(size=10)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", autorange="reversed", tickfont=dict(size=10)),
    )
    return fig


def paper_equity_chart(equity_curve, initial_capital, label):
    is_up   = equity_curve.iloc[-1] >= initial_capital
    color   = TEAL if is_up else RED
    fill_c  = "rgba(0,212,170,0.05)" if is_up else "rgba(255,75,110,0.05)"

    fig = go.Figure()
    fig.add_hline(
        y=initial_capital,
        line=dict(color="#111d33", width=1, dash="dot"),
        annotation_text="Cost basis",
        annotation_font=dict(size=9, color="#1e2d47"),
    )
    fig.add_trace(go.Scatter(
        x=equity_curve.index, y=equity_curve.values,
        fill="tozeroy", fillcolor=fill_c,
        line=dict(color=color, width=2),
        showlegend=False,
        hovertemplate="<span style='color:#4a5a7a'>%{x|%b %d, %Y}</span><br><b>$%{y:,.0f}</b><extra></extra>",
    ))
    fig.update_layout(
        **PLOT_BASE,
        height=300,
        margin=dict(l=4, r=4, t=8, b=4),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0c1120", bordercolor="#111d33", font_size=12),
        yaxis=dict(gridcolor="#0d1828", tickprefix="$", tickformat=",.0f",
                   tickfont=dict(size=10)),
        xaxis=dict(gridcolor="#0d1828", tickfont=dict(size=10)),
    )
    return fig


# ── Custom HTML helpers ────────────────────────────────────────────────────────
def render_metric_cards(sm, bm):
    specs = [
        ("Total Return", "total_return", True),
        ("CAGR",         "cagr",         True),
        ("Sharpe",       "sharpe",       False),
        ("Sortino",      "sortino",      False),
        ("Calmar",       "calmar",       False),
        ("Max Drawdown", "max_drawdown", True),
        ("Win Rate",     "win_rate",     True),
    ]
    cards = ""
    for label, key, is_pct in specs:
        sv, bv = sm[key], bm[key]
        valid_s = sv == sv  # NaN check
        valid_b = bv == bv

        if is_pct:
            display  = f"{sv*100:+.2f}%" if valid_s else "—"
            raw_val  = sv if valid_s else 0
            diff     = (sv - bv) * 100 if (valid_s and valid_b) else None
            delta    = f"{diff:+.2f}% vs B&H" if diff is not None else "—"
        else:
            display  = f"{sv:.2f}" if valid_s else "—"
            raw_val  = sv if valid_s else 0
            diff     = (sv - bv) if (valid_s and valid_b) else None
            delta    = f"{diff:+.2f} vs B&H" if diff is not None else "—"

        val_cls   = "pos" if raw_val >= 0 else "neg"
        delta_cls = "pos" if (diff is not None and diff >= 0) else "neg"
        cards += f"""
        <div class="metric-card">
          <div class="mc-label">{label}</div>
          <div class="mc-value {val_cls}">{display}</div>
          <div class="mc-delta {delta_cls}">{delta}</div>
        </div>"""

    st.markdown(f'<div class="metric-grid">{cards}</div>', unsafe_allow_html=True)


def render_signal_badge(position: str) -> str:
    pos = position.upper()
    if "LONG" in pos or pos == "IN MARKET":
        cls, icon = "badge-long",  "▲"
    elif "SHORT" in pos:
        cls, icon = "badge-short", "▼"
    else:
        cls, icon = "badge-flat",  "◼"
    return (
        f'<div class="signal-wrap">'
        f'<span class="signal-label">Current Signal</span>'
        f'<span class="signal-badge {cls}">{icon}&nbsp;{position}</span>'
        f'</div>'
    )


def render_portfolio_cards(paper):
    pnl   = paper["pnl_dollars"]
    is_up = pnl >= 0
    val_color = "#00d4aa" if is_up else "#ff4b6e"
    sign      = "+" if is_up else ""
    hi_class  = "highlight" if is_up else "highlight-neg"
    pct       = paper["total_return"] * 100

    cards = f"""
    <div class="port-grid">
      <div class="port-card {hi_class}">
        <div class="pc-label">Portfolio Value</div>
        <div class="pc-value" style="color:{val_color}">${paper['current_value']:,.0f}</div>
        <div class="pc-sub" style="color:{val_color}">{pct:+.2f}%</div>
      </div>
      <div class="port-card">
        <div class="pc-label">Starting Capital</div>
        <div class="pc-value" style="color:#c8d8f0">${paper['initial_capital']:,.0f}</div>
        <div class="pc-sub">cost basis</div>
      </div>
      <div class="port-card">
        <div class="pc-label">Total P&L</div>
        <div class="pc-value" style="color:{val_color}">{sign}${abs(pnl):,.0f}</div>
        <div class="pc-sub" style="color:{val_color}">{pct:+.2f}%</div>
      </div>
      <div class="port-card">
        <div class="pc-label">Data As Of</div>
        <div class="pc-value" style="color:#c8d8f0;font-size:1.1rem">{paper['last_updated']}</div>
        <div class="pc-sub">last market close</div>
      </div>
    </div>"""
    st.markdown(cards, unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="ql-logo"><span class="ql-logo-accent">Quant</span>Lab</div>'
        '<div class="ql-tagline">SYSTEMATIC STRATEGY RESEARCH</div>',
        unsafe_allow_html=True,
    )
    st.divider()

    strategy_choice = st.selectbox(
        "Strategy",
        ["Momentum — MA Crossover", "Pairs Trading — Cointegration"],
        label_visibility="collapsed",
    )
    is_pairs = strategy_choice.startswith("Pairs")

    st.markdown("**Universe**")
    if not is_pairs:
        ticker = st.text_input("Ticker", value="SPY", label_visibility="collapsed").strip().upper()
        st.caption(f"Ticker: `{ticker}`")
    else:
        c1, c2 = st.columns(2)
        ticker_a = c1.text_input("Leg A", value="SPY").strip().upper()
        ticker_b = c2.text_input("Leg B", value="QQQ").strip().upper()

    st.markdown("**Period**")
    col_d1, col_d2 = st.columns(2)
    start_date = col_d1.date_input("From", value=date(2015, 1, 1), label_visibility="visible")
    end_date   = col_d2.date_input("To",   value=date(2026, 1, 1), label_visibility="visible")

    with st.expander("⚙  Strategy Parameters"):
        if not is_pairs:
            short_w = st.slider("Short MA (days)", 5, 100, 20)
            long_w  = st.slider("Long MA (days)",  30, 300, 100)
        else:
            zscore_w = st.slider("Z-Score Window", 20, 120, 60)
            entry_t  = st.slider("Entry Threshold σ", 1.0, 4.0, 2.0, 0.1)
            exit_t   = st.slider("Exit Threshold σ", -1.0, 1.0, 0.0, 0.1)

    with st.expander("💼  Paper Portfolio"):
        paper_capital = st.number_input(
            "Starting Capital ($)", value=100_000, step=10_000, min_value=1_000,
        )

    st.markdown("")
    run_btn = st.button("▶  Run Analysis", type="primary", use_container_width=True)
    st.divider()
    st.markdown(
        '<div style="font-size:0.68rem;color:#1e2d47;line-height:1.7">'
        'Data · Yahoo Finance<br>Research use only · Not financial advice<br>'
        '<span style="color:#2d3a52">Built by <b style="color:#4a5a7a">Patricio Putz</b></span>'
        '</div>',
        unsafe_allow_html=True,
    )


# ── Page header ────────────────────────────────────────────────────────────────
if not is_pairs:
    page_title = f"MA({short_w}/{long_w}) · {ticker}"
else:
    page_title = f"Pairs · {ticker_a} / {ticker_b}"

st.markdown(
    f'<div class="page-title">{page_title}</div>'
    f'<div class="page-sub">'
    f'{start_date.strftime("%b %d, %Y")} → {end_date.strftime("%b %d, %Y")}'
    f' &nbsp;·&nbsp; Paper portfolio: {start_date.strftime("%b %Y")} → today'
    f'</div>',
    unsafe_allow_html=True,
)

tab_bt, tab_paper = st.tabs(["  📊  Backtest", "  📋  Paper Portfolio"])

# ── Run analysis ───────────────────────────────────────────────────────────────
if run_btn or "results" not in st.session_state:
    with st.spinner("Fetching market data…"):
        try:
            if not is_pairs:
                results = _run_momentum(ticker, str(start_date), str(end_date), short_w, long_w)
                paper   = _paper_momentum(ticker, short_w, long_w, paper_capital, str(start_date))
            else:
                results = _run_pairs(ticker_a, ticker_b, str(start_date), str(end_date),
                                     zscore_w, entry_t, exit_t)
                paper   = _paper_pairs(ticker_a, ticker_b, zscore_w, entry_t, exit_t,
                                       paper_capital, str(start_date))
            st.session_state["results"] = results
            st.session_state["paper"]   = paper
        except Exception as exc:
            st.error(f"Failed to load data: {exc}")
            st.stop()

results = st.session_state.get("results")
paper   = st.session_state.get("paper")

if results is None:
    st.info("Configure the sidebar and click **Run Analysis**.")
    st.stop()

sm = results["strategy"]
bm = results["buy_hold"]
sn = results["strategy_name"]

# ── Backtest tab ───────────────────────────────────────────────────────────────
with tab_bt:
    render_metric_cards(sm, bm)
    st.plotly_chart(
        equity_drawdown_chart(sm["equity_curve"], bm["equity_curve"], sn),
        use_container_width=True,
    )

    st.markdown('<p class="section-label">Monthly Returns</p>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        fig_l = monthly_heatmap(sm["equity_curve"], f"{sn}")
        if fig_l.data:
            st.plotly_chart(fig_l, use_container_width=True)
    with col_r:
        fig_r = monthly_heatmap(bm["equity_curve"], "Buy & Hold")
        if fig_r.data:
            st.plotly_chart(fig_r, use_container_width=True)

# ── Paper portfolio tab ────────────────────────────────────────────────────────
with tab_paper:
    render_portfolio_cards(paper)

    st.markdown(
        render_signal_badge(paper["current_position"]),
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        paper_equity_chart(paper["equity_curve"], paper["initial_capital"], paper["ticker"]),
        use_container_width=True,
    )

    st.markdown('<p class="section-label">Trade Log</p>', unsafe_allow_html=True)

    if not paper["trades"].empty:
        def _style_action(v):
            return "color:#00d4aa;font-weight:600" if v == "BUY" else (
                   "color:#ff4b6e;font-weight:600" if v == "SELL" else "")

        def _style_pnl(v):
            if isinstance(v, str) and v.startswith("$+"):
                return "color:#00d4aa"
            if isinstance(v, str) and v.startswith("$-"):
                return "color:#ff4b6e"
            return "color:#2d3a52"

        styled = (
            paper["trades"].tail(40).style
            .map(_style_action, subset=["Action"])
            .map(_style_pnl, subset=["P&L"])
            .set_properties(**{"font-family": "JetBrains Mono, monospace",
                                "font-size": "0.82rem", "text-align": "right"})
            .set_properties(subset=["Date", "Action"], **{"text-align": "left"})
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.caption("Detailed trade log not available for this strategy type.")
