#!/bin/bash

set -x

pushd /root/data/paylesshealth/ || exit

dolt checkout main
dolt remote add upstream onefact/paylesshealth
dolt pull upstream
dolt push

python3 /root/src/check_urls.py /root/data/paylesshealth

branch_name="update_$(date --rfc-3339 date | sed 's/://g' | sed 's/\s/__/g' | sed 's/-/_/g' | cut -f1 -d '+')"

dolt checkout -b "$branch_name"
dolt add .
dolt commit -m "Remove dead URLs"
dolt push -u origin "$branch_name"
dolt checkout main

popd || exit
