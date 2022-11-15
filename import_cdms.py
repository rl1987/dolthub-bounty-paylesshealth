#!/usr/bin/python3

import csv
import sys

import doltcli as dolt


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("{} <dolt_db_dir> <csv_file_path>".format(sys.argv[0]))
        return

    dolt_db_dir = sys.argv[1]
    csv_file_path = sys.argv[2]

    db = dolt.Dolt(dolt_db_dir)

    in_f = open(csv_file_path, "r")
    csv_reader = csv.DictReader(in_f)

    for row in csv_reader:
        homepage_url = row.get("homepage_url")
        chargemaster_direct_url = row.get("chargemaster_direct_url")
        chargemaster_direct_url = chargemaster_direct_url.split("?")[0]

        sql = 'UPDATE `hospitals` SET `chargemaster_direct_url` = "{}" WHERE `homepage_url` = "{}";'.format(
            chargemaster_direct_url, homepage_url
        )
        print(sql)
        db.sql(sql, result_format="csv")


if __name__ == "__main__":
    main()
