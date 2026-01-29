"""
XLSX Chart Generator — 44 matplotlib charts for the Comprehensive Quality Report.
Each function returns PNG bytes for embedding in Excel.
"""
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Wedge, FancyArrowPatch
import matplotlib.ticker as ticker

from xlsx_theme import (
    setup_chart_style, CHART_COLORS, TEXT_PRIMARY, TEXT_SECONDARY,
    PRIMARY, ACCENT, BORDER_LIGHT,
)

# =============================================================================
# Helpers
# =============================================================================

def _save_chart(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


def _no_data_chart(title="No Data", figsize=(8, 5)) -> bytes:
    fig, ax = plt.subplots(figsize=figsize)
    ax.text(0.5, 0.5, title, ha="center", va="center", fontsize=16,
            color=f"#{TEXT_SECONDARY}", transform=ax.transAxes)
    ax.axis("off")
    return _save_chart(fig)


def _gauge_chart(value, max_val=100, title="", zones=None, figsize=(5, 3.5)):
    """Create a semicircular gauge chart."""
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(aspect="equal"))
    if zones is None:
        zones = [(0, 60, "#ef4444"), (60, 80, "#eab308"), (80, 100, "#22c55e")]
    for start, end, color in zones:
        theta1 = 180 - (end / max_val * 180)
        theta2 = 180 - (start / max_val * 180)
        wedge = Wedge((0, 0), 1, theta1, theta2, width=0.3,
                       facecolor=color, edgecolor="white", linewidth=2)
        ax.add_patch(wedge)
    angle = 180 - (value / max_val * 180)
    angle_rad = np.radians(angle)
    ax.plot([0, 0.7 * np.cos(angle_rad)], [0, 0.7 * np.sin(angle_rad)],
            color=f"#{TEXT_PRIMARY}", linewidth=2)
    ax.plot(0, 0, "o", color=f"#{TEXT_PRIMARY}", markersize=8)
    ax.text(0, -0.35, f"{value:.0f}" if isinstance(value, (int, float)) else str(value),
            ha="center", va="center", fontsize=24, fontweight="bold", color=f"#{TEXT_PRIMARY}")
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.5, 1.3)
    ax.axis("off")
    return fig


def _radar_chart(labels, values, title="", figsize=(6, 6), fill_color=None):
    """Generic radar chart helper."""
    n = len(labels)
    if n < 3:
        return None
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    values_plot = values + [values[0]]
    angles += [angles[0]]
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))
    color = fill_color or CHART_COLORS[0]
    ax.plot(angles, values_plot, "o-", color=color, linewidth=2)
    ax.fill(angles, values_plot, alpha=0.25, color=color)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=20)
    ax.set_ylim(0, 100)
    return fig


# =============================================================================
# Sheet 1 — Executive Summary (3)
# =============================================================================

def chart_exec_health_gauge(score, language="en") -> bytes:
    """Semicircular gauge 0-100 with color zones."""
    setup_chart_style(language)
    if score is None:
        return _no_data_chart("No Data", (5, 3.5))
    title = "Overall Health Score" if language == "en" else "\u7efc\u5408\u5065\u5eb7\u5206\u6570"
    fig = _gauge_chart(float(score), 100, title)
    return _save_chart(fig)


def chart_exec_process_radar(result, language="en") -> bytes:
    """4-axis radar for ITIL processes."""
    setup_chart_style(language)
    if result is None or not hasattr(result, "kpis"):
        return _no_data_chart("No Data", (6, 6))
    kpis = result.kpis
    if language == "en":
        labels = ["Incidents (SLA)", "Changes (Success)", "Requests (Fulfill)", "Problems (Close)"]
    else:
        labels = ["\u4e8b\u4ef6(SLA)", "\u53d8\u66f4(\u6210\u529f\u7387)", "\u8bf7\u6c42(\u5b8c\u6210\u7387)", "\u95ee\u9898(\u5173\u95ed\u7387)"]
    vals = [
        getattr(kpis, "incident_sla_rate", 0) * 100,
        getattr(kpis, "change_success_rate", 0) * 100,
        getattr(kpis, "request_fulfillment_rate", 0) * 100,
        getattr(kpis, "problem_closure_rate", 0) * 100,
    ]
    title = "Process Performance" if language == "en" else "\u6d41\u7a0b\u7ee9\u6548"
    fig = _radar_chart(labels, vals, title)
    if fig is None:
        return _no_data_chart("Insufficient Data", (6, 6))
    return _save_chart(fig)


def chart_exec_sparklines(trends, language="en") -> bytes:
    """6 sparklines in 2x3 grid."""
    setup_chart_style(language)
    if not trends:
        return _no_data_chart()
    fig, axes = plt.subplots(2, 3, figsize=(10, 5))
    axes = axes.flatten()
    kpi_names = list(trends.keys())[:6] if isinstance(trends, dict) else [f"KPI {i+1}" for i in range(min(6, len(trends)))]
    for i, ax in enumerate(axes):
        if i < len(kpi_names):
            key = kpi_names[i]
            data = trends[key] if isinstance(trends, dict) else trends[i] if i < len(trends) else []
            if hasattr(data, "__iter__") and len(list(data)) > 0:
                vals = list(data)
                ax.plot(vals, color=CHART_COLORS[i % len(CHART_COLORS)], linewidth=2)
                ax.fill_between(range(len(vals)), vals, alpha=0.1, color=CHART_COLORS[i % len(CHART_COLORS)])
            ax.set_title(str(key), fontsize=9)
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return _save_chart(fig)


# =============================================================================
# Sheet 2 — Incident Analysis (5)
# =============================================================================

