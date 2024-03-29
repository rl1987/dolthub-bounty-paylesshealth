#!/usr/bin/python3

import csv
from urllib.parse import urlparse
import sys

import doltcli as dolt
import requests

FIELDNAMES = ["name", "ccn", "homepage_url", "chargemaster_indirect_url"]


def main():
    proxies = {
        "http": "http://brd-customer-c_cecd546c-zone-zone_search:d7gv8z8umqte@zproxy.lum-superproxy.io:22225",
        "https": "http://brd-customer-c_cecd546c-zone-zone_search:d7gv8z8umqte@zproxy.lum-superproxy.io:22225",
    }

    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    out_f = open("pricetransp.csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    dolt_db_dir = sys.argv[1]

    db = dolt.Dolt(dolt_db_dir)

    seen_domains = set()

    sql = "SELECT `name`, `ccn`, `homepage_url` FROM `hospitals` WHERE `homepage_url` IS NOT NULL AND `chargemaster_direct_url` IS NULL;"

    res = db.sql(sql, result_format="json")

    for row in res["rows"]:
        print(row)

        o = urlparse(row["homepage_url"])
        domain = o.netloc

        if domain in seen_domains:
            continue

        seen_domains.add(domain)

        google_query = 'site:{} "pricing transparency" OR "chargemaster" OR "standard charges" OR "machine readable files"'.format(
            domain
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

        cdm_indirect_url = first_result.get("link")
        if (
            ".pdf" in cdm_indirect_url
            or ".xlsx" in cdm_indirect_url
            or ".csv" in cdm_indirect_url
        ):
            continue

        out_row = {
            "name": row["name"],
            "ccn": row["ccn"],
            "homepage_url": row["homepage_url"],
            "chargemaster_indirect_url": cdm_indirect_url,
        }

        print(out_row)

        csv_writer.writerow(out_row)


if __name__ == "__main__":
    main()
