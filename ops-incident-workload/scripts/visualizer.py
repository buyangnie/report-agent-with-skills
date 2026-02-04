"""
Visualization module for BO Workload Performance Report.

Generates charts and heatmaps for the analysis results.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from io import BytesIO
import base64

from config import CHART_FIGSIZE, CHART_DPI, COLORS, TIER_COLORS
from analyzer import (
    AnalysisResult,
    ResolverProfile,
    CategoryRisk,
    WorkloadBalanceResult,
    KnowledgeSilo,
    TrendAnalysis,
    TrendPeriod
)


# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette([COLORS["primary"], COLORS["secondary"], COLORS["success"], 
                 COLORS["warning"], COLORS["danger"]])


def fig_to_base64(fig: plt.Figure) -> str:
    """
    Convert matplotlib figure to base64 string.
    
    Args:
        fig: Matplotlib figure
    
    Returns:
        Base64 encoded PNG string
    """
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=CHART_DPI, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_base64


def create_tier_distribution_chart(result: AnalysisResult) -> str:
    """
    Create tier distribution pie chart.
    
    Args:
        result: Analysis result
    
    Returns:
        Base64 encoded chart image
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    
    tiers = ["Tier 1", "Tier 2", "Tier 3"]
    counts = [result.tier_counts.get(tier, 0) for tier in tiers]
    colors = [TIER_COLORS.get(tier, COLORS["primary"]) for tier in tiers]
    
    # Only include non-zero tiers
    non_zero = [(t, c, col) for t, c, col in zip(tiers, counts, colors) if c > 0]
    if not non_zero:
        plt.close(fig)
        return ""
    
    tiers, counts, colors = zip(*non_zero)
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=tiers,
        colors=colors,
        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*sum(counts))})',
        startangle=90,
        explode=[0.02] * len(tiers)
    )
    
    # Style
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    ax.set_title('BO Tier Distribution', fontsize=14, fontweight='bold', pad=20)
    
    return fig_to_base64(fig)