def chart_inc_monthly_trend(monthly_data, language="en") -> bytes:
    """Dual-axis line: incident count + completion rate."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    counts = [getattr(m, "incident_count", 0) for m in monthly_data]
    rates = [getattr(m, "completion_rate", 0) for m in monthly_data]
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(range(len(months)), counts, color=CHART_COLORS[0], alpha=0.7,
            label="Incident Count" if language == "en" else "\u4e8b\u4ef6\u6570")
    ax1.set_xlabel("Month" if language == "en" else "\u6708\u4efd")
    ax1.set_ylabel("Count" if language == "en" else "\u6570\u91cf", color=CHART_COLORS[0])
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels(months, rotation=45, ha="right")
    ax2 = ax1.twinx()
    ax2.plot(range(len(months)), [r * 100 for r in rates], "o-", color=CHART_COLORS[1], linewidth=2,
             label="Completion %" if language == "en" else "\u5b8c\u6210\u7387")
    ax2.set_ylabel("Completion %" if language == "en" else "\u5b8c\u6210\u7387%", color=CHART_COLORS[1])
    ax2.set_ylim(0, 105)
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.95))
    title = "Incident Monthly Trend" if language == "en" else "\u4e8b\u4ef6\u6708\u5ea6\u8d8b\u52bf"
    ax1.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_inc_priority_pie(priority_rows, language="en") -> bytes:
    """Pie chart of P1/P2/P3/P4 counts."""
    setup_chart_style(language)
    if not priority_rows:
        return _no_data_chart()
    labels = [getattr(r, "priority", f"P{i}") for i, r in enumerate(priority_rows)]
    sizes = [getattr(r, "count", 0) for r in priority_rows]
    if sum(sizes) == 0:
        return _no_data_chart()
    colors = CHART_COLORS[:len(labels)]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    title = "Incidents by Priority" if language == "en" else "\u4e8b\u4ef6\u4f18\u5148\u7ea7\u5206\u5e03"
    ax.set_title(title)
    return _save_chart(fig)


def chart_inc_category_top10(category_rows, language="en") -> bytes:
    """Horizontal bar of top 10 categories."""
    setup_chart_style(language)
    if not category_rows:
        return _no_data_chart()
    rows = sorted(category_rows, key=lambda r: getattr(r, "count", 0), reverse=True)[:10]
    labels = [getattr(r, "category", f"Cat{i}") for i, r in enumerate(rows)]
    counts = [getattr(r, "count", 0) for r in rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    y_pos = range(len(labels))
    ax.barh(y_pos, counts, color=CHART_COLORS[0])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Count" if language == "en" else "\u6570\u91cf")
    title = "Top 10 Incident Categories" if language == "en" else "\u4e8b\u4ef6\u5206\u7c7bTOP10"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_inc_mttr_boxplot(incidents_df, language="en") -> bytes:
    """Box plot of Resolution Time by Priority."""
    setup_chart_style(language)
    if incidents_df is None or (isinstance(incidents_df, pd.DataFrame) and incidents_df.empty):
        return _no_data_chart()
    df = incidents_df
    fig, ax = plt.subplots(figsize=(8, 5))
    if isinstance(df, pd.DataFrame) and "Priority" in df.columns and "Resolution Time(m)" in df.columns:
        groups = df.groupby("Priority")["Resolution Time(m)"].apply(list).to_dict()
        labels_sorted = sorted(groups.keys())
        data = [groups[k] for k in labels_sorted]
        bp = ax.boxplot(data, labels=labels_sorted, patch_artist=True)
        for i, box in enumerate(bp["boxes"]):
            box.set_facecolor(CHART_COLORS[i % len(CHART_COLORS)])
            box.set_alpha(0.7)
    else:
        ax.text(0.5, 0.5, "Missing columns", ha="center", va="center", transform=ax.transAxes)
    ax.set_ylabel("Resolution Time (min)" if language == "en" else "\u89e3\u51b3\u65f6\u95f4(\u5206\u949f)")
    title = "MTTR by Priority" if language == "en" else "\u5404\u4f18\u5148\u7ea7\u89e3\u51b3\u65f6\u95f4"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_inc_p1p2_trend(monthly_data, language="en") -> bytes:
    """Line chart of high priority percentage over months."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    pcts = [getattr(m, "high_priority_pct", 0) * 100 for m in monthly_data]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(len(months)), pcts, "o-", color=CHART_COLORS[3], linewidth=2)
    ax.fill_between(range(len(months)), pcts, alpha=0.1, color=CHART_COLORS[3])
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.set_ylabel("P1/P2 %" if language == "en" else "\u9ad8\u4f18\u5148\u7ea7%")
    title = "P1/P2 Incident Trend" if language == "en" else "\u9ad8\u4f18\u5148\u7ea7\u4e8b\u4ef6\u8d8b\u52bf"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


# =============================================================================
# Sheet 3 — SLA Analysis (5)
# =============================================================================

def chart_sla_gauge_response(rate, language="en") -> bytes:
    """Gauge for response SLA rate (0-1)."""
    setup_chart_style(language)
    if rate is None:
        return _no_data_chart("No Data", (5, 3.5))
    title = "Response SLA" if language == "en" else "\u54cd\u5e94SLA"
    fig = _gauge_chart(float(rate) * 100, 100, title)
    return _save_chart(fig)


def chart_sla_gauge_resolution(rate, language="en") -> bytes:
    """Gauge for resolution SLA rate (0-1)."""
    setup_chart_style(language)
    if rate is None:
        return _no_data_chart("No Data", (5, 3.5))
    title = "Resolution SLA" if language == "en" else "\u89e3\u51b3SLA"
    fig = _gauge_chart(float(rate) * 100, 100, title)
    return _save_chart(fig)


