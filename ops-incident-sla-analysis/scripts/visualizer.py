"""
Visualization Engine for SLA Violation Analysis.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from utils import IMG_DIR, COLORS, CHART_COLORS, RISK_COLORS


class VizEngine:
    @staticmethod
    def save_chart(fig, filename):
        """Save chart to images directory."""
        os.makedirs(IMG_DIR, exist_ok=True)
        path = os.path.join(IMG_DIR, filename)
        fig.savefig(path, dpi=100, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        return path

    @staticmethod
    def sla_gauge_chart(rate, title, filename):
        """Create a gauge-like chart for SLA rate."""
        fig, ax = plt.subplots(figsize=(6, 4))

        # Simple bar representation
        colors = ['#ef4444' if rate < 90 else '#f59e0b' if rate < 95 else '#10b981']
        ax.barh([0], [rate], color=colors[0], height=0.5)
        ax.barh([0], [100], color='#e5e7eb', height=0.5, alpha=0.3)
        ax.axvline(x=95, color='#374151', linestyle='--', label='Target 95%')

        ax.set_xlim(0, 100)
        ax.set_yticks([])
        ax.set_xlabel('SLA Compliance Rate (%)')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend()

        return VizEngine.save_chart(fig, filename)

    @staticmethod
    def bar_chart(data, title, filename, horizontal=True, color=None):
        """Create bar chart from Series or dict."""
        if len(data) == 0:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        if hasattr(data, 'index'):
            labels = [str(x)[:20] for x in data.index]
            values = data.values
        else:
            labels = [str(x)[:20] for x in data.keys()]
            values = list(data.values())

        bar_color = color or CHART_COLORS[0]

        if horizontal:
            y_pos = range(len(labels))
            ax.barh(y_pos, values, color=bar_color)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(labels)
            ax.invert_yaxis()
        else:
            x_pos = range(len(labels))
            ax.bar(x_pos, values, color=bar_color)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(labels, rotation=45, ha='right')

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        return VizEngine.save_chart(fig, filename)

    @staticmethod
    def pie_chart(data, title, filename, colors=None):
        """Create pie chart."""
        if len(data) == 0:
            return None

        fig, ax = plt.subplots(figsize=(8, 6))

        if hasattr(data, 'index'):
            labels = [str(x) for x in data.index]
            values = data.values
        else:
            labels = list(data.keys())
            values = list(data.values())

        chart_colors = colors or CHART_COLORS[:len(labels)]

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            colors=chart_colors,
            startangle=90
        )

        ax.set_title(title, fontsize=12, fontweight='bold')

        return VizEngine.save_chart(fig, filename)

    @staticmethod
    def risk_distribution_chart(data, title, filename):
        """Create risk distribution chart with specific colors."""
        if len(data) == 0:
            return None

        fig, ax = plt.subplots(figsize=(8, 5))

        labels = list(data.keys())
        values = list(data.values())
        colors = [RISK_COLORS.get(l, '#6b7280') for l in labels]

        ax.bar(labels, values, color=colors)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_ylabel('Count')

        for i, v in enumerate(values):
            ax.text(i, v + 0.5, str(v), ha='center', fontweight='bold')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        return VizEngine.save_chart(fig, filename)

    @staticmethod
    def trend_line(data, title, filename, xlabel='', ylabel=''):
        """Create trend line chart."""
        if len(data) == 0:
            return None

        fig, ax = plt.subplots(figsize=(10, 5))

        if hasattr(data, 'index'):
            x = [str(i) for i in data.index]
            y = data.values
        else:
            x = list(range(len(data)))
            y = list(data.values())

        ax.plot(x, y, marker='o', color=CHART_COLORS[0], linewidth=2, markersize=6)
        ax.fill_between(range(len(x)), y, alpha=0.1, color=CHART_COLORS[0])

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_xticks(range(len(x)))
        ax.set_xticklabels(x, rotation=45, ha='right')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        return VizEngine.save_chart(fig, filename)

    @staticmethod
    def stacked_bar_chart(df, x_col, y_cols, title, filename, colors=None):
        """Create stacked bar chart."""
        if len(df) == 0:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        x = range(len(df))
        bottom = [0] * len(df)
        chart_colors = colors or CHART_COLORS

        for i, col in enumerate(y_cols):
            ax.bar(x, df[col], bottom=bottom, label=col, color=chart_colors[i % len(chart_colors)])
            bottom = [b + v for b, v in zip(bottom, df[col])]

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([str(v)[:15] for v in df[x_col]], rotation=45, ha='right')
        ax.legend()

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        return VizEngine.save_chart(fig, filename)
