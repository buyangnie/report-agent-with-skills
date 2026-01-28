"""
Visualization Engine for Ops Deep Dive Report.
Modern Light Theme - Clean, Professional Charts
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
import pandas as pd
import os
from utils import IMG_DIR, COLORS, CHART_COLORS, PASTEL_COLORS

# Suppress font warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Modern Light Chart Style Configuration
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 11,
    'axes.unicode_minus': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#e5e7eb',
    'axes.linewidth': 0.8,
    'axes.grid': True,
    'grid.color': '#f3f4f6',
    'grid.linewidth': 0.5,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.dpi': 100,
    'savefig.dpi': 150,
    'savefig.facecolor': 'white',
    'savefig.edgecolor': 'none',
})


class VizEngine:
    """Modern Light Chart Generation Engine."""
    
    @staticmethod
    def _setup_style():
        """Apply modern light style."""
        sns.set_style("white")
        
    @staticmethod
    def _save(filename):
        """Save figure with clean white background."""
        path = os.path.join(IMG_DIR, filename)
        plt.tight_layout(pad=1.5)
        plt.savefig(path, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
        return path
    
    @staticmethod
    def pie_chart(data, title, filename, colors=None):
        """Modern donut chart with clean aesthetics."""
        VizEngine._setup_style()
        fig, ax = plt.subplots(figsize=(8, 6))
        
        colors = colors or PASTEL_COLORS[:len(data)]
        
        # Create donut effect
        wedges, texts, autotexts = ax.pie(
            data.values, 
            labels=None,  # Remove labels from pie
            autopct='%1.1f%%',
            colors=colors[:len(data)],
            startangle=90,
            pctdistance=0.75,
            wedgeprops={'linewidth': 2, 'edgecolor': 'white'}
        )
        
        # Add center circle for donut effect
        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        ax.add_patch(centre_circle)
        
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('600')
            autotext.set_color(COLORS['text'])
        
        # Add legend outside
        ax.legend(wedges, data.index, loc='center left', bbox_to_anchor=(1, 0.5),
                 frameon=False, fontsize=10)
        
        ax.set_title(title, fontsize=14, fontweight='600', color=COLORS['text'], pad=20)
        return VizEngine._save(filename)
    
    @staticmethod
    def bar_chart(data, title, filename, xlabel='', ylabel='', horizontal=False, color=None):
        """Clean bar chart with rounded corners effect."""
        VizEngine._setup_style()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Use Chart Colors cycle if no color specified
        color = color or CHART_COLORS[0]
        
        if horizontal:
            bars = ax.barh(data.index.astype(str), data.values, color=color, 
                          height=0.6, edgecolor='white', linewidth=0) # Removed linewidth
            ax.set_xlabel(ylabel, fontweight='500', color=COLORS['text_secondary'])
            ax.invert_yaxis()
            # Annotate
            for bar, val in zip(bars, data.values):
                ax.text(bar.get_width() + max(data.values)*0.02, 
                       bar.get_y() + bar.get_height()/2, 
                       f'{int(val)}', va='center', fontsize=10, 
                       color=COLORS['text'], fontweight='500')
        else:
            bars = ax.bar(data.index.astype(str), data.values, color=color,
                         width=0.6, edgecolor='white', linewidth=0) # Removed linewidth
            ax.set_xlabel(xlabel, fontweight='500', color=COLORS['text_secondary'])
            ax.set_ylabel(ylabel, fontweight='500', color=COLORS['text_secondary'])
            plt.xticks(rotation=45, ha='right')
            # Annotate
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max(data.values)*0.02,
                       f'{int(height)}', ha='center', va='bottom', fontsize=10,
                       color=COLORS['text'], fontweight='500')
        
        ax.set_title(title, fontsize=14, fontweight='600', color='#111827', pad=15)
        ax.tick_params(colors=COLORS['text_secondary'])
        
        return VizEngine._save(filename)
    
    @staticmethod
    def trend_line(data, title, filename, xlabel='', ylabel=''):
        """Smooth trend line with gradient fill."""
        VizEngine._setup_style()
        fig, ax = plt.subplots(figsize=(12, 5))
        
        x = range(len(data))
        
        # Main line - Thinner, smoother
        ax.plot(x, data.values, marker='o', linewidth=3, markersize=8, 
               color=CHART_COLORS[0], markerfacecolor='white', 
               markeredgewidth=2.5, markeredgecolor=CHART_COLORS[0])
        
        # Gradient fill
        ax.fill_between(x, data.values, alpha=0.1, color=CHART_COLORS[0])
        
        # Annotate points
        for i, val in enumerate(data.values):
            ax.annotate(f'{int(val)}', (i, val), textcoords="offset points", 
                       xytext=(0, 12), ha='center', fontsize=9, 
                       color=COLORS['text'], fontweight='500')
        
        ax.set_xticks(x)
        labels = [str(l)[-7:] if len(str(l)) > 7 else str(l) for l in data.index]
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_xlabel(xlabel, fontweight='500', color=COLORS['text_secondary'])
        ax.set_ylabel(ylabel, fontweight='500', color=COLORS['text_secondary'])
        ax.set_title(title, fontsize=14, fontweight='600', color='#111827', pad=15)
        ax.tick_params(colors=COLORS['text_secondary'])
        
        return VizEngine._save(filename)
    
    @staticmethod
    def heatmap(data, title, filename):
        """Clean heatmap with modern styling."""
        VizEngine._setup_style()
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Custom colormap - light to primary
        cmap = sns.light_palette(CHART_COLORS[0], as_cmap=True, n_colors=10)
        
        sns.heatmap(data, cmap=cmap, annot=True, fmt='d', linewidths=2, 
                   linecolor='white', ax=ax, cbar_kws={'label': 'Ticket Count', 'shrink': 0.8}, 
                   annot_kws={'size': 9, 'weight': '500', 'color': '#374151'})
        
        ax.set_title(title, fontsize=14, fontweight='600', color='#111827', pad=15)
        ax.set_xlabel('Hour', fontweight='500', color=COLORS['text_secondary'])
        ax.set_ylabel('Day of Week', fontweight='500', color=COLORS['text_secondary'])
        ax.tick_params(colors=COLORS['text_secondary'])
        
        return VizEngine._save(filename)
    
    @staticmethod
    def scatter_matrix(data, x_col, y_col, label_col, title, filename, size_col=None):
        """Bubble chart with quadrant analysis."""
        VizEngine._setup_style()
        fig, ax = plt.subplots(figsize=(10, 8))
        
        x = data[x_col]
        y = data[y_col]
        
        # Exclude Unassigned if present
        mask = data[label_col] != 'Unassigned'
        x = x[mask]
        y = y[mask]
        labels = data[label_col][mask]
        
        sizes = 150  # Default scalar size
        if size_col and size_col in data.columns:
            size_data = data[size_col][mask]
            sizes = size_data.apply(lambda v: max(v * 2, 80))
        
        # Scatter with soft colors
        scatter = ax.scatter(x, y, s=sizes, c=CHART_COLORS[0], alpha=0.6, 
                           edgecolors='white', linewidth=1.5)
        
        # Quadrant lines
        x_mean = x.mean()
        y_mean = y.mean()
        ax.axvline(x_mean, color=COLORS['border'], linestyle=':', linewidth=2)
        ax.axhline(y_mean, color=COLORS['border'], linestyle=':', linewidth=2)
        
        # Quadrant labels with background
        ax.text(x.max(), y.min(), 'High Output\nFast Resolution', ha='right', va='bottom', 
               fontsize=10, color=COLORS['success'], fontweight='700', alpha=0.9)
        ax.text(x.min(), y.max(), 'Low Output\nSlow Resolution', ha='left', va='top', 
               fontsize=10, color=COLORS['danger'], fontweight='700', alpha=0.9)
        
        # Annotate top performers
        for i, label in enumerate(labels):
            if x.iloc[i] > x.quantile(0.8) or y.iloc[i] > y.quantile(0.8):
                ax.annotate(label, (x.iloc[i], y.iloc[i]), textcoords="offset points",
                           xytext=(8, 8), fontsize=9, color=COLORS['text'], fontweight='500')
        
        ax.set_xlabel(x_col, fontweight='500', color=COLORS['text_secondary'])
        ax.set_ylabel(y_col, fontweight='500', color=COLORS['text_secondary'])
        ax.set_title(title, fontsize=14, fontweight='600', color='#111827', pad=15)
        ax.tick_params(colors=COLORS['text_secondary'])
        
        return VizEngine._save(filename)
    
    @staticmethod
    def grouped_bar(data, title, filename, xlabel='', ylabel=''):
        """Grouped bar chart with modern styling."""
        VizEngine._setup_style()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = np.arange(len(data.index))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, data['mean'], width, label='Mean', 
                      color=CHART_COLORS[0], edgecolor='white', linewidth=0)
        bars2 = ax.bar(x + width/2, data['median'], width, label='Median', 
                      color=CHART_COLORS[4], edgecolor='white', linewidth=0) # Use violet for secondary
        
        ax.set_xlabel(xlabel, fontweight='500', color=COLORS['text_secondary'])
        ax.set_ylabel(ylabel, fontweight='500', color=COLORS['text_secondary'])
        ax.set_title(title, fontsize=14, fontweight='600', color='#111827', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(data.index)
        ax.legend(frameon=False)
        ax.tick_params(colors=COLORS['text_secondary'])
        
        # Annotate
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(data['mean'])*0.02,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=9, 
                   color=COLORS['text'], fontweight='500')
        
        return VizEngine._save(filename)
    
    @staticmethod
    def keyword_cloud(keywords, title, filename):
        """Horizontal bar chart for keywords with gradient colors."""
        VizEngine._setup_style()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if not keywords:
            ax.text(0.5, 0.5, 'No keyword data', ha='center', va='center', 
                   fontsize=14, color=COLORS['text_secondary'])
            return VizEngine._save(filename)
        
        words, counts = zip(*keywords)
        
        # Create gradient colors based on count
        max_count = max(counts)
        colors = [plt.cm.Blues(0.4 + 0.5 * (c / max_count)) for c in counts]
        
        bars = ax.barh(words, counts, color=colors, height=0.6, 
                      edgecolor='white', linewidth=0.5)
        ax.invert_yaxis()
        
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + max_count*0.02, bar.get_y() + bar.get_height()/2,
                   str(count), va='center', fontsize=10, color=COLORS['text'], fontweight='500')
        
        ax.set_title(title, fontsize=14, fontweight='600', color=COLORS['text'], pad=15)
        ax.set_xlabel('Frequency', fontweight='500', color=COLORS['text_secondary'])
        ax.tick_params(colors=COLORS['text_secondary'])
        
        return VizEngine._save(filename)
    
    @staticmethod
    def sla_rate_chart(data, title, filename):
        """SLA compliance bar chart with threshold line."""
        VizEngine._setup_style()
        fig, ax = plt.subplots(figsize=(10, 6))
        
        priorities = data['Priority'].tolist()
        rates = data['SLA_Rate'].tolist()
        
        # Color based on threshold
        colors = [COLORS['success'] if r >= 95 else COLORS['warning'] if r >= 90 else COLORS['danger'] for r in rates]
        
        bars = ax.bar(priorities, rates, color=colors, width=0.6, 
                     edgecolor='white', linewidth=0.5)
        
        # Threshold line
        ax.axhline(95, color=COLORS['warning'], linestyle='--', linewidth=2, 
                  label='Target (95%)', alpha=0.8)
        
        # Annotate
        for bar, rate in zip(bars, rates):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                   f'{rate:.1f}%', ha='center', va='bottom', fontsize=12, 
                   fontweight='600', color=COLORS['text'])
        
        ax.set_ylim(0, 105)
        ax.set_xlabel('Priority', fontweight='500', color=COLORS['text_secondary'])
        ax.set_ylabel('SLA Compliance (%)', fontweight='500', color=COLORS['text_secondary'])
        ax.set_title(title, fontsize=14, fontweight='600', color=COLORS['text'], pad=15)
        ax.legend(frameon=False, loc='lower right')
        ax.tick_params(colors=COLORS['text_secondary'])
        
        return VizEngine._save(filename)
