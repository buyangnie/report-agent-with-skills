#!/usr/bin/env python3
"""
Major Incident Analysis Report Generator

Usage:
    python generate_report.py <order_number> [--language en|zh] [--data-file path]

Examples:
    python generate_report.py 80000001
    python generate_report.py 80000001 --language zh
    python generate_report.py 80000001 --data-file data/incident_80000001.json
"""
import argparse
import json
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from analyzer import IncidentAnalyzer
from report_builder import generate_html_report, generate_docx_report


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Major Incident Analysis Report"
    )
    parser.add_argument(
        "order_number",
        help="The incident order number to analyze"
    )
    parser.add_argument(
        "--language", "-l",
        choices=["en", "zh"],
        default="en",
        help="Report language (default: en)"
    )
    parser.add_argument(
        "--data-file", "-f",
        type=Path,
        help="Path to incident JSON data file"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=config.OUTPUT_DIR,
        help="Output directory for reports"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM analysis (use rule-based fallback)"
    )
    return parser.parse_args()


def find_data_file(order_number: str, data_dir: Path) -> Path | None:
    """Find data file for the given order number."""
    # Try common naming patterns
    patterns = [
        f"incident_{order_number}.json",
        f"{order_number}.json",
        f"data_{order_number}.json",
    ]

    for pattern in patterns:
        filepath = data_dir / pattern
        if filepath.exists():
            return filepath

    return None


def load_incident_data(filepath: Path) -> dict:
    """Load incident data from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    """Main entry point."""
    args = parse_args()

    print(f"=" * 60)
    print(f"Major Incident Analysis Report Generator")
    print(f"=" * 60)
    print(f"Order Number: {args.order_number}")
    print(f"Language: {args.language}")
    print()

    # Find or use specified data file
    if args.data_file:
        data_file = args.data_file
    else:
        data_file = find_data_file(args.order_number, config.DATA_DIR)

    if not data_file or not data_file.exists():
        print(f"ERROR: Data file not found for incident {args.order_number}")
        print(f"Please provide a JSON file with the incident data.")
        print(f"Expected location: {config.DATA_DIR}/incident_{args.order_number}.json")
        print()
        print("You can also specify a data file with --data-file option.")
        return 1

    print(f"Data file: {data_file}")
    print()

    # Load data
    try:
        data = load_incident_data(data_file)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in data file: {e}")
        return 1
    except Exception as e:
        print(f"ERROR: Failed to load data file: {e}")
        return 1

    # Validate data structure
    if "incident" not in data:
        print("ERROR: Data file must contain 'incident' object")
        return 1
    if "timeline" not in data:
        print("ERROR: Data file must contain 'timeline' array")
        return 1

    # Run analysis
    print("Running analysis...")
    try:
        analyzer = IncidentAnalyzer.from_json(data)
        analysis = analyzer.analyze(language=args.language, use_llm=not args.no_llm)
    except Exception as e:
        print(f"ERROR: Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print(f"  - Response time: {analysis.response_time_minutes} minutes")
    print(f"  - Resolution time: {analysis.resolution_time_minutes} minutes")
    print(f"  - Escalations: {analysis.escalation_count}")
    print(f"  - Reassignments: {analysis.reassignment_count}")
    print(f"  - Issues detected: {len(analysis.issues)}")
    print()

    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Generate reports
    print("Generating reports...")

    # HTML report
    html_path = generate_html_report(analysis, args.output_dir, args.language)
    print(f"  - HTML: {html_path}")

    # DOCX report (if implemented)
    docx_path = generate_docx_report(analysis, args.output_dir, args.language)
    if docx_path:
        print(f"  - DOCX: {docx_path}")

    print()
    print("Done!")
    print(f"=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