def create_bottleneck_ranking_chart(profiles: List[ResolverProfile], top_n: int = 10) -> str:
    """
    Create horizontal bar chart for bottleneck ranking with P1/P2 ratio indicators.
    
    Args:
        profiles: List of resolver profiles
        top_n: Number of top bottlenecks to show
    
    Returns:
        Base64 encoded chart image
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Sort by bottleneck score
    sorted_profiles = sorted(profiles, key=lambda x: x.bottleneck_score, reverse=True)[:top_n]
    
    if not sorted_profiles:
        plt.close(fig)
        return ""
    
    names = [p.name for p in sorted_profiles]
    scores = [p.bottleneck_score for p in sorted_profiles]
    p1_p2_ratios = [p.priority_index * 100 for p in sorted_profiles]  # Already calculated
    
    # Color based on score
    colors = []
    for score in scores:
        if score >= 0.6:
            colors.append(COLORS["danger"])
        elif score >= 0.4:
            colors.append(COLORS["warning"])
        else:
            colors.append(COLORS["success"])
    
    # Create horizontal bar chart
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, scores, color=colors, edgecolor='white', linewidth=0.5)
    
    # Add value labels with P1/P2 ratio
    for i, (bar, score, ratio) in enumerate(zip(bars, scores, p1_p2_ratios)):
        width = bar.get_width()
        # Score label
        ax.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                f'{score:.2f}', va='center', ha='left', fontsize=9, fontweight='bold')
        # P1/P2 ratio indicator
        if ratio > 0:
            ax.text(0.02, bar.get_y() + bar.get_height()/2,
                    f'P1/P2: {ratio:.0f}%', va='center', ha='left', 
                    fontsize=8, color='white', alpha=0.9)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.set_xlabel('Bottleneck Score')
    ax.set_title('Top Bottleneck Experts (with P1/P2 Ratio)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1.15)
    ax.invert_yaxis()
    
    # Add legend
    legend_patches = [
        mpatches.Patch(color=COLORS["danger"], label='Critical (≥0.6)'),
        mpatches.Patch(color=COLORS["warning"], label='Warning (0.4-0.6)'),
        mpatches.Patch(color=COLORS["success"], label='Normal (<0.4)')
    ]
    ax.legend(handles=legend_patches, loc='lower right')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def create_dependency_heatmap(
    profiles: List[ResolverProfile],
    category_risks: List[CategoryRisk]
) -> str:
    """
    Create resolver × category dependency heatmap.
    
    Args:
        profiles: List of resolver profiles
        category_risks: List of category risks
    
    Returns:
        Base64 encoded chart image
    """
    # Build matrix
    categories = [r.category for r in category_risks if r.ticket_count >= 5][:15]  # Top 15
    resolvers = [p.name for p in profiles if p.total_tickets >= 10][:20]  # Top 20
    
    if not categories or not resolvers:
        return ""
    
    # Create matrix
    matrix = np.zeros((len(resolvers), len(categories)))
    
    for i, resolver in enumerate(resolvers):
        profile = next((p for p in profiles if p.name == resolver), None)
        if profile:
            for j, category in enumerate(categories):
                matrix[i, j] = profile.category_distribution.get(category, 0)
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Normalize by row for better visualization
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    normalized_matrix = matrix / row_sums
    
    sns.heatmap(
        normalized_matrix,
        annot=matrix.astype(int),
        fmt='d',
        cmap='Blues',
        xticklabels=categories,
        yticklabels=resolvers,
        ax=ax,
        cbar_kws={'label': 'Proportion'},
        linewidths=0.5
    )
    
    # Highlight single-point dependencies
    high_risk_categories = [r.category for r in category_risks if r.risk_level == "High"]
    for j, category in enumerate(categories):
        if category in high_risk_categories:
            ax.axvline(x=j, color=COLORS["danger"], linewidth=2, alpha=0.7)
            ax.axvline(x=j+1, color=COLORS["danger"], linewidth=2, alpha=0.7)
    
    ax.set_title('Resolver × Category Dependency Matrix\n(Red borders = High-risk categories)',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Category')
    ax.set_ylabel('Resolver')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig_to_base64(fig)


def create_workload_distribution_chart(
    balance: WorkloadBalanceResult,
    profiles: List[ResolverProfile] = None
) -> str:
    """
    Create workload distribution stacked bar chart showing P1/P2/P3/P4 breakdown.
    
    Args:
        balance: Workload balance result
        profiles: Optional list of resolver profiles for priority breakdown
    
    Returns:
        Base64 encoded chart image
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    if not balance.workload_distribution:
        plt.close(fig)
        return ""
    
    # Sort by total workload
    sorted_items = sorted(balance.workload_distribution.items(), key=lambda x: x[1], reverse=True)
    names = [item[0] for item in sorted_items][:20]  # Top 20
    
    if profiles:
        # Build priority breakdown from profiles
        profile_map = {p.name: p for p in profiles}
        p1_counts = []
        p2_counts = []
        p3_counts = []
        p4_counts = []
        
        for name in names:
            p = profile_map.get(name)
            if p:
                p1_counts.append(p.p1_count)
                p2_counts.append(p.p2_count)
                p3_counts.append(p.p3_count)
                p4_counts.append(p.p4_count)
            else:
                p1_counts.append(0)
                p2_counts.append(0)
                p3_counts.append(0)
                p4_counts.append(0)
        
        x_pos = np.arange(len(names))
        width = 0.7
        
        # Stacked bar chart with priority breakdown
        ax.bar(x_pos, p1_counts, width, label='P1 (Critical)', color=COLORS["danger"], edgecolor='white')
        ax.bar(x_pos, p2_counts, width, bottom=p1_counts, label='P2 (High)', color=COLORS["warning"], edgecolor='white')
        bottom_p3 = np.array(p1_counts) + np.array(p2_counts)
        ax.bar(x_pos, p3_counts, width, bottom=bottom_p3, label='P3 (Medium)', color=COLORS["info"], edgecolor='white')
        bottom_p4 = bottom_p3 + np.array(p3_counts)
        ax.bar(x_pos, p4_counts, width, bottom=bottom_p4, label='P4 (Low)', color=COLORS["success"], edgecolor='white')
        
    else:
        # Fallback: simple bar chart
        workloads = [balance.workload_distribution.get(name, 0) for name in names]
        x_pos = np.arange(len(names))
        avg = balance.avg_workload
        
        colors = []
        for w in workloads:
            if w > avg * 1.5:
                colors.append(COLORS["danger"])
            elif w > avg * 1.2:
                colors.append(COLORS["warning"])
            elif w < avg * 0.5:
                colors.append(COLORS["info"])
            else:
                colors.append(COLORS["primary"])
        
        ax.bar(x_pos, workloads, color=colors, edgecolor='white', linewidth=0.5)
    
    # Add average line
    avg = balance.avg_workload
    ax.axhline(y=avg, color=COLORS["dark"], linestyle='--', linewidth=2, label=f'Average ({avg:.1f})')
    
    # Add Gini coefficient annotations
    gini_text = f'Raw Gini: {balance.gini_coefficient:.3f} ({balance.interpretation})'
    if balance.weighted_gini_coefficient > 0:
        gini_text += f'\nWeighted Gini: {balance.weighted_gini_coefficient:.3f} ({balance.weighted_interpretation})'
    
    ax.text(0.95, 0.95, gini_text,
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
            fontsize=9)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.set_ylabel('Ticket Count')
    ax.set_title('Workload Distribution by Priority', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def create_mttr_by_tier_chart(profiles: List[ResolverProfile]) -> str:
    """
    Create MTTR comparison box plot by tier.
    
    Args:
        profiles: List of resolver profiles
    
    Returns:
        Base64 encoded chart image
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data
    data = {"Tier": [], "MTTR (hours)": []}
    for profile in profiles:
        if profile.avg_mttr_hours > 0:
            data["Tier"].append(profile.tier)
            data["MTTR (hours)"].append(profile.avg_mttr_hours)
    
    if not data["Tier"]:
        plt.close(fig)
        return ""
    
    df = pd.DataFrame(data)
    
    # Create box plot
    tier_order = ["Tier 1", "Tier 2", "Tier 3"]
    tier_colors = [TIER_COLORS.get(t, COLORS["primary"]) for t in tier_order]
    
    box = sns.boxplot(
        x="Tier",
        y="MTTR (hours)",
        data=df,
        order=tier_order,
        palette=tier_colors,
        ax=ax
    )
    
    # Add individual points
    sns.stripplot(
        x="Tier",
        y="MTTR (hours)",
        data=df,
        order=tier_order,
        color=COLORS["dark"],
        alpha=0.5,
        size=4,
        ax=ax
    )
    
    ax.set_title('MTTR Distribution by Tier', fontsize=14, fontweight='bold')
    ax.set_ylabel('MTTR (hours)')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def create_category_coverage_chart(category_risks: List[CategoryRisk], top_n: int = 15) -> str:
    """
    Create category coverage analysis chart.
    
    Args:
        category_risks: List of category risks
        top_n: Number of categories to show
    
    Returns:
        Base64 encoded chart image
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Sort by ticket count
    sorted_risks = sorted(category_risks, key=lambda x: x.ticket_count, reverse=True)[:top_n]
    
    if not sorted_risks:
        plt.close(fig)
        return ""
    
    categories = [r.category for r in sorted_risks]
    ticket_counts = [r.ticket_count for r in sorted_risks]
    resolver_counts = [r.resolver_count for r in sorted_risks]
    risk_levels = [r.risk_level for r in sorted_risks]
    
    x = np.arange(len(categories))
    width = 0.35
    
    # Create grouped bar chart
    bars1 = ax.bar(x - width/2, ticket_counts, width, label='Ticket Count', 
                   color=COLORS["primary"], edgecolor='white')
    bars2 = ax.bar(x + width/2, resolver_counts, width, label='Resolver Count',
                   color=COLORS["secondary"], edgecolor='white')
    
    # Highlight high-risk categories
    for i, risk in enumerate(risk_levels):
        if risk == "High":
            ax.axvspan(i - 0.5, i + 0.5, alpha=0.2, color=COLORS["danger"])
    
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.set_ylabel('Count')
    ax.set_title('Category Coverage Analysis\n(Red background = High-risk single-point dependency)',
                 fontsize=14, fontweight='bold')
    ax.legend()
    
    # Add secondary y-axis for resolver count
    ax2 = ax.twinx()
    ax2.set_ylabel('Resolver Count', color=COLORS["secondary"])
    ax2.tick_params(axis='y', labelcolor=COLORS["secondary"])
    ax2.set_ylim(0, max(resolver_counts) * 1.5)
    
    plt.tight_layout()
    return fig_to_base64(fig)


def create_expert_hourly_heatmap(profiles: List[ResolverProfile], top_n: int = 10) -> str:
    """
    Create hourly activity heatmap for top experts.
    
    Args:
        profiles: List of resolver profiles
        top_n: Number of experts to show
    
    Returns:
        Base64 encoded chart image
    """
    # Filter to BO resolvers (Tier 2 and 3) with hourly data
    bo_profiles = [p for p in profiles if p.tier in ["Tier 2", "Tier 3"] and p.hourly_distribution]
    
    if not bo_profiles:
        return ""
    
    # Sort by ticket count
    sorted_profiles = sorted(bo_profiles, key=lambda x: x.total_tickets, reverse=True)[:top_n]
    
    if not sorted_profiles:
        return ""
    
    # Build matrix
    hours = list(range(24))
    resolvers = [p.name for p in sorted_profiles]
    
    matrix = np.zeros((len(resolvers), 24))
    for i, profile in enumerate(sorted_profiles):
        for hour in range(24):
            matrix[i, hour] = profile.hourly_distribution.get(hour, 0)
    
    # Normalize by row
    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    normalized_matrix = matrix / row_sums
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(14, 6))
    
    sns.heatmap(
        normalized_matrix,
        cmap='YlOrRd',
        xticklabels=hours,
        yticklabels=resolvers,
        ax=ax,
        cbar_kws={'label': 'Activity Proportion'},
        linewidths=0.5
    )
    
    ax.set_title('Expert Hourly Activity Pattern', fontsize=14, fontweight='bold')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Expert')
    
    plt.tight_layout()
    return fig_to_base64(fig)


