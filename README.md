# ReportAgent

> An intelligent agentic ITSM operations reporting system.

The agent's core identity can be powered by various LLMs such as **Codex**, **ClaudeCode**, **Goose**, or **OpenCode**.

## Project Structure

This repository is organized into Skills and Agent definitions:

*   **`Agents.md`**: Contains the role definition prompts to initialize the agent.
*   **Skills**: Each of the following directories represents a specific reporting skill:
    *   `customer-cross-overview/`: Cross-process comprehensive dashboard.
    *   `ops-incident-major-analysis/`: Major incident deep-dive analysis.
    *   `ops-incident-quality/`: Incident quality metrics.
    *   `ops-incident-sla-analysis/`: SLA compliance analysis.
    *   `ops-incident-workload/`: Workload distribution analysis.
    *   `adhoc-cross-analysis/`: Ad-hoc cross-domain queries.

## Overview

ReportAgent is a skills-based reporting framework that analyzes ITSM (IT Service Management) data and generates comprehensive reports in HTML, DOCX, and PPTX formats. Each skill focuses on a specific analysis domain and supports bilingual output (English and Chinese).

## Dev Environment Tips

*   Python 3.9+ required
*   Each skill has its own `.env` file for API keys (e.g., Claude API)
*   Install dependencies: `pip install -r requirements.txt` (per skill)
*   Data files are Excel exports from ITSM systems (ServiceNow, etc.)

## Running Reports

```bash
# Navigate to a skill
cd customer-cross-overview/scripts

# Generate reports with AI insights (both EN and ZH)
python3 generate_report.py

# Generate for specific language
python3 generate_report.py --language zh

# Skip AI insights for faster testing
python3 generate_report.py --no-ai
```

## Adding a New Skill

1.  Copy an existing skill directory as template
2.  Update `SKILL.md` with new skill definition
3.  Modify `config.py` for new data sources and thresholds
4.  Update `i18n.py` with all new text labels
5.  Implement custom analysis logic in `*_analyzer.py`
6.  Adjust visualizations in `*_visualizer.py`
7.  Test with sample data before production use