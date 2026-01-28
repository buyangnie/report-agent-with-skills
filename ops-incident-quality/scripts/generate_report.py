"""
Main entry point for Incident Quality Report Generation.
"""
import os
import sys
import argparse

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ensure script directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import get_data_file, ensure_dirs, OUTPUT_DIR
from analyzer import ReportAnalyzer
from visualizer import VizEngine
from insight_generator import generate_insights
from report_builder import ReportBuilder
from i18n import get_text, get_report_filename

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate Incident Quality Report')
    parser.add_argument(
        '--language',
        type=str,
        choices=['en', 'zh'],
        default='en',
        help='Report language (en=English, zh=Chinese). Default: en'
    )
    parser.add_argument(
        '--input',
        type=str,
        default=None,
        help='Path to input Excel file. If not specified, uses first .xlsx file in data/ directory'
    )
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear AI insights cache before generating report'
    )
    args = parser.parse_args()
    lang = args.language

    # Handle cache clearing
    if args.clear_cache:
        from insight_generator import clear_cache
        print("🗑️  Clearing insights cache...")
        clear_cache()
        print("✅ Cache cleared")

    # Print header with language support
    print("=" * 60)
    if lang == 'zh':
        print("🚀 事件质量报告生成器")
    else:
        print("🚀 Incident Quality Report Generator")
    print("=" * 60)

    # Setup
    ensure_dirs()

    # Load data
    if args.input:
        if not os.path.exists(args.input):
            print(f"❌ Error: File not found: {args.input}")
            sys.exit(1)
        data_file = args.input
    else:
        data_file = get_data_file()

    print(f"\n📂 Data Source: {data_file}")

    analyzer = ReportAnalyzer(data_file)

    try:
        analyzer.load_data()
        print(f"✅ Data loaded successfully | {len(analyzer.df)} tickets")
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return

    # Run analysis
    print("\n🔍 Running multi-dimensional analysis...")
    results = analyzer.analyze_all()
    print("✅ Analysis complete")

    # Generate charts
    print("\n📊 Generating visualizations...")
    charts = generate_charts(results)
    print(f"✅ Generated {len(charts)} charts")

    # Generate AI insights with language
    print("\n🤖 Generating AI insights...")
    insights = generate_insights(results, language=lang)
    print(f"✅ Generated {len(insights)} dimension insights")

    # Build reports with language
    print("\n📝 Building reports...")
    builder = ReportBuilder(results, charts, insights, language=lang)

    html_path = builder.build_html()
    print(f"  - HTML: {html_path}")

    docx_path = builder.build_docx()
    print(f"  - DOCX: {docx_path}")

    # Print summary
    print("\n" + "=" * 60)
    print(f"✅ {get_text('generation_complete', lang)}")
    print("=" * 60)
    print(f"\n📊 {get_text('executive_summary', lang)}:")
    print(f"  - {get_text('data_period', lang)}: {results['summary']['date_range']}")
    print(f"  - {get_text('total_tickets', lang)}: {results['summary']['total']}")
    print(f"  - {get_text('sla_compliance', lang)}: {results['summary']['sla_rate']:.1f}%")
    print(f"  - {get_text('avg_mttr', lang)}: {results['summary']['avg_mttr']:.1f}h")
    print(f"  - {get_text('p1_incidents', lang)}: {results['summary']['p1_count']}")
    print(f"  - {get_text('p2_incidents', lang)}: {results['summary']['p2_count']}")

    if results['summary']['anomalies']:
        print(f"\n⚠️ {get_text('key_alerts', lang)}:")
        for a in results['summary']['anomalies']:
            print(f"  - {a}")

    if results['recommendations']:
        print(f"\n💡 {get_text('recommendations', lang)} ({len(results['recommendations'])}):")
        for rec in results['recommendations'][:3]:
            priority_icon = '🔴' if rec['priority'] == 'HIGH' else '🟡'
            print(f"  {priority_icon} [{rec['category']}] {rec['text']}")

    print(f"\n📁 {get_text('output_files', lang)}:")
    print(f"  - {html_path}")
    print(f"  - {docx_path}")
    print()


