#!/usr/bin/env python3
"""
Main entry point for BO Workload Performance Report generation.

Usage:
    python generate_report.py --language en
    python generate_report.py --language zh
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add script directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = SCRIPT_DIR.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from config import DATA_FILE, OUTPUT_DIR
from analyzer import BOWorkloadAnalyzer
from visualizer import Visualizer
from insight_generator import InsightGenerator
from report_builder import ReportBuilder


def print_banner(language: str) -> None:
    """Print startup banner."""
    if language == "zh":
        print("\n" + "=" * 60)
        print("  📊 BO 负载绩效报告生成器")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("  📊 BO Workload Performance Report Generator")
        print("=" * 60)


def print_progress(step: str, language: str) -> None:
    """Print progress message."""
    print(f"  ▶ {step}")


def main():
    """Main entry point."""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Generate BO Workload Performance Report"
    )
    parser.add_argument(
        "--language", "-l",
        choices=["en", "zh"],
        default="en",
        help="Output language (en=English, zh=Chinese)"
    )
    parser.add_argument(
        "--data-file", "-d",
        type=str,
        default=None,
        help="Path to data file (default: data/Incidents-exported.xlsx)"
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AI insight generation"
    )
    
    args = parser.parse_args()
    language = args.language
    
    print_banner(language)
    
    # Determine data file
    data_file = args.data_file if args.data_file else str(DATA_FILE)
    
    if not Path(data_file).exists():
        print(f"\n  ❌ Error: Data file not found: {data_file}")
        sys.exit(1)
    
    print(f"\n  📁 Data file: {data_file}")
    print(f"  🌐 Language: {'Chinese' if language == 'zh' else 'English'}")
    print()
    
    try:
        # Step 1: Load and analyze data
        print_progress("Loading and analyzing data...", language)
        analyzer = BOWorkloadAnalyzer(data_file)
        result = analyzer.analyze()
        
        print(f"    ✓ Loaded {result.total_tickets} tickets")
        print(f"    ✓ Found {result.total_resolvers} resolvers")
        print(f"    ✓ Identified {result.total_bo_resolvers} BO experts (Tier 2+3)")
        print(f"    ✓ Date range: {result.start_date} to {result.end_date}")
        
        # Step 2: Generate charts
        print_progress("Generating charts...", language)
        visualizer = Visualizer(result)
        charts = visualizer.generate_all_charts()
        print(f"    ✓ Generated {len(charts)} charts")
        
        # Step 3: Generate AI insights (if enabled)
        insights = {}
        if not args.no_ai:
            print_progress("Generating AI insights...", language)
            insight_gen = InsightGenerator(language)
            insights = insight_gen.generate_all_insights(result)
            print(f"    ✓ Generated {len(insights)} insights")
        else:
            print_progress("Skipping AI insights (--no-ai)", language)
        
        # Step 4: Build reports
        print_progress("Building reports...", language)
        builder = ReportBuilder(result, charts, insights, language)
        output_paths = builder.save()
        
        print()
        print("  ✅ Reports generated successfully!")
        print()
        print("  📄 Output files:")
        for fmt, path in output_paths.items():
            print(f"    • {fmt.upper()}: {path}")
        
        # Print summary
        print()
        print("  📈 Key Findings:")
        print(f"    • SLA Compliance Rate: {result.global_sla_rate:.1%}")
        print(f"    • Average MTTR: {result.global_avg_mttr:.1f} hours")
        print(f"    • High-Risk Categories: {result.high_risk_count}")
        print(f"    • Bottleneck Experts: {result.bottleneck_count}")
        
        if result.workload_balance:
            print(f"    • Workload Balance (Gini): {result.workload_balance.gini_coefficient:.3f} ({result.workload_balance.interpretation})")
        
        print()
        print("=" * 60)
        
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