def chart_sla_monthly_trend(monthly_data, language="en") -> bytes:
    """SLA rate over months with 95% threshold."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    rates = [getattr(m, "sla_rate", 0) * 100 for m in monthly_data]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(len(months)), rates, "o-", color=CHART_COLORS[0], linewidth=2)
    ax.axhline(y=95, color=CHART_COLORS[3], linestyle="--", linewidth=1.5,
               label="95% Target" if language == "en" else "95%\u76ee\u6807")
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.set_ylabel("SLA %")
    ax.set_ylim(0, 105)
    ax.legend()
    title = "SLA Monthly Trend" if language == "en" else "SLA\u6708\u5ea6\u8d8b\u52bf"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_sla_violation_by_priority(violations, language="en") -> bytes:
    """Stacked bar of SLA violations by priority."""
    setup_chart_style(language)
    if not violations:
        return _no_data_chart()
    labels = [getattr(v, "priority", f"P{i}") for i, v in enumerate(violations)]
    response_v = [getattr(v, "response_violations", 0) for v in violations]
    resolution_v = [getattr(v, "resolution_violations", 0) for v in violations]
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(labels))
    ax.bar(x, response_v, color=CHART_COLORS[3], label="Response" if language == "en" else "\u54cd\u5e94")
    ax.bar(x, resolution_v, bottom=response_v, color=CHART_COLORS[0],
           label="Resolution" if language == "en" else "\u89e3\u51b3")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_ylabel("Violations" if language == "en" else "\u8fdd\u89c4\u6570")
    title = "SLA Violations by Priority" if language == "en" else "\u5404\u4f18\u5148\u7ea7SLA\u8fdd\u89c4"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_sla_violation_heatmap(violations, language="en") -> bytes:
    """Heatmap of violations by category x month."""
    setup_chart_style(language)
    if not violations:
        return _no_data_chart("No Data", (10, 6))
    # Build matrix from violation objects
    cats = sorted(set(getattr(v, "category", "Unknown") for v in violations))
    months = sorted(set(getattr(v, "month", "Unknown") for v in violations))
    if not cats or not months:
        return _no_data_chart("No Data", (10, 6))
    matrix = np.zeros((len(cats), len(months)))
    cat_idx = {c: i for i, c in enumerate(cats)}
    month_idx = {m: i for i, m in enumerate(months)}
    for v in violations:
        ci = cat_idx.get(getattr(v, "category", "Unknown"), 0)
        mi = month_idx.get(getattr(v, "month", "Unknown"), 0)
        matrix[ci, mi] += getattr(v, "count", 1)
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels(cats)
    fig.colorbar(im, ax=ax)
    title = "SLA Violation Heatmap" if language == "en" else "SLA\u8fdd\u89c4\u70ed\u529b\u56fe"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


# =============================================================================
# Sheet 4 — Change Analysis (5)
# =============================================================================

def chart_chg_type_pie(change_types, language="en") -> bytes:
    """Pie by change type."""
    setup_chart_style(language)
    if not change_types:
        return _no_data_chart()
    labels = [getattr(r, "type", f"Type{i}") for i, r in enumerate(change_types)]
    sizes = [getattr(r, "count", 0) for r in change_types]
    if sum(sizes) == 0:
        return _no_data_chart()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(sizes, labels=labels, colors=CHART_COLORS[:len(labels)], autopct="%1.1f%%", startangle=90)
    title = "Changes by Type" if language == "en" else "\u53d8\u66f4\u7c7b\u578b\u5206\u5e03"
    ax.set_title(title)
    return _save_chart(fig)


def chart_chg_success_trend(monthly_data, language="en") -> bytes:
    """Success rate line with 90% threshold."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    rates = [getattr(m, "success_rate", 0) * 100 for m in monthly_data]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(len(months)), rates, "o-", color=CHART_COLORS[1], linewidth=2)
    ax.axhline(y=90, color=CHART_COLORS[3], linestyle="--", linewidth=1.5,
               label="90% Target" if language == "en" else "90%\u76ee\u6807")
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.set_ylabel("Success %")
    ax.set_ylim(0, 105)
    ax.legend()
    title = "Change Success Rate Trend" if language == "en" else "\u53d8\u66f4\u6210\u529f\u7387\u8d8b\u52bf"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_chg_category_bar(categories, language="en") -> bytes:
    """Grouped bar: total vs failed."""
    setup_chart_style(language)
    if not categories:
        return _no_data_chart()
    labels = [getattr(r, "category", f"Cat{i}") for i, r in enumerate(categories)]
    totals = [getattr(r, "total", 0) for r in categories]
    failed = [getattr(r, "failed", 0) for r in categories]
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w/2, totals, w, color=CHART_COLORS[0], label="Total" if language == "en" else "\u603b\u8ba1")
    ax.bar(x + w/2, failed, w, color=CHART_COLORS[3], label="Failed" if language == "en" else "\u5931\u8d25")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()
    title = "Changes by Category" if language == "en" else "\u53d8\u66f4\u5206\u7c7b"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_chg_incident_scatter(changes_df, language="en") -> bytes:
    """Scatter: X=duration, Y=risk, color by incident_caused."""
    setup_chart_style(language)
    if changes_df is None or (isinstance(changes_df, pd.DataFrame) and changes_df.empty):
        return _no_data_chart()
    df = changes_df
    fig, ax = plt.subplots(figsize=(8, 5))
    if isinstance(df, pd.DataFrame) and "Duration(h)" in df.columns and "Risk Score" in df.columns:
        colors_map = {True: CHART_COLORS[3], False: CHART_COLORS[1], 1: CHART_COLORS[3], 0: CHART_COLORS[1]}
        if "Incident Caused" in df.columns:
            c = df["Incident Caused"].map(lambda v: colors_map.get(v, CHART_COLORS[0]))
        else:
            c = CHART_COLORS[0]
        ax.scatter(df["Duration(h)"], df["Risk Score"], c=c, alpha=0.6, s=40)
        ax.set_xlabel("Duration (h)" if language == "en" else "\u6301\u7eed\u65f6\u95f4(\u5c0f\u65f6)")
        ax.set_ylabel("Risk Score" if language == "en" else "\u98ce\u9669\u5206")
    else:
        ax.text(0.5, 0.5, "Missing columns", ha="center", va="center", transform=ax.transAxes)
    title = "Change Risk vs Duration" if language == "en" else "\u53d8\u66f4\u98ce\u9669vs\u6301\u7eed\u65f6\u95f4"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_chg_planning_accuracy(monthly_data, language="en") -> bytes:
    """Line of on-time % per month."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    pcts = [getattr(m, "on_time_pct", 0) * 100 for m in monthly_data]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(len(months)), pcts, "o-", color=CHART_COLORS[4], linewidth=2)
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.set_ylabel("On-time %" if language == "en" else "\u51c6\u65f6%")
    ax.set_ylim(0, 105)
    title = "Change Planning Accuracy" if language == "en" else "\u53d8\u66f4\u8ba1\u5212\u51c6\u786e\u7387"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


# =============================================================================
# Sheet 5 — Request Analysis (5)
# =============================================================================

def chart_req_type_pie(request_types, language="en") -> bytes:
    """Pie by request type."""
    setup_chart_style(language)
    if not request_types:
        return _no_data_chart()
    labels = [getattr(r, "type", f"Type{i}") for i, r in enumerate(request_types)]
    sizes = [getattr(r, "count", 0) for r in request_types]
    if sum(sizes) == 0:
        return _no_data_chart()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(sizes, labels=labels, colors=CHART_COLORS[:len(labels)], autopct="%1.1f%%", startangle=90)
    title = "Requests by Type" if language == "en" else "\u8bf7\u6c42\u7c7b\u578b\u5206\u5e03"
    ax.set_title(title)
    return _save_chart(fig)


def chart_req_csat_bar(csat_dist, language="en") -> bytes:
    """Bar chart of CSAT scores 1-5."""
    setup_chart_style(language)
    if not csat_dist:
        return _no_data_chart()
    labels = [getattr(b, "score", i+1) for i, b in enumerate(csat_dist)]
    counts = [getattr(b, "count", 0) for b in csat_dist]
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [CHART_COLORS[3], CHART_COLORS[2], CHART_COLORS[2], CHART_COLORS[1], CHART_COLORS[0]]
    ax.bar(range(len(labels)), counts, color=colors[:len(labels)])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([str(l) for l in labels])
    ax.set_xlabel("Score" if language == "en" else "\u8bc4\u5206")
    ax.set_ylabel("Count" if language == "en" else "\u6570\u91cf")
    title = "CSAT Distribution" if language == "en" else "\u6ee1\u610f\u5ea6\u5206\u5e03"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_req_monthly_trend(monthly_data, language="en") -> bytes:
    """Dual Y: volume + avg CSAT."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    volumes = [getattr(m, "request_count", 0) for m in monthly_data]
    csats = [getattr(m, "avg_csat", 0) for m in monthly_data]
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(range(len(months)), volumes, color=CHART_COLORS[0], alpha=0.7,
            label="Volume" if language == "en" else "\u6570\u91cf")
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels(months, rotation=45, ha="right")
    ax1.set_ylabel("Volume" if language == "en" else "\u6570\u91cf", color=CHART_COLORS[0])
    ax2 = ax1.twinx()
    ax2.plot(range(len(months)), csats, "o-", color=CHART_COLORS[2], linewidth=2,
             label="Avg CSAT" if language == "en" else "\u5e73\u5747\u6ee1\u610f\u5ea6")
    ax2.set_ylabel("Avg CSAT", color=CHART_COLORS[2])
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.95))
    title = "Request Monthly Trend" if language == "en" else "\u8bf7\u6c42\u6708\u5ea6\u8d8b\u52bf"
    ax1.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_req_fulfillment_boxplot(requests_df, language="en") -> bytes:
    """Box plot of Fulfillment Time by Request Type."""
    setup_chart_style(language)
    if requests_df is None or (isinstance(requests_df, pd.DataFrame) and requests_df.empty):
        return _no_data_chart()
    df = requests_df
    fig, ax = plt.subplots(figsize=(8, 5))
    if isinstance(df, pd.DataFrame) and "Request Type" in df.columns and "Fulfillment Time(h)" in df.columns:
        groups = df.groupby("Request Type")["Fulfillment Time(h)"].apply(list).to_dict()
        labels_sorted = sorted(groups.keys())
        data = [groups[k] for k in labels_sorted]
        bp = ax.boxplot(data, labels=labels_sorted, patch_artist=True)
        for i, box in enumerate(bp["boxes"]):
            box.set_facecolor(CHART_COLORS[i % len(CHART_COLORS)])
            box.set_alpha(0.7)
        ax.set_xticklabels(labels_sorted, rotation=45, ha="right")
    else:
        ax.text(0.5, 0.5, "Missing columns", ha="center", va="center", transform=ax.transAxes)
    ax.set_ylabel("Fulfillment Time (h)" if language == "en" else "\u5b8c\u6210\u65f6\u95f4(\u5c0f\u65f6)")
    title = "Fulfillment Time by Type" if language == "en" else "\u5404\u7c7b\u578b\u5b8c\u6210\u65f6\u95f4"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_req_dept_heatmap(requests_df, language="en") -> bytes:
    """Heatmap of request volume by type x department."""
    setup_chart_style(language)
    if requests_df is None or (isinstance(requests_df, pd.DataFrame) and requests_df.empty):
        return _no_data_chart("No Data", (10, 6))
    df = requests_df
    fig, ax = plt.subplots(figsize=(10, 6))
    if isinstance(df, pd.DataFrame) and "Request Type" in df.columns and "Department" in df.columns:
        pivot = df.pivot_table(index="Request Type", columns="Department", aggfunc="size", fill_value=0)
        im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_yticklabels(pivot.index)
        fig.colorbar(im, ax=ax)
    else:
        ax.text(0.5, 0.5, "Missing columns", ha="center", va="center", transform=ax.transAxes)
    title = "Request Volume: Type x Department" if language == "en" else "\u8bf7\u6c42\u91cf:\u7c7b\u578b\u00d7\u90e8\u95e8"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


