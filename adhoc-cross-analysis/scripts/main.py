"""
Main entry point for Adhoc Cross Analysis.
"""
import os
import sys
import json
import argparse
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Ensure script directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUT_DIR
from utils import get_data_file, ensure_dirs, get_text
from data_loader import DataLoader
from intent_parser import IntentParser
from query_executor import QueryExecutor
from description_generator import DescriptionGenerator


def main():
    parser = argparse.ArgumentParser(description='Adhoc Cross Analysis')
    parser.add_argument(
        '--query',
        type=str,
        help='Analysis query (e.g., "哪个团队 SLA 最差")'
    )
    parser.add_argument(
        '--language',
        type=str,
        choices=['en', 'zh'],
        default='zh',
        help='Output language. Default: zh'
    )
    parser.add_argument(
        '--input',
        type=str,
        default=None,
        help='Path to input Excel file'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--output-json',
        action='store_true',
        help='Output result as JSON'
    )
    args = parser.parse_args()
    lang = args.language

    # Print header
    print("=" * 60)
    if lang == 'zh':
        print("🔍 即席分析工具")
    else:
        print("🔍 Adhoc Analysis Tool")
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

    # Initialize components
    print("\n⏳ Loading and preprocessing data...")
    loader = DataLoader(data_file).load()
    print(f"✅ Data loaded | {loader.aggregated['summary']['total']:,} tickets")

    intent_parser = IntentParser()
    executor = QueryExecutor(loader)
    generator = DescriptionGenerator(language=lang)

    # Interactive mode
    if args.interactive:
        run_interactive(intent_parser, executor, generator, lang)
        return

    # Single query mode
    if not args.query:
        print("\n❌ Error: Please provide --query or use --interactive mode")
        print("\nExamples:")
        print('  python3 main.py --query "哪个团队 SLA 最差"')
        print('  python3 main.py --query "工单量趋势" --language zh')
        print('  python3 main.py --interactive')
        sys.exit(1)

    # Execute query
    result = execute_query(args.query, intent_parser, executor, generator, lang, args.output_json)

    # Save outputs
    save_outputs(args.query, result, lang)


def execute_query(query, intent_parser, executor, generator, lang, output_json=False):
    """Execute a single query."""
    print(f"\n📝 Query: {query}")

    # Parse intent
    print("\n🔍 Parsing intent...")
    intent = intent_parser.parse(query)
    intent_desc = intent_parser.describe_intent(intent, lang)
    print(f"   → {intent_desc}")

    # Execute query
    print("\n⚙️ Executing query...")
    result = executor.execute(intent)
    print(f"   → Found {len(result.get('data', []))} results")

    # Generate description
    print("\n📄 Generating description...")
    description = generator.generate(intent, result)

    # Build full result
    full_result = {
        'query': query,
        'intent': intent,
        'result': result,
        'description': description,
        'timestamp': datetime.now().isoformat(),
    }

    # Print results
    print("\n" + "=" * 60)
    if lang == 'zh':
        print("📊 分析结果")
    else:
        print("📊 Analysis Result")
    print("=" * 60)

    if output_json:
        # Clean up for JSON output
        json_result = {
            'query': query,
            'intent': {k: v for k, v in intent.items() if k != 'raw_query'},
            'data': result.get('data', []),
            'samples': result.get('samples', []),
            'description': description,
        }
        print(json.dumps(json_result, ensure_ascii=False, indent=2))
    else:
        print(f"\n{description}")

    return full_result


def save_outputs(query, result, lang):
    """Save outputs to files."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    lang_suffix = 'CN' if lang == 'zh' else 'EN'

    # Save JSON
    json_path = os.path.join(OUTPUT_DIR, f'Adhoc_Analysis_{timestamp}_{lang_suffix}.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'query': query,
            'intent': {k: v for k, v in result['intent'].items() if k != 'raw_query'},
            'data': result['result'].get('data', []),
            'samples': result['result'].get('samples', []),
            'description': result['description'],
            'timestamp': result['timestamp'],
        }, f, ensure_ascii=False, indent=2)

    # Save HTML
    html_path = os.path.join(OUTPUT_DIR, f'Adhoc_Analysis_{timestamp}_{lang_suffix}.html')
    html_content = generate_html(query, result, lang)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n📁 Output files:")
    print(f"   - {json_path}")
    print(f"   - {html_path}")


def generate_html(query, result, lang):
    """Generate HTML report."""
    title = '即席分析报告' if lang == 'zh' else 'Adhoc Analysis Report'
    description = result['description'].replace('\n', '<br>')

    # Format data table
    data = result['result'].get('data', [])
    table_rows = ''
    if data:
        for item in data:
            table_rows += f"<tr><td>{item.get('name', '')}</td><td>{item.get('value', '')}</td><td>{item.get('count', '')}</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; color: #374151; line-height: 1.6; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 24px; border-radius: 12px; margin-bottom: 20px; }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
        .header .query {{ font-size: 18px; opacity: 0.9; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #1e40af; margin-top: 0; font-size: 18px; }}
        .description {{ white-space: pre-wrap; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ background: #f9fafb; font-weight: 600; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="query">📝 {query}</div>
        </div>
        <div class="card">
            <h2>{'分析结果' if lang == 'zh' else 'Analysis Result'}</h2>
            <div class="description">{description}</div>
        </div>
        {'<div class="card"><h2>' + ('数据表' if lang == 'zh' else 'Data Table') + '</h2><table><thead><tr><th>Name</th><th>Value</th><th>Count</th></tr></thead><tbody>' + table_rows + '</tbody></table></div>' if table_rows else ''}
        <div class="footer">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | Adhoc Analysis
        </div>
    </div>
</body>
</html>"""
    return html


def run_interactive(intent_parser, executor, generator, lang):
    """Run in interactive mode."""
    if lang == 'zh':
        print("\n🎯 交互模式 - 输入问题进行分析，输入 'quit' 退出")
        prompt = "问题> "
    else:
        print("\n🎯 Interactive mode - Enter query to analyze, type 'quit' to exit")
        prompt = "Query> "

    while True:
        try:
            query = input(f"\n{prompt}").strip()
            if not query:
                continue
            if query.lower() in ['quit', 'exit', 'q', '退出']:
                print("\n👋 Bye!")
                break

            execute_query(query, intent_parser, executor, generator, lang)

        except KeyboardInterrupt:
            print("\n\n👋 Bye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