def create_sla_comparison_chart(profiles: List[ResolverProfile], top_n: int = 15) -> str:
    """
    Create SLA rate comparison chart.

    Args:
        profiles: List of resolver profiles
        top_n: Number of resolvers to show

    Returns:
        Base64 encoded chart image
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Filter and sort profiles
    valid_profiles = [p for p in profiles if p.total_tickets >= 5]
    sorted_profiles = sorted(valid_profiles, key=lambda x: x.sla_rate)[:top_n]  # Lowest first

    if not sorted_profiles:
        plt.close(fig)
        return ""

    names = [p.name for p in sorted_profiles]
    sla_rates = [p.sla_rate * 100 for p in sorted_profiles]
    tiers = [p.tier for p in sorted_profiles]

    # Colors based on tier
    colors = [TIER_COLORS.get(tier, COLORS["primary"]) for tier in tiers]

    # Create bar chart
    y_pos = np.arange(len(names))
    bars = ax.barh(y_pos, sla_rates, color=colors, edgecolor='white', linewidth=0.5)

    # Add threshold lines
    ax.axvline(x=90, color=COLORS["warning"], linestyle='--', linewidth=2, label='Target (90%)')
    ax.axvline(x=80, color=COLORS["danger"], linestyle='--', linewidth=2, label='Critical (80%)')

    # Add value labels
    for bar, rate in zip(bars, sla_rates):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{rate:.1f}%', va='center', ha='left', fontsize=9)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.set_xlabel('SLA Compliance Rate (%)')
    ax.set_title('SLA Compliance Comparison (Lowest First)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 110)
    ax.legend(loc='lower right')

    plt.tight_layout()
    return fig_to_base64(fig)


def create_trend_line_chart(trend_analysis: TrendAnalysis) -> str:
    """
    Create multi-metric trend line chart.

    Args:
        trend_analysis: TrendAnalysis object with period data

    Returns:
        Base64 encoded chart image
    """
    if not trend_analysis or not trend_analysis.periods:
        return ""

    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    periods = trend_analysis.periods
    labels = [p.period_label for p in periods]
    x = np.arange(len(labels))

    # Volume trend
    ax1 = axes[0]
    volumes = [p.ticket_count for p in periods]
    ax1.fill_between(x, volumes, alpha=0.3, color=COLORS["primary"])
    ax1.plot(x, volumes, marker='o', color=COLORS["primary"], linewidth=2, markersize=6)
    ax1.set_ylabel('Ticket Count')
    ax1.set_title(f'Volume Trend ({trend_analysis.period_type.capitalize()})', fontsize=12, fontweight='bold')

    # Add trend annotation
    if trend_analysis.volume_trend:
        color = COLORS["success"] if trend_analysis.volume_trend == "decreasing" else \
                COLORS["danger"] if trend_analysis.volume_trend == "increasing" else COLORS["info"]
        ax1.text(0.98, 0.95, f'{trend_analysis.volume_trend.capitalize()} ({trend_analysis.volume_change_pct:+.1f}%)',
                 transform=ax1.transAxes, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor=color, alpha=0.3), fontsize=10)

    # Average line
    avg_vol = np.mean(volumes)
    ax1.axhline(y=avg_vol, color=COLORS["dark"], linestyle='--', alpha=0.5, label=f'Avg: {avg_vol:.0f}')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)

    # MTTR trend
    ax2 = axes[1]
    mttrs = [p.avg_mttr_hours for p in periods]
    ax2.fill_between(x, mttrs, alpha=0.3, color=COLORS["warning"])
    ax2.plot(x, mttrs, marker='s', color=COLORS["warning"], linewidth=2, markersize=6)
    ax2.set_ylabel('MTTR (hours)')
    ax2.set_title('MTTR Trend', fontsize=12, fontweight='bold')

    if trend_analysis.mttr_trend:
        color = COLORS["success"] if trend_analysis.mttr_trend == "improving" else \
                COLORS["danger"] if trend_analysis.mttr_trend == "deteriorating" else COLORS["info"]
        ax2.text(0.98, 0.95, f'{trend_analysis.mttr_trend.capitalize()} ({trend_analysis.mttr_change_pct:+.1f}%)',
                 transform=ax2.transAxes, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor=color, alpha=0.3), fontsize=10)

    avg_mttr = np.mean(mttrs)
    ax2.axhline(y=avg_mttr, color=COLORS["dark"], linestyle='--', alpha=0.5, label=f'Avg: {avg_mttr:.1f}h')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)

    # SLA trend
    ax3 = axes[2]
    slas = [p.sla_rate * 100 for p in periods]
    ax3.fill_between(x, slas, alpha=0.3, color=COLORS["success"])
    ax3.plot(x, slas, marker='^', color=COLORS["success"], linewidth=2, markersize=6)
    ax3.set_ylabel('SLA Rate (%)')
    ax3.set_title('SLA Compliance Trend', fontsize=12, fontweight='bold')

    if trend_analysis.sla_trend:
        color = COLORS["success"] if trend_analysis.sla_trend == "improving" else \
                COLORS["danger"] if trend_analysis.sla_trend == "deteriorating" else COLORS["info"]
        ax3.text(0.98, 0.95, f'{trend_analysis.sla_trend.capitalize()} ({trend_analysis.sla_change_pct:+.1f}%)',
                 transform=ax3.transAxes, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor=color, alpha=0.3), fontsize=10)

    # Target lines
    ax3.axhline(y=90, color=COLORS["warning"], linestyle='--', alpha=0.7, label='Target (90%)')
    ax3.axhline(y=80, color=COLORS["danger"], linestyle='--', alpha=0.7, label='Critical (80%)')
    ax3.set_ylim(0, 105)
    ax3.legend(loc='lower left')
    ax3.grid(True, alpha=0.3)

    # X-axis labels
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels, rotation=45, ha='right')

    plt.tight_layout()
    return fig_to_base64(fig)


def create_priority_distribution_heatmap(profiles: List[ResolverProfile], top_n: int = 20) -> str:
    """
    Create a heatmap showing priority distribution across resolvers.
    
    Args:
        profiles: List of resolver profiles
        top_n: Number of resolvers to show
    
    Returns:
        Base64 encoded chart image
    """
    # Sort by weighted workload
    sorted_profiles = sorted(profiles, key=lambda x: x.weighted_workload, reverse=True)[:top_n]
    
    if not sorted_profiles:
        return ""
    
    # Build data for heatmap
    resolvers = [p.name for p in sorted_profiles]
    priorities = ['P1', 'P2', 'P3', 'P4']
    
    # Create matrix
    matrix = np.zeros((len(resolvers), len(priorities)))
    for i, p in enumerate(sorted_profiles):
        matrix[i, 0] = p.p1_count
        matrix[i, 1] = p.p2_count
        matrix[i, 2] = p.p3_count
        matrix[i, 3] = p.p4_count
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, max(8, len(resolvers) * 0.4)))
    
    # Create heatmap with custom colormap
    cmap = sns.color_palette([COLORS["danger"], COLORS["warning"], COLORS["info"], COLORS["success"]], as_cmap=True)
    
    sns.heatmap(
        matrix,
        annot=True,
        fmt='.0f',
        cmap='YlOrRd',
        xticklabels=priorities,
        yticklabels=resolvers,
        ax=ax,
        cbar_kws={'label': 'Ticket Count'},
        linewidths=0.5
    )
    
    ax.set_title('Priority Distribution by Resolver\n(Higher P1/P2 = More Critical Work)', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Priority Level')
    ax.set_ylabel('Resolver')
    
    plt.tight_layout()
    return fig_to_base64(fig)


class Visualizer:
    """
    Chart generator for BO Workload Performance Report.
    """
    
    def __init__(self, result: AnalysisResult):
        """
        Initialize visualizer with analysis result.
        
        Args:
            result: Analysis result from BOWorkloadAnalyzer
        """
        self.result = result
    
    def generate_all_charts(self) -> Dict[str, str]:
        """
        Generate all charts for the report.
        
        Returns:
            Dictionary of chart name to base64 encoded image
        """
        charts = {}
        
        # Tier distribution
        charts["tier_distribution"] = create_tier_distribution_chart(self.result)
        
        # Bottleneck ranking (now with P1/P2 ratio)
        charts["bottleneck_ranking"] = create_bottleneck_ranking_chart(
            self.result.resolver_profiles
        )
        
        # Dependency heatmap
        charts["dependency_heatmap"] = create_dependency_heatmap(
            self.result.resolver_profiles,
            self.result.category_risks
        )
        
        # Workload distribution (now with priority breakdown)
        if self.result.workload_balance:
            charts["workload_distribution"] = create_workload_distribution_chart(
                self.result.workload_balance,
                self.result.resolver_profiles  # Pass profiles for priority breakdown
            )
        
        # Priority distribution heatmap (NEW)
        charts["priority_heatmap"] = create_priority_distribution_heatmap(
            self.result.resolver_profiles
        )
        
        # MTTR by tier
        charts["mttr_by_tier"] = create_mttr_by_tier_chart(self.result.resolver_profiles)
        
        # Category coverage
        charts["category_coverage"] = create_category_coverage_chart(
            self.result.category_risks
        )
        
        # Expert hourly heatmap
        charts["expert_hourly"] = create_expert_hourly_heatmap(
            self.result.resolver_profiles
        )
        
        # SLA comparison
        charts["sla_comparison"] = create_sla_comparison_chart(
            self.result.resolver_profiles
        )

        # Trend line chart
        if self.result.trend_analysis and self.result.trend_analysis.periods:
            charts["trend_line"] = create_trend_line_chart(self.result.trend_analysis)

        # Remove empty charts
        charts = {k: v for k, v in charts.items() if v}

        return charts