# =============================================================================
# Sheet 6 — Problem Analysis (5)
# =============================================================================

def chart_prb_status_funnel(status_rows, language="en") -> bytes:
    """Funnel / horizontal bar by status."""
    setup_chart_style(language)
    if not status_rows:
        return _no_data_chart()
    labels = [getattr(r, "status", f"S{i}") for i, r in enumerate(status_rows)]
    counts = [getattr(r, "count", 0) for r in status_rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    y_pos = range(len(labels))
    ax.barh(y_pos, counts, color=CHART_COLORS[:len(labels)])
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Count" if language == "en" else "\u6570\u91cf")
    title = "Problem Status Funnel" if language == "en" else "\u95ee\u9898\u72b6\u6001\u6f0f\u6597"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_prb_rootcause_pie(rootcause_rows, language="en") -> bytes:
    """Pie of root cause categories."""
    setup_chart_style(language)
    if not rootcause_rows:
        return _no_data_chart()
    labels = [getattr(r, "category", f"RC{i}") for i, r in enumerate(rootcause_rows)]
    sizes = [getattr(r, "count", 0) for r in rootcause_rows]
    if sum(sizes) == 0:
        return _no_data_chart()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(sizes, labels=labels, colors=CHART_COLORS[:len(labels)], autopct="%1.1f%%", startangle=90)
    title = "Root Cause Categories" if language == "en" else "\u6839\u56e0\u5206\u7c7b"
    ax.set_title(title)
    return _save_chart(fig)


def chart_prb_monthly_bar(monthly_data, language="en") -> bytes:
    """Bar + cumulative line."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    counts = [getattr(m, "problem_count", 0) for m in monthly_data]
    cumulative = np.cumsum(counts).tolist()
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(range(len(months)), counts, color=CHART_COLORS[0], alpha=0.7,
            label="Monthly" if language == "en" else "\u6708\u5ea6")
    ax1.set_xticks(range(len(months)))
    ax1.set_xticklabels(months, rotation=45, ha="right")
    ax1.set_ylabel("Count" if language == "en" else "\u6570\u91cf")
    ax2 = ax1.twinx()
    ax2.plot(range(len(months)), cumulative, "o-", color=CHART_COLORS[3], linewidth=2,
             label="Cumulative" if language == "en" else "\u7d2f\u8ba1")
    ax2.set_ylabel("Cumulative" if language == "en" else "\u7d2f\u8ba1")
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.95))
    title = "Problem Monthly Trend" if language == "en" else "\u95ee\u9898\u6708\u5ea6\u8d8b\u52bf"
    ax1.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_prb_impact_bubble(problems_df, language="en") -> bytes:
    """Bubble chart: X=age, Y=related incidents, size=priority."""
    setup_chart_style(language)
    if problems_df is None or (isinstance(problems_df, pd.DataFrame) and problems_df.empty):
        return _no_data_chart()
    df = problems_df
    fig, ax = plt.subplots(figsize=(8, 5))
    if isinstance(df, pd.DataFrame):
        age_col = "Age(days)" if "Age(days)" in df.columns else None
        inc_col = "Related Incidents" if "Related Incidents" in df.columns else None
        pri_col = "Priority" if "Priority" in df.columns else None
        if age_col and inc_col:
            sizes = df[pri_col].map({"P1": 200, "P2": 120, "P3": 60, "P4": 30}).fillna(50) if pri_col else 50
            ax.scatter(df[age_col], df[inc_col], s=sizes, alpha=0.6, color=CHART_COLORS[0])
            ax.set_xlabel("Age (days)" if language == "en" else "\u5e74\u9f84(\u5929)")
            ax.set_ylabel("Related Incidents" if language == "en" else "\u5173\u8054\u4e8b\u4ef6")
        else:
            ax.text(0.5, 0.5, "Missing columns", ha="center", va="center", transform=ax.transAxes)
    title = "Problem Impact Analysis" if language == "en" else "\u95ee\u9898\u5f71\u54cd\u5206\u6790"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_prb_rca_trend(monthly_data, language="en") -> bytes:
    """RCA completion rate line over months."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    rates = [getattr(m, "rca_completion_rate", 0) * 100 for m in monthly_data]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(len(months)), rates, "o-", color=CHART_COLORS[4], linewidth=2)
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.set_ylabel("RCA Completion %" if language == "en" else "RCA\u5b8c\u6210\u7387%")
    ax.set_ylim(0, 105)
    title = "RCA Completion Trend" if language == "en" else "RCA\u5b8c\u6210\u7387\u8d8b\u52bf"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


# =============================================================================
# Sheet 7 — Cross-Process (4)
# =============================================================================

def chart_cross_sankey(change_links, problem_links, language="en") -> bytes:
    """Sankey-style flow using matplotlib patches/arrows."""
    setup_chart_style(language)
    if not change_links and not problem_links:
        return _no_data_chart()
    fig, ax = plt.subplots(figsize=(10, 6))
    # Simplified flow diagram
    nodes = {
        "Changes": (0.1, 0.7), "Incidents": (0.5, 0.5), "Problems": (0.1, 0.3),
        "Resolved": (0.9, 0.5),
    }
    for name, (x, y) in nodes.items():
        box = FancyBboxPatch((x - 0.08, y - 0.06), 0.16, 0.12,
                              boxstyle="round,pad=0.02", facecolor=CHART_COLORS[0], alpha=0.7)
        ax.add_patch(box)
        ax.text(x, y, name, ha="center", va="center", fontsize=10, color="white", fontweight="bold")
    # Arrows
    links = []
    if change_links:
        links.append(("Changes", "Incidents", len(change_links) if hasattr(change_links, "__len__") else 1))
    if problem_links:
        links.append(("Problems", "Incidents", len(problem_links) if hasattr(problem_links, "__len__") else 1))
    links.append(("Incidents", "Resolved", 1))
    for src, dst, weight in links:
        sx, sy = nodes[src]
        dx, dy = nodes[dst]
        arrow = FancyArrowPatch((sx + 0.08, sy), (dx - 0.08, dy),
                                 arrowstyle="->", mutation_scale=15,
                                 linewidth=max(1, min(weight, 5)), color=f"#{TEXT_SECONDARY}")
        ax.add_patch(arrow)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0, 1)
    ax.axis("off")
    title = "Cross-Process Flow" if language == "en" else "\u8de8\u6d41\u7a0b\u5173\u8054"
    ax.set_title(title, fontsize=13, fontweight="bold")
    return _save_chart(fig)


