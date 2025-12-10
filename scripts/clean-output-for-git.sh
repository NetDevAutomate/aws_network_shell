#!/usr/bin/env bash
# Clean terminal output for git commit messages
# Usage: pbpaste | ./scripts/clean-output-for-git.sh
#    or: cat output.txt | ./scripts/clean-output-for-git.sh

# Remove ANSI color codes and box drawing characters
sed -E '
  # Remove ANSI escape sequences
  s/\x1B\[[0-9;]*[mK]//g

  # Remove box drawing characters (Unicode)
  s/[┏┓┗┛┃━┣┫┳┻╋├┤┬┴─│╭╮╰╯┼]/|/g
  s/[┡┩]/+/g

  # Clean up multiple spaces (keep indentation)
  s/  +/ /g

  # Remove empty lines (more than 2 consecutive)
  /^[[:space:]]*$/N
  /^\n$/N
  /^\n\n$/d

  # Trim trailing whitespace
  s/[[:space:]]*$//
'
