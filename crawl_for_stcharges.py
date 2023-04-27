#!/usr/bin/python3

import csv
from urllib.parse import urlparse, urljoin
import subprocess
import sys
import io

import doltcli as dolt


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    dolt_db_dir = sys.argv[1]

    db = dolt.Dolt(dolt_db_dir)

    out_f = open("stdcharges.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(
        out_f,
        fieldnames=[
            "homepage",
            "standard_charge_file_indirect_url",
            "standard_charge_file_url",
        ],
        lineterminator="\n",
    )
    csv_writer.writeheader()

    sql = "SELECT DISTINCT(homepage) FROM hospitals WHERE homepage IS NOT NULL AND standard_charge_file_url IS NULL;"

    res = db.sql(sql, result_format="json")

    for row in res["rows"]:
        homepage = row.get("homepage)")
        print(homepage)
        proc = subprocess.Popen(
            ["hakrawler", "-subs", "-u", "-w"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )

        # https://stackoverflow.com/questions/163542/how-do-i-pass-a-string-into-subprocess-popen-using-the-stdin-argument
        stdout = proc.communicate(input=(homepage + "\n").encode("utf-8"))[0]

        for line in stdout.decode("utf-8").split("\n"):
            if not line.startswith("["):
                continue

            line = line.strip()

            line = line[1:]

            components = line.split("] ")

            if len(components) < 2:
                continue

            url1 = components[0]
            url2 = components[1]

            if "standard" in url2 and "charges" in url2:
                row = {
                    "homepage": homepage,
                    "standard_charge_file_indirect_url": url1,
                    "standard_charge_file_url": url2,
                }

                print(row)
                csv_writer.writerow(row)

    out_f.close()


if __name__ == "__main__":
    main()
