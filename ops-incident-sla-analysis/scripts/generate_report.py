"""
Main entry point for SLA Violation Analysis Report Generation.
"""
import os
import sys
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ensure script directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import get_data_file, ensure_dirs, OUTPUT_DIR
from analyzer import SLAAnalyzer
from visualizer import VizEngine
from report_builder import ReportBuilder
from i18n import get_text


def main():
    parser = argparse.ArgumentParser(description='Generate SLA Violation Analysis Report')
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
        help='Path to input Excel file'
    )
    args = parser.parse_args()
    lang = args.language

    # Print header
    print("=" * 60)
    if lang == 'zh':
        print("🚀 SLA 违约归因分析报告生成器")
    else:
        print("🚀 SLA Violation Analysis Report Generator")
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

    # Initialize analyzer
    analyzer = SLAAnalyzer(data_file)

    try:
        analyzer.load_data()
        print(f"✅ Data loaded successfully | {len(analyzer.df)} tickets")
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return

    # Run analysis
    print("\n🔍 Running SLA violation analysis...")
    results = analyzer.analyze_all()
    print("✅ Analysis complete")

    # Generate charts
    print("\n📊 Generating visualizations...")
    charts = generate_charts(results)
    print(f"✅ Generated {len(charts)} charts")

    # Build reports
    print("\n📝 Building reports...")
    builder = ReportBuilder(results, charts, language=lang)

    html_path = builder.build_html()
    print(f"  - HTML: {html_path}")

    docx_path = builder.build_docx()
    print(f"  - DOCX: {docx_path}")

    # Print summary
    overview = results['overview']
    risk = results['risk']
    violations = results['violations']

    print("\n" + "=" * 60)
    print(f"✅ {get_text('generation_complete', lang)}")
    print("=" * 60)

    print(f"\n📊 {get_text('sla_overview', lang)}:")
    print(f"  - {get_text('data_period', lang)}: {overview['date_range']}")
    print(f"  - {get_text('total_tickets', lang)}: {overview['total']:,}")
    print(f"  - {get_text('resolution_sla', lang)}: {overview['res_rate']:.1f}%")
    print(f"  - {get_text('total_violations', lang)}: {overview['res_violations']}")
    print(f"  - {get_text('high_risk_count', lang)}: {risk['high_risk_count']}")

    # Alerts
    if overview['res_rate'] < 95:
        print(f"\n⚠️ SLA compliance below 95% target!")

    if risk['high_risk_count'] > 10:
        print(f"⚠️ {risk['high_risk_count']} tickets at high risk of SLA breach!")

    # Recommendations
    if results['recommendations']:
        print(f"\n💡 {get_text('recommendations', lang)} ({len(results['recommendations'])}):")
        for rec in results['recommendations'][:3]:
            icon = '🔴' if rec['priority'] == 'HIGH' else '🟡'
            text = rec.get('text_zh' if lang == 'zh' else 'text', rec['text'])
            print(f"  {icon} {text}")

    print(f"\n📁 {get_text('output_files', lang)}:")
    print(f"  - {html_path}")
    print(f"  - {docx_path}")
    print()


def generate_charts(results):
    """Generate all visualization charts."""
    charts = {}

    overview = results.get('overview', {})
    risk = results.get('risk', {})
    violations = results.get('violations', {})
    attribution = results.get('attribution', {})

    # SLA by priority
    if 'by_priority' in overview and len(overview['by_priority']) > 0:
        df = overview['by_priority']
        data = df.set_index('Priority')['Res_Rate']
        charts['sla_by_priority'] = VizEngine.bar_chart(
            data,
            'SLA Compliance Rate by Priority',
            'sla_by_priority.png',
            horizontal=False,
            color='#3b82f6'
        )

    # Risk distribution
    if 'distribution' in risk and risk['distribution']:
        charts['risk_distribution'] = VizEngine.risk_distribution_chart(
            risk['distribution'],
            'Risk Level Distribution',
            'risk_distribution.png'
        )

    # Severity distribution
    if 'severity_distribution' in violations and violations['severity_distribution']:
        charts['severity_distribution'] = VizEngine.pie_chart(
            violations['severity_distribution'],
            'Violation Severity Distribution',
            'severity_distribution.png'
        )

    # Violations by category
    if 'by_category' in violations and len(violations['by_category']) > 0:
        charts['violations_by_category'] = VizEngine.bar_chart(
            violations['by_category'],
            'Violations by Category',
            'violations_by_category.png',
            horizontal=True,
            color='#ef4444'
        )

    # Attribution
    if attribution:
        charts['attribution'] = VizEngine.bar_chart(
            attribution,
            'Violation Attribution',
            'attribution.png',
            horizontal=False,
            color='#8b5cf6'
        )

    return charts


if __name__ == "__main__":
    main()
