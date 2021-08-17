#!/bin/bash

INPUT_FILE="./data/tpfc-recent-clean.csv"

TODAY_DATE=$(date +"%Y-%m-%d")
OUTPUT_FILE="./data/posts_url_${TODAY_DATE}.csv"

minet ct summary clean_url $INPUT_FILE --posts $OUTPUT_FILE \
 --sort-by total_interactions --start-date 2019-01-01 --platforms facebook