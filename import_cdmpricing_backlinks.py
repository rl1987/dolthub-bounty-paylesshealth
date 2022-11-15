#!/usr/bin/python3

import csv
import sys

import doltcli as dolt
import requests


def main():
    db = dolt.Dolt(sys.argv[1])

    in_f = open(
        "backlinks/moz-inbound-links-for-cdmpricing_com-2022-11-12_23_02_39_380560Z.csv",
        "r",
    )
    csv_reader = csv.reader(in_f)

    seen_urls = set()

    for row in csv_reader:
        if len(row) != 17:
            continue

        indirect_url = row[0]
        if indirect_url == "URL":
            continue

        direct_url = row[7]
        direct_url = "https://" + direct_url
        indirect_url = "https://" + indirect_url
        if direct_url.endswith("shoppable-services"):
            direct_url = direct_url.replace("shoppable-services", "standard-charges")

        if not direct_url.endswith("/standard-charges"):
            direct_url = direct_url + "/standard-charges"

        if direct_url in seen_urls:
            continue

        try:
            resp = requests.get(indirect_url, timeout=5.0)
            if resp.status_code != 200:
                continue
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            continue

        seen_urls.add(direct_url)

        sql = 'UPDATE `hospitals` SET `chargemaster_indirect_url` = "{}" WHERE `chargemaster_direct_url` = "{}" AND `chargemaster_indirect_url` IS NULL;'.format(
            indirect_url, direct_url
        )
        print(sql)

        db.sql(sql, result_format="csv")

    in_f.close()


if __name__ == "__main__":
    main()
