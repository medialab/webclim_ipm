#!/bin/bash

LIST=$1
TODAY_DATE=$(date +"%Y-%m-%d")

OUTPUT_NAME="posts_${LIST}.csv"

minet ct posts --list-ids $LIST --start-date 2019-01-01 --end-date 2020-12-31 > \
  "./data/section_2_condor/${OUTPUT_NAME}"

# minet ct posts --list-ids $LIST --start-date 2019-01-01 --end-date 2020-12-31 \
#   --resume --output "./data/section_2_condor/${OUTPUT_NAME}"