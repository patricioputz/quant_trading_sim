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
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    h1 { font-size: 1.75rem !important; font-weight: 700; letter-spacing: -0.5px; }

    .signal-badge {
        display: inline-block;
        padding: 5px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.8px;
        text-transform: uppercase;
    }
    .badge-long  { background:#00d4aa18; color:#00d4aa; border:1px solid #00d4aa55; }
    .badge-short { background:#ff4b4b18; color:#ff4b4b; border:1px solid #ff4b4b55; }
    .badge-cash  { background:#88888818; color:#aaa;    border:1px solid #55555588; }

    div[data-testid="stMetricValue"] > div { font-size: 1.4rem; font-weight: 700; }
    div[data-testid="stMetricLabel"] > div { font-size: 0.75rem; color: #888; }
    div[data-testid="stMetricDelta"] > div { font-size: 0.78rem; }

    .section-label {
        font-size: 0.72rem;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: #555;
        margin-bottom: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Colour palette ─────────────────────────────────────────────────────────────
TEAL  = "#00d4aa"
RED   = "#ff4b4b"
BLUE  = "#4c9be8"
GRAY  = "#555"

PLOT_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="#0e1117",
    plot_bgcolor="#0e1117",
    font=dict(family="Inter, system-ui, sans-serif", size=12, color="#ccc"),
    margin=dict(l=0, r=0, t=36, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
    sc = s_curve  / s_curve.iloc[0]
    bc = bh_curve / bh_curve.iloc[0]
    s_dd = (sc / sc.cummax() - 1) * 100
    b_dd = (bc / bc.cummax() - 1) * 100

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.62, 0.38],
        vertical_spacing=0.03,
    )
    # equity
    fig.add_trace(go.Scatter(
        x=sc.index, y=sc.values, name=label,
        line=dict(color=TEAL, width=2),
        hovertemplate="%{x|%b %d %Y}  <b>%{y:.3f}</b><extra></extra>",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=bc.index, y=bc.values, name="Buy & Hold",
        line=dict(color=BLUE, width=1.5, dash="dot"),
        hovertemplate="%{x|%b %d %Y}  <b>%{y:.3f}</b><extra></extra>",
    ), row=1, col=1)
    # drawdown
    fig.add_trace(go.Scatter(
        x=s_dd.index, y=s_dd.values, name=label,
        fill="tozeroy", fillcolor="rgba(255,75,75,0.15)",
        line=dict(color=RED, width=1),
        showlegend=False,
        hovertemplate="%{x|%b %d %Y}  <b>%{y:.1f}%</b><extra></extra>",
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=b_dd.index, y=b_dd.values,
        line=dict(color=BLUE, width=1, dash="dot"),
        showlegend=False,
        hovertemplate="%{x|%b %d %Y}  <b>%{y:.1f}%</b><extra></extra>",
    ), row=2, col=1)

    fig.update_layout(
        **PLOT_BASE, height=500,
        yaxis =dict(gridcolor="#1a2030", title="Normalised Value"),
        yaxis2=dict(gridcolor="#1a2030", title="Drawdown %", ticksuffix="%"),
        xaxis =dict(gridcolor="#1a2030"),
        xaxis2=dict(
            gridcolor="#1a2030",
            rangeslider=dict(visible=True, bgcolor="#161b27", thickness=0.035),
        ),
    )
    return fig


def monthly_heatmap(equity_curve, title="Monthly Returns"):
    monthly = equity_curve.resample("ME").last().pct_change().dropna()
    df = monthly.to_frame("ret")
    df["year"]  = df.index.year
    df["month"] = df.index.month
    pivot = df.pivot(index="year", columns="month", values="ret")

    present = [m for m in range(1, 13) if m in pivot.columns]
    z    = pivot[present].values * 100
    xlbl = ["Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"]
    xlbl = [xlbl[m-1] for m in present]
    ylbl = [str(y) for y in pivot.index]
    text = [[f"{v:.1f}%" if not np.isnan(v) else "" for v in row] for row in z]

    scale = [
        [0.0, "#6b0f1a"], [0.35, "#2a1215"],
        [0.5, "#161b27"],
        [0.65, "#0d2b1f"], [1.0, "#006644"],
    ]
    fig = go.Figure(go.Heatmap(
        z=z, x=xlbl, y=ylbl, text=text,
        texttemplate="%{text}", textfont=dict(size=11),
        colorscale=scale, zmid=0, showscale=False,
        hovertemplate="%{y} %{x}: <b>%{z:.2f}%</b><extra></extra>",
    ))
    fig.update_layout(
        **PLOT_BASE, height=max(180, len(ylbl) * 28 + 60),
        title=dict(text=title, font=dict(size=13, color="#ccc")),
        xaxis=dict(side="top", gridcolor="transparent"),
        yaxis=dict(gridcolor="transparent", autorange="reversed"),
        margin=dict(l=0, r=0, t=52, b=0),
    )
    return fig


def paper_equity_chart(equity_curve, initial_capital, label):
    fig = go.Figure()
    fig.add_hline(y=initial_capital, line=dict(color=GRAY, width=1, dash="dot"))
    color = TEAL if equity_curve.iloc[-1] >= initial_capital else RED
    fig.add_trace(go.Scatter(
        x=equity_curve.index, y=equity_curve.values,
        name=label, fill="tozeroy",
        fillcolor=f"rgba({'0,212,170' if color == TEAL else '255,75,75'},0.08)",
        line=dict(color=color, width=2),
        hovertemplate="%{x|%b %d %Y}  <b>$%{y:,.0f}</b><extra></extra>",
    ))
    fig.update_layout(
        **PLOT_BASE, height=340,
        yaxis=dict(gridcolor="#1a2030", tickprefix="$", tickformat=",.0f"),
        xaxis=dict(gridcolor="#1a2030"),
        showlegend=False,
    )
    return fig


def metric_row(sm, bm):
    specs = [
        ("Total Return", "total_return", True),
        ("CAGR",         "cagr",         True),
        ("Sharpe",       "sharpe",       False),
        ("Sortino",      "sortino",      False),
        ("Calmar",       "calmar",       False),
        ("Max Drawdown", "max_drawdown", True),
        ("Win Rate",     "win_rate",     True),
    ]
    cols = st.columns(len(specs))
    for col, (label, key, is_pct) in zip(cols, specs):
        sv, bv = sm[key], bm[key]
        if is_pct:
            display = f"{sv*100:+.2f}%" if sv == sv else "—"
            delta   = f"{(sv-bv)*100:+.2f}% vs B&H" if (sv == sv and bv == bv) else None
        else:
            display = f"{sv:.2f}" if sv == sv else "—"
            delta   = f"{sv-bv:+.2f} vs B&H" if (sv == sv and bv == bv) else None
        col.metric(label, display, delta)


def signal_badge(position: str) -> str:
    pos = position.upper()
    if "LONG" in pos or pos == "IN MARKET":
        return f'<span class="signal-badge badge-long">▲ {position}</span>'
    elif "SHORT" in pos:
        return f'<span class="signal-badge badge-short">▼ {position}</span>'
    else:
        return f'<span class="signal-badge badge-cash">◼ {position}</span>'


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## QuantLab")
    st.caption("Systematic Strategy Research")
    st.divider()

    strategy_choice = st.selectbox(
        "Strategy",
        ["Momentum — MA Crossover", "Pairs Trading — Cointegration"],
    )
    is_pairs = strategy_choice.startswith("Pairs")

    st.subheader("Universe")
    if not is_pairs:
        ticker = st.text_input("Ticker", value="SPY").strip().upper()
    else:
        c1, c2 = st.columns(2)
        ticker_a = c1.text_input("Leg A", value="SPY").strip().upper()
        ticker_b = c2.text_input("Leg B", value="QQQ").strip().upper()

    st.subheader("Period")
    start_date = st.date_input("From", value=date(2015, 1, 1))
    end_date   = st.date_input("To",   value=date(2026, 1, 1))

    with st.expander("⚙️  Parameters"):
        if not is_pairs:
            short_w = st.slider("Short MA", 5, 100,  20)
            long_w  = st.slider("Long MA",  30, 300, 100)
        else:
            zscore_w = st.slider("Z-Score Window (days)", 20, 120, 60)
            entry_t  = st.slider("Entry Threshold (σ)",   1.0, 4.0, 2.0, 0.1)
            exit_t   = st.slider("Exit Threshold (σ)",   -1.0, 1.0, 0.0, 0.1)

    with st.expander("💼  Paper Portfolio"):
        paper_capital = st.number_input(
            "Starting Capital ($)", value=100_000, step=10_000, min_value=1_000,
        )

    run_btn = st.button("▶  Run Analysis", type="primary", use_container_width=True)
    st.divider()
    st.caption("Data via Yahoo Finance · For research use only")


# ── Page header ────────────────────────────────────────────────────────────────
if not is_pairs:
    page_title = f"MA({short_w}/{long_w})  ·  {ticker}"
else:
    page_title = f"Pairs Trading  ·  {ticker_a} / {ticker_b}"

st.markdown(f"# {page_title}")
st.caption(
    f"{start_date.strftime('%b %d, %Y')}  →  {end_date.strftime('%b %d, %Y')}"
    f"   ·   Paper portfolio from {start_date.strftime('%b %d, %Y')} to today"
)

tab_bt, tab_paper = st.tabs(["📊  Backtest Analysis", "📋  Paper Portfolio"])

# ── Run ────────────────────────────────────────────────────────────────────────
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
    st.info("Set parameters in the sidebar and click **Run Analysis**.")
    st.stop()

sm = results["strategy"]
bm = results["buy_hold"]
sn = results["strategy_name"]

# ── Backtest tab ───────────────────────────────────────────────────────────────
with tab_bt:
    metric_row(sm, bm)
    st.plotly_chart(equity_drawdown_chart(sm["equity_curve"], bm["equity_curve"], sn),
                    use_container_width=True)

    st.divider()
    st.markdown('<p class="section-label">Monthly Returns</p>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(
            monthly_heatmap(sm["equity_curve"], f"{sn} — Monthly Returns"),
            use_container_width=True,
        )
    with col_r:
        st.plotly_chart(
            monthly_heatmap(bm["equity_curve"], "Buy & Hold — Monthly Returns"),
            use_container_width=True,
        )

# ── Paper portfolio tab ────────────────────────────────────────────────────────
with tab_paper:
    pnl_sign  = "+" if paper["pnl_dollars"] >= 0 else ""
    pnl_color = TEAL if paper["pnl_dollars"] >= 0 else RED

    # Summary row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Portfolio Value",  f"${paper['current_value']:,.0f}",
              f"{paper['total_return']*100:+.2f}%")
    c2.metric("Starting Capital", f"${paper['initial_capital']:,.0f}")
    c3.metric("Total P&L",        f"{pnl_sign}${abs(paper['pnl_dollars']):,.0f}",
              f"{paper['total_return']*100:+.2f}%")
    c4.metric("Data as of",       paper["last_updated"])

    # Current signal
    st.markdown(
        f"**Current Signal** &nbsp; {signal_badge(paper['current_position'])}",
        unsafe_allow_html=True,
    )
    st.markdown("")

    # Equity curve
    st.plotly_chart(
        paper_equity_chart(paper["equity_curve"], paper["initial_capital"],
                           paper["ticker"]),
        use_container_width=True,
    )

    # Trade log (momentum only)
    st.divider()
    if not paper["trades"].empty:
        st.markdown('<p class="section-label">Trade Log</p>', unsafe_allow_html=True)

        def _colour_action(val):
            if val == "BUY":
                return "color: #00d4aa; font-weight:600"
            elif val == "SELL":
                return "color: #ff4b4b; font-weight:600"
            return ""

        def _colour_pnl(val):
            if isinstance(val, str) and val.startswith("$+"):
                return "color: #00d4aa"
            elif isinstance(val, str) and val.startswith("$-"):
                return "color: #ff4b4b"
            return "color: #888"

        styled = (
            paper["trades"]
            .tail(30)
            .style
            .map(_colour_action, subset=["Action"])
            .map(_colour_pnl, subset=["P&L"])
            .set_properties(**{"text-align": "right"})
            .set_properties(subset=["Date", "Action"], **{"text-align": "left"})
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)
    else:
        st.info("Detailed trade log not available for this strategy type.")
