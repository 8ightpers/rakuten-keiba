#!/bin/bash

python getraceid_today.py

cat cal.source.txt | grep '<a href="https://keiba.rakuten.co.jp/race_card/list/RACEID/' | grep `date +"%Y%m%d"` | grep -v 'レース一覧' | grep -v '投票' > cal.source.txt2
sed 's/ //g' cal.source.txt2 > cal.source.txt

python getRaceidList.py