def chart_cross_radar(process_health, language="en") -> bytes:
    """Radar chart of process health scores."""
    setup_chart_style(language)
    if not process_health:
        return _no_data_chart("No Data", (6, 6))
    labels = [getattr(r, "process", f"P{i}") for i, r in enumerate(process_health)]
    values = [getattr(r, "score", 0) for r in process_health]
    title = "Process Health Radar" if language == "en" else "\u6d41\u7a0b\u5065\u5eb7\u96f7\u8fbe"
    fig = _radar_chart(labels, values, title)
    if fig is None:
        return _no_data_chart("Insufficient Data", (6, 6))
    return _save_chart(fig)


def chart_cross_timeline(change_links, language="en") -> bytes:
    """Timeline scatter of change->incident events."""
    setup_chart_style(language)
    if not change_links:
        return _no_data_chart()
    fig, ax = plt.subplots(figsize=(10, 6))
    dates = [getattr(cl, "date", i) for i, cl in enumerate(change_links)]
    impacts = [getattr(cl, "impact", 1) for cl in change_links]
    ax.scatter(range(len(dates)), impacts, c=CHART_COLORS[3], s=60, alpha=0.7)
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([str(d) for d in dates], rotation=45, ha="right")
    ax.set_ylabel("Impact" if language == "en" else "\u5f71\u54cd")
    title = "Change-Incident Timeline" if language == "en" else "\u53d8\u66f4-\u4e8b\u4ef6\u65f6\u95f4\u7ebf"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_cross_heatmap(correlations, language="en") -> bytes:
    """Correlation heatmap between processes."""
    setup_chart_style(language)
    if correlations is None:
        return _no_data_chart("No Data", (10, 6))
    fig, ax = plt.subplots(figsize=(10, 6))
    if isinstance(correlations, pd.DataFrame):
        matrix = correlations.values
        labels_x = list(correlations.columns)
        labels_y = list(correlations.index)
    elif isinstance(correlations, np.ndarray):
        matrix = correlations
        labels_x = labels_y = [f"P{i}" for i in range(matrix.shape[0])]
    elif isinstance(correlations, dict):
        keys = sorted(correlations.keys())
        matrix = np.array([[correlations.get(k, {}).get(k2, 0) for k2 in keys] for k in keys])
        labels_x = labels_y = keys
    else:
        return _no_data_chart("No Data", (10, 6))
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=-1, vmax=1)
    ax.set_xticks(range(len(labels_x)))
    ax.set_xticklabels(labels_x, rotation=45, ha="right")
    ax.set_yticks(range(len(labels_y)))
    ax.set_yticklabels(labels_y)
    fig.colorbar(im, ax=ax)
    # Annotate
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center", fontsize=8)
    title = "Process Correlation" if language == "en" else "\u6d41\u7a0b\u76f8\u5173\u6027"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


