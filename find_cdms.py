#!/usr/bin/python3

import csv
from urllib.parse import urlparse
import sys

import doltcli as dolt
import requests

FIELDNAMES = ["homepage_url", "chargemaster_direct_url"]


def main():
    proxies = {
        "http": "http://brd-customer-c_cecd546c-zone-zone_search:d7gv8z8umqte@zproxy.lum-superproxy.io:22225",
        "https": "http://brd-customer-c_cecd546c-zone-zone_search:d7gv8z8umqte@zproxy.lum-superproxy.io:22225",
    }

    if len(sys.argv) != 3:
        print("Usage:")
        print("{} <dolt_db_dir> <filetype>".format(sys.argv[0]))
        return

    dolt_db_dir = sys.argv[1]
    filetype = sys.argv[2]

    out_f = open("{}.csv".format(filetype), "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    db = dolt.Dolt(dolt_db_dir)

    seen_domains = set()

    sql = "SELECT `homepage_url` FROM `hospitals` GROUP BY homepage_url HAVING COUNT(`homepage_url`) = 1;"

    res = db.sql(sql, result_format="json")

    for row in res["rows"]:
        print(row)

        o = urlparse(row["homepage_url"])
        domain = o.netloc

        if domain in seen_domains:
            continue

        seen_domains.add(domain)

        google_query = 'site:{} filetype:{} AND ("standard charges" OR "chargemaster" OR CDM)'.format(
            domain, filetype
        )

        params = {
            "q": google_query,
            "lum_json": "1",
            "uule": "w CAIQICINVW5pdGVkIFN0YXRlcw",
        }

        resp = requests.get(
            "https://www.google.com/search",
            params=params,
            verify=False,
            proxies=proxies,
        )
        print(resp.url)

        if resp.status_code != 200:
            print(resp.text)
            continue

        json_dict = resp.json()

        if json_dict.get("organic") is None or len(json_dict.get("organic")) == 0:
            continue

        first_result = json_dict.get("organic")[0]

        cdm_direct_url = first_result.get("link")

        try:
            resp = requests.head(cdm_direct_url, timeout=2)
            print(resp.url)
            if resp.status_code != 200:
                continue
        except:
            continue

        out_row = {
            "homepage_url": row["homepage_url"],
            "chargemaster_direct_url": cdm_direct_url,
        }

        print(out_row)

        csv_writer.writerow(out_row)


if __name__ == "__main__":
    main()
