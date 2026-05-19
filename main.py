#!/usr/bin/env python3
"""CLI entry point for the hiring agent workflow.

Usage:
    python main.py analyze --type candidate --file examples/candidate.md
    python main.py analyze --type project --file examples/project.md
    python main.py analyze --type candidate --text "3年前端经验，React/Vue"
    python main.py analyze --type candidate --file resume.md --output result.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from workflow.graph import run_workflow


def analyze_candidate(text: str, jd_text: str = None, output_file: str = None):
    """Analyze a candidate resume."""
    result = run_workflow(text, input_type="candidate", jd_text=jd_text)
    print_result(result, output_file)
    return result


def analyze_project(text: str, output_file: str = None):
    """Analyze a project document."""
    result = run_workflow(text, input_type="project")
    print_result(result, output_file)
    return result


def print_result(result: dict, output_file: str = None):
    """Print or save the result."""
    output = json.dumps(result, ensure_ascii=False, indent=2)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"[OK] 结果已保存到: {output_file}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(
        description="Hiring Agent Workflow CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze candidate or project")
    analyze_parser.add_argument(
        "--type",
        choices=["candidate", "project"],
        required=True,
        help="Type of input to analyze"
    )
    analyze_parser.add_argument(
        "--file",
        help="Path to input file (resume or project document)"
    )
    analyze_parser.add_argument(
        "--text",
        help="Direct text input (alternative to --file)"
    )
    analyze_parser.add_argument(
        "--jd",
        help="Path to job description file (for candidate analysis)"
    )
    analyze_parser.add_argument(
        "--output",
        help="Path to output JSON file"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        if not args.file and not args.text:
            print("Error: 请提供 --file 或 --text 参数", file=sys.stderr)
            sys.exit(1)

        # Read input
        if args.file:
            input_path = Path(args.file)
            if not input_path.exists():
                print(f"Error: 文件不存在: {args.file}", file=sys.stderr)
                sys.exit(1)
            input_text = input_path.read_text(encoding="utf-8")
        else:
            input_text = args.text

        # Read JD if provided
        jd_text = None
        if args.jd:
            jd_path = Path(args.jd)
            if jd_path.exists():
                jd_text = jd_path.read_text(encoding="utf-8")

        # Run analysis
        if args.type == "candidate":
            analyze_candidate(input_text, jd_text=jd_text, output_file=args.output)
        else:
            analyze_project(input_text, output_file=args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()