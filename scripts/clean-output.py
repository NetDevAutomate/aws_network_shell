#!/usr/bin/env python3
"""Clean terminal output for git commit messages or documentation.

Usage:
    # From clipboard (macOS)
    pbpaste | python scripts/clean-output.py

    # From file
    python scripts/clean-output.py < output.txt

    # Copy to clipboard (macOS)
    pbpaste | python scripts/clean-output.py | pbcopy

    # With compact mode (removes empty lines)
    pbpaste | python scripts/clean-output.py --compact
"""

import sys
import re
import argparse


def clean_output(text: str, compact: bool = False) -> str:
    """Clean terminal output for documentation.

    Args:
        text: Raw terminal output with ANSI codes and box drawing
        compact: Remove all blank lines if True

    Returns:
        Cleaned text suitable for markdown code blocks
    """
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        # Remove ANSI escape sequences (colors, cursor movements)
        line = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", line)

        # Replace box drawing characters with simple ASCII
        box_chars = {
            "┏": "+",
            "┓": "+",
            "┗": "+",
            "┛": "+",
            "┣": "+",
            "┫": "+",
            "┳": "+",
            "┻": "+",
            "╋": "+",
            "├": "+",
            "┤": "+",
            "┬": "+",
            "┴": "+",
            "┃": "|",
            "│": "|",
            "━": "-",
            "─": "-",
            "┡": "+",
            "┩": "+",
            "╭": "+",
            "╮": "+",
            "╰": "+",
            "╯": "+",
            "┼": "+",
        }
        for char, replacement in box_chars.items():
            line = line.replace(char, replacement)

        # Normalize multiple spaces (but preserve indentation)
        line = re.sub(r"(?<=\S)  +", " ", line)

        # Remove trailing whitespace
        line = line.rstrip()

        cleaned.append(line)

    # Join lines
    result = "\n".join(cleaned)

    if compact:
        # Remove multiple consecutive blank lines, keep max 1
        result = re.sub(r"\n\n\n+", "\n\n", result)
        # Remove leading/trailing blank lines
        result = result.strip()
    else:
        # Just remove excessive blank lines (keep max 2)
        result = re.sub(r"\n\n\n+", "\n\n", result)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Clean terminal output for git commit messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (from stdin)
  pbpaste | python scripts/clean-output.py

  # Compact mode (remove blank lines)
  pbpaste | python scripts/clean-output.py --compact

  # Copy result to clipboard
  pbpaste | python scripts/clean-output.py | pbcopy

  # From file
  python scripts/clean-output.py < terminal-output.txt > cleaned.txt
        """,
    )
    parser.add_argument(
        "--compact",
        "-c",
        action="store_true",
        help="Remove all blank lines for compact output",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input file (default: stdin)",
    )

    args = parser.parse_args()

    # Read input
    text = args.input_file.read()

    # Clean and print
    cleaned = clean_output(text, compact=args.compact)
    print(cleaned)


if __name__ == "__main__":
    main()