# =============================================================================
# Sheet 8 — Personnel (5)
# =============================================================================

def chart_pers_workload_bar(personnel, language="en") -> bytes:
    """Horizontal bar sorted by count."""
    setup_chart_style(language)
    if not personnel:
        return _no_data_chart()
    rows = sorted(personnel, key=lambda r: getattr(r, "count", 0), reverse=True)
    labels = [getattr(r, "name", f"P{i}") for i, r in enumerate(rows)]
    counts = [getattr(r, "count", 0) for r in rows]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(range(len(labels)), counts, color=CHART_COLORS[0])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("Ticket Count" if language == "en" else "\u5de5\u5355\u6570")
    title = "Personnel Workload" if language == "en" else "\u4eba\u5458\u5de5\u4f5c\u91cf"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_pers_load_boxplot(personnel, language="en") -> bytes:
    """Box plot of workload distribution."""
    setup_chart_style(language)
    if not personnel:
        return _no_data_chart()
    counts = [getattr(r, "count", 0) for r in personnel]
    fig, ax = plt.subplots(figsize=(8, 5))
    bp = ax.boxplot([counts], patch_artist=True, labels=["Workload" if language == "en" else "\u5de5\u4f5c\u91cf"])
    bp["boxes"][0].set_facecolor(CHART_COLORS[0])
    bp["boxes"][0].set_alpha(0.7)
    ax.set_ylabel("Ticket Count" if language == "en" else "\u5de5\u5355\u6570")
    title = "Workload Distribution" if language == "en" else "\u5de5\u4f5c\u91cf\u5206\u5e03"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_pers_skill_heatmap(incidents_df, language="en") -> bytes:
    """Heatmap of person x category counts."""
    setup_chart_style(language)
    if incidents_df is None or (isinstance(incidents_df, pd.DataFrame) and incidents_df.empty):
        return _no_data_chart("No Data", (10, 6))
    df = incidents_df
    fig, ax = plt.subplots(figsize=(10, 6))
    if isinstance(df, pd.DataFrame) and "Assigned To" in df.columns and "Category" in df.columns:
        pivot = df.pivot_table(index="Assigned To", columns="Category", aggfunc="size", fill_value=0)
        # Limit to top 15 people
        top = pivot.sum(axis=1).nlargest(15).index
        pivot = pivot.loc[top]
        im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_xticklabels(pivot.columns, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_yticklabels(pivot.index, fontsize=8)
        fig.colorbar(im, ax=ax)
    else:
        ax.text(0.5, 0.5, "Missing columns", ha="center", va="center", transform=ax.transAxes)
    title = "Skill Matrix" if language == "en" else "\u6280\u80fd\u77e9\u9635"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_pers_efficiency_scatter(personnel, language="en") -> bytes:
    """Scatter: X=count, Y=avg_resolution_min, color by SLA rate."""
    setup_chart_style(language)
    if not personnel:
        return _no_data_chart()
    counts = [getattr(r, "count", 0) for r in personnel]
    resolutions = [getattr(r, "avg_resolution_min", 0) for r in personnel]
    sla_rates = [getattr(r, "sla_rate", 0.5) for r in personnel]
    fig, ax = plt.subplots(figsize=(8, 5))
    sc = ax.scatter(counts, resolutions, c=sla_rates, cmap="RdYlGn", s=60, alpha=0.7, vmin=0, vmax=1)
    fig.colorbar(sc, ax=ax, label="SLA Rate")
    ax.set_xlabel("Ticket Count" if language == "en" else "\u5de5\u5355\u6570")
    ax.set_ylabel("Avg Resolution (min)" if language == "en" else "\u5e73\u5747\u89e3\u51b3\u65f6\u95f4(\u5206)")
    title = "Personnel Efficiency" if language == "en" else "\u4eba\u5458\u6548\u7387"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_pers_top10_radar(personnel, language="en") -> bytes:
    """Radar for top 10 personnel on multiple metrics."""
    setup_chart_style(language)
    if not personnel:
        return _no_data_chart("No Data", (6, 6))
    top10 = sorted(personnel, key=lambda r: getattr(r, "count", 0), reverse=True)[:10]
    if len(top10) < 3:
        return _no_data_chart("Insufficient Data", (6, 6))
    labels = [getattr(r, "name", f"P{i}") for i, r in enumerate(top10)]
    # Normalize count to 0-100
    max_count = max(getattr(r, "count", 1) for r in top10) or 1
    values = [getattr(r, "count", 0) / max_count * 100 for r in top10]
    title = "Top 10 Personnel" if language == "en" else "TOP10\u4eba\u5458"
    fig = _radar_chart(labels, values, title)
    if fig is None:
        return _no_data_chart("Insufficient Data", (6, 6))
    return _save_chart(fig)


# =============================================================================
# Sheet 9 — Time Analysis (5)
# =============================================================================

def chart_time_four_process_trend(monthly_data, language="en") -> bytes:
    """Multi-line for 4 process counts."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    processes = {
        ("Incidents" if language == "en" else "\u4e8b\u4ef6"): "incident_count",
        ("Changes" if language == "en" else "\u53d8\u66f4"): "change_count",
        ("Requests" if language == "en" else "\u8bf7\u6c42"): "request_count",
        ("Problems" if language == "en" else "\u95ee\u9898"): "problem_count",
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (label, attr) in enumerate(processes.items()):
        vals = [getattr(m, attr, 0) for m in monthly_data]
        ax.plot(range(len(months)), vals, "o-", color=CHART_COLORS[i], linewidth=2, label=label)
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.legend()
    ax.set_ylabel("Count" if language == "en" else "\u6570\u91cf")
    title = "Four Process Trend" if language == "en" else "\u56db\u5927\u6d41\u7a0b\u8d8b\u52bf"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_time_dow_bar(dow_data, language="en") -> bytes:
    """Bar chart by day of week."""
    setup_chart_style(language)
    if not dow_data:
        return _no_data_chart()
    labels = [getattr(d, "day", f"D{i}") for i, d in enumerate(dow_data)]
    counts = [getattr(d, "count", 0) for d in dow_data]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(len(labels)), counts, color=CHART_COLORS[0])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Count" if language == "en" else "\u6570\u91cf")
    title = "Activity by Day of Week" if language == "en" else "\u6309\u661f\u671f\u5206\u5e03"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_time_hour_heatmap(incidents_df, language="en") -> bytes:
    """Heatmap of hour x weekday counts."""
    setup_chart_style(language)
    if incidents_df is None or (isinstance(incidents_df, pd.DataFrame) and incidents_df.empty):
        return _no_data_chart("No Data", (10, 6))
    df = incidents_df
    fig, ax = plt.subplots(figsize=(10, 6))
    if isinstance(df, pd.DataFrame) and "Hour" in df.columns and "Weekday" in df.columns:
        pivot = df.pivot_table(index="Hour", columns="Weekday", aggfunc="size", fill_value=0)
        im = ax.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(pivot.shape[1]))
        ax.set_xticklabels(pivot.columns)
        ax.set_yticks(range(pivot.shape[0]))
        ax.set_yticklabels(pivot.index)
        fig.colorbar(im, ax=ax)
    else:
        ax.text(0.5, 0.5, "Missing columns", ha="center", va="center", transform=ax.transAxes)
    title = "Incident Hour x Weekday" if language == "en" else "\u4e8b\u4ef6\u65f6\u6bb5\u00d7\u661f\u671f"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_time_quarterly(monthly_data, language="en") -> bytes:
    """Quarterly aggregated bar + line."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    # Group by quarter
    quarters = {}
    for m in monthly_data:
        month_str = getattr(m, "month", "")
        count = getattr(m, "incident_count", 0) + getattr(m, "change_count", 0) + \
                getattr(m, "request_count", 0) + getattr(m, "problem_count", 0)
        # Simple quarter assignment
        try:
            month_num = int(str(month_str).split("-")[1]) if "-" in str(month_str) else 0
            q = f"Q{(month_num - 1) // 3 + 1}"
        except (ValueError, IndexError):
            q = "Q1"
        quarters[q] = quarters.get(q, 0) + count
    labels = sorted(quarters.keys())
    values = [quarters[q] for q in labels]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(len(labels)), values, color=CHART_COLORS[0], alpha=0.7)
    ax.plot(range(len(labels)), values, "o-", color=CHART_COLORS[3], linewidth=2)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_ylabel("Total Volume" if language == "en" else "\u603b\u91cf")
    title = "Quarterly Summary" if language == "en" else "\u5b63\u5ea6\u6c47\u603b"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