def generate_charts(results):
    """Generate all visualization charts."""
    charts = {}
    
    # SLA Analysis Charts
    sla = results.get('sla', {})
    
    if 'by_priority' in sla and len(sla['by_priority']) > 0:
        charts['sla_rate_chart'] = VizEngine.sla_rate_chart(
            sla['by_priority'], 
            'SLA Compliance by Priority', 
            'sla_rate_chart.png'
        )
    
    if 'violations_by_person' in sla and len(sla['violations_by_person']) > 0:
        charts['sla_violations_by_person'] = VizEngine.bar_chart(
            sla['violations_by_person'].head(10),
            'SLA Violations by Person (Top 10)',
            'sla_violations_by_person.png',
            horizontal=True,
            color='#c0392b'
        )
    
    if 'violations_by_category' in sla and len(sla['violations_by_category']) > 0:
        charts['sla_violations_by_category'] = VizEngine.bar_chart(
            sla['violations_by_category'].head(10),
            'SLA Violations by Category (Top 10)',
            'sla_violations_by_category.png',
            horizontal=True,
            color='#e74c3c'
        )
    
    if 'severity_distribution' in sla and len(sla['severity_distribution']) > 0:
        charts['sla_severity'] = VizEngine.pie_chart(
            sla['severity_distribution'],
            'Violation Severity Distribution',
            'sla_severity.png'
        )
    
    # Priority Analysis Charts
    priority = results.get('priority', {})
    
    if 'distribution' in priority and len(priority['distribution']) > 0:
        charts['priority_dist'] = VizEngine.pie_chart(
            priority['distribution'],
            'Priority Distribution',
            'priority_dist.png',
            colors=['#c0392b', '#e74c3c', '#f39c12', '#27ae60']
        )
    
    if 'mttr_by_priority' in priority and len(priority['mttr_by_priority']) > 0:
        charts['mttr_by_priority'] = VizEngine.grouped_bar(
            priority['mttr_by_priority'],
            'MTTR Comparison by Priority',
            'mttr_by_priority.png',
            xlabel='Priority',
            ylabel='Hours'
        )
    
    # Personnel Analysis Charts
    personnel = results.get('personnel', {})
    
    if 'efficiency' in personnel and len(personnel['efficiency']) > 0:
        charts['personnel_matrix'] = VizEngine.scatter_matrix(
            personnel['efficiency'],
            'Volume', 'Avg_MTTR', 'Resolver',
            'Performance Matrix (Volume vs MTTR)',
            'personnel_matrix.png'
        )
    
    if 'volume_rank' in personnel and len(personnel['volume_rank']) > 0:
        charts['volume_rank'] = VizEngine.bar_chart(
            personnel['volume_rank'].head(10),
            'Volume Ranking (Top 10)',
            'volume_rank.png',
            horizontal=True,
            color='#3498db'
        )
    
    if 'sla_violation_rank' in personnel and len(personnel['sla_violation_rank']) > 0:
        violation_series = personnel['sla_violation_rank'].set_index('Resolver')['SLA_Violations']
        charts['sla_violation_rank'] = VizEngine.bar_chart(
            violation_series.head(10),
            'SLA Violation Ranking (Top 10)',
            'sla_violation_rank.png',
            horizontal=True,
            color='#e74c3c'
        )
    
    # Category Analysis Charts
    category = results.get('category', {})
    
    if 'distribution' in category and len(category['distribution']) > 0:
        charts['category_dist'] = VizEngine.pie_chart(
            category['distribution'].head(8),
            'Category Distribution (Top 8)',
            'category_dist.png'
        )
    
    if 'keywords' in category and len(category['keywords']) > 0:
        charts['keywords'] = VizEngine.keyword_cloud(
            category['keywords'],
            'Keyword Mining (Top 15)',
            'keywords.png'
        )
    
    # Time Analysis Charts
    time_data = results.get('time', {})
    
    if 'heatmap' in time_data and time_data['heatmap'] is not None:
        charts['heatmap'] = VizEngine.heatmap(
            time_data['heatmap'],
            'Incident Heatmap (Day x Hour)',
            'heatmap.png'
        )
    
    if 'monthly_volume' in time_data and len(time_data['monthly_volume']) > 0:
        charts['monthly_trend'] = VizEngine.trend_line(
            time_data['monthly_volume'],
            'Monthly Incident Trend',
            'monthly_trend.png',
            xlabel='Month',
            ylabel='Tickets'
        )
    
    return charts


if __name__ == "__main__":
    main()
