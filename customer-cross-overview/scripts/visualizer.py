"""
Comprehensive Visualizer for Customer Quality Report.

Generates charts and visualizations for all ITIL processes.
"""

import base64
from io import BytesIO
from typing import Dict, List

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from config import COLORS
from analyzer import ComprehensiveResult, TrendData


class ComprehensiveVisualizer:
    """Generate visualizations for comprehensive report."""

    def __init__(self, result: ComprehensiveResult):
        self.result = result
        self.colors = {
            'primary': '#2563EB',
            'success': '#059669',
            'warning': '#D97706',
            'danger': '#DC2626',
            'info': '#0891B2',
            'gray': '#6B7280',
            'incident': '#3B82F6',
            'change': '#10B981',
            'request': '#F59E0B',
            'problem': '#EC4899',
        }

    def generate_all_charts(self) -> Dict[str, str]:
        """Generate all charts and return as base64 encoded strings."""
        charts = {}

        # Trend charts
        if self.result.trends:
            if 'incident_volume' in self.result.trends:
                charts['incident_volume'] = self._generate_trend_chart(
                    self.result.trends['incident_volume'],
                    'Incident Volume',
                    self.colors['incident']
                )

            if 'sla' in self.result.trends:
                charts['sla_trend'] = self._generate_trend_chart(
                    self.result.trends['sla'],
                    'SLA Compliance %',
                    self.colors['success']
                )

            if 'mttr' in self.result.trends:
                charts['mttr_trend'] = self._generate_trend_chart(
                    self.result.trends['mttr'],
                    'Avg MTTR (hours)',
                    self.colors['warning']
                )

        # Process distribution pie chart
        charts['process_distribution'] = self._generate_process_distribution()

        # Health gauge
        charts['health_gauge'] = self._generate_health_gauge()

        return charts

    def _generate_trend_chart(
        self,
        trend_data: TrendData,
        title: str,
        color: str
    ) -> str:
        """Generate a trend line chart."""
        if not trend_data.points:
            return ""

        fig, ax = plt.subplots(figsize=(6, 3), dpi=100)

        # Data
        labels = [p.period for p in trend_data.points]
        values = [p.value for p in trend_data.points]

        # Simplify labels for readability
        if len(labels) > 6:
            display_labels = [''] * len(labels)
            step = len(labels) // 4
            for i in range(0, len(labels), step):
                display_labels[i] = labels[i]
            labels = display_labels

        x = np.arange(len(values))

        # Plot
        ax.fill_between(x, values, alpha=0.2, color=color)
        ax.plot(x, values, color=color, linewidth=2, marker='o', markersize=4)

        # Add trend line
        if len(values) >= 2:
            z = np.polyfit(x, values, 1)
            p = np.poly1d(z)
            ax.plot(x, p(x), '--', color=self.colors['gray'], alpha=0.5, linewidth=1)

        # Styling
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8, rotation=45, ha='right')
        ax.set_ylabel(title, fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Add min/max annotations
        if values:
            max_idx = np.argmax(values)
            min_idx = np.argmin(values)
            ax.annotate(f'{values[max_idx]:.1f}', (max_idx, values[max_idx]),
                       textcoords="offset points", xytext=(0, 5),
                       ha='center', fontsize=8, color=color)
            if max_idx != min_idx:
                ax.annotate(f'{values[min_idx]:.1f}', (min_idx, values[min_idx]),
                           textcoords="offset points", xytext=(0, -12),
                           ha='center', fontsize=8, color=self.colors['gray'])

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _generate_process_distribution(self) -> str:
        """Generate process distribution pie chart."""
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)

        sizes = [
            self.result.total_incidents,
            self.result.total_changes,
            self.result.total_requests,
            self.result.total_problems
        ]

        # Filter out zeros
        labels = ['Incidents', 'Changes', 'Requests', 'Problems']
        colors = [
            self.colors['incident'],
            self.colors['change'],
            self.colors['request'],
            self.colors['problem']
        ]

        non_zero = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
        if not non_zero:
            return ""

        sizes, labels, colors = zip(*non_zero)

        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.0f%%',
            startangle=90,
            explode=[0.02] * len(sizes)
        )

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        ax.set_title('Record Distribution by Process', fontsize=11, fontweight='bold')
        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _generate_health_gauge(self) -> str:
        """Generate health score gauge."""
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)

        # Score
        score = self.result.health_score

        # Color based on score
        if score >= 90:
            color = self.colors['success']
        elif score >= 80:
            color = '#FBBF24'
        elif score >= 70:
            color = self.colors['warning']
        else:
            color = self.colors['danger']

        # Draw gauge
        theta = np.linspace(np.pi, 0, 100)
        r = 1

        # Background arc
        ax.fill_between(
            theta, 0, r,
            alpha=0.1,
            color=self.colors['gray'],
            transform=ax.transData + plt.matplotlib.transforms.Affine2D().rotate_around(0, 0, 0)
        )

        # Create arc segments
        for i, (start, end, c) in enumerate([
            (0, 0.5, self.colors['danger']),
            (0.5, 0.7, self.colors['warning']),
            (0.7, 0.9, '#FBBF24'),
            (0.9, 1.0, self.colors['success'])
        ]):
            theta_seg = np.linspace(np.pi * (1 - end), np.pi * (1 - start), 50)
            ax.plot(np.cos(theta_seg), np.sin(theta_seg), linewidth=12, color=c, alpha=0.3)

        # Score indicator
        score_angle = np.pi * (1 - score / 100)
        ax.plot([0, 0.7 * np.cos(score_angle)], [0, 0.7 * np.sin(score_angle)],
               linewidth=4, color=color)
        ax.scatter([0.7 * np.cos(score_angle)], [0.7 * np.sin(score_angle)],
                  s=100, color=color, zorder=5)

        # Center text
        ax.text(0, -0.2, f'{score:.0f}', ha='center', va='center',
               fontsize=24, fontweight='bold', color=color)
        ax.text(0, -0.4, self.result.health_grade, ha='center', va='center',
               fontsize=10, color=self.colors['gray'])

        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.6, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')


def generate_sparkline(values: List[float], color: str = '#2563EB') -> str:
    """Generate a simple sparkline."""
    if not values or len(values) < 2:
        return ""

    fig, ax = plt.subplots(figsize=(2.5, 0.8), dpi=100)

    x = np.arange(len(values))
    ax.fill_between(x, values, alpha=0.2, color=color)
    ax.plot(x, values, color=color, linewidth=1.5)

    # Mark endpoints
    ax.scatter([0, len(values) - 1], [values[0], values[-1]], s=20, color=color, zorder=5)

    ax.set_xlim(-0.5, len(values) - 0.5)
    ax.axis('off')

    plt.tight_layout(pad=0)

    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor='white', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