def chart_time_forecast(monthly_data, language="en") -> bytes:
    """Line with linear forecast + confidence band."""
    setup_chart_style(language)
    if not monthly_data:
        return _no_data_chart()
    counts = [getattr(m, "incident_count", 0) for m in monthly_data]
    n = len(counts)
    x = np.arange(n)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x, counts, "o-", color=CHART_COLORS[0], linewidth=2, label="Actual" if language == "en" else "\u5b9e\u9645")
    if n >= 2:
        coeffs = np.polyfit(x, counts, 1)
        trend_fn = np.poly1d(coeffs)
        forecast_x = np.arange(n + 3)
        forecast_y = trend_fn(forecast_x)
        std = np.std(counts)
        ax.plot(forecast_x, forecast_y, "--", color=CHART_COLORS[3], linewidth=1.5,
                label="Forecast" if language == "en" else "\u9884\u6d4b")
        ax.fill_between(forecast_x, forecast_y - std, forecast_y + std, alpha=0.1, color=CHART_COLORS[3])
    months = [getattr(m, "month", str(i)) for i, m in enumerate(monthly_data)]
    months += [f"+{i}" for i in range(1, 4)]
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.legend()
    ax.set_ylabel("Incident Count" if language == "en" else "\u4e8b\u4ef6\u6570")
    title = "Trend Forecast" if language == "en" else "\u8d8b\u52bf\u9884\u6d4b"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)


