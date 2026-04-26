#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: ./shiftjis_convert.sh <file>" >&2
    exit 1
fi

input_file="$1"

if [ ! -f "$input_file" ]; then
    echo "File not found: $input_file" >&2
    exit 1
fi

input_dir="$(dirname "$input_file")"
input_base="$(basename "$input_file")"

if [[ "$input_base" == *.* ]]; then
    output_base="${input_base%.*}_shiftjis.${input_base##*.}"
else
    output_base="${input_base}_shiftjis"
fi

output_file="$input_dir/$output_base"
tmp_output="$(mktemp)"

if ! iconv -f UTF-8 -t CP932//TRANSLIT//IGNORE "$input_file" > "$tmp_output"; then
    echo "Warning: some characters could not be represented in Shift_JIS/CP932 and were omitted or transliterated." >&2
fi

mv "$tmp_output" "$output_file"

echo "$output_file"