# =============================================================================
# Sheet 10 — Action Plan (2)
# =============================================================================

def chart_action_priority_pie(actions, language="en") -> bytes:
    """Pie by action priority."""
    setup_chart_style(language)
    if not actions:
        return _no_data_chart()
    from collections import Counter
    priorities = Counter(getattr(a, "priority", "Medium") for a in actions)
    labels = list(priorities.keys())
    sizes = list(priorities.values())
    if sum(sizes) == 0:
        return _no_data_chart()
    color_map = {"High": CHART_COLORS[3], "Medium": CHART_COLORS[2], "Low": CHART_COLORS[1],
                 "\u9ad8": CHART_COLORS[3], "\u4e2d": CHART_COLORS[2], "\u4f4e": CHART_COLORS[1]}
    colors = [color_map.get(l, CHART_COLORS[0]) for l in labels]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    title = "Actions by Priority" if language == "en" else "\u884c\u52a8\u8ba1\u5212\u4f18\u5148\u7ea7"
    ax.set_title(title)
    return _save_chart(fig)


def chart_action_process_bar(actions, language="en") -> bytes:
    """Stacked bar by process."""
    setup_chart_style(language)
    if not actions:
        return _no_data_chart()
    from collections import Counter
    processes = Counter(getattr(a, "process", "General") for a in actions)
    labels = list(processes.keys())
    counts = list(processes.values())
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(range(len(labels)), counts, color=CHART_COLORS[:len(labels)])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Action Count" if language == "en" else "\u884c\u52a8\u6570")
    title = "Actions by Process" if language == "en" else "\u5404\u6d41\u7a0b\u884c\u52a8\u8ba1\u5212"
    ax.set_title(title)
    fig.tight_layout()
    return _save_chart(fig)
