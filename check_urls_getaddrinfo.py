#!/usr/bin/python3

import sys
import socket
from urllib.parse import urlparse

import doltcli as dolt


def domain_not_resolving(ns, domain):
    try:
        t = socket.getaddrinfo(domain, 80, proto=socket.IPPROTO_TCP)
        print(domain, t)
        return False
    except Exception as e:
        return True


def check_urls_in_col(db, colname):
    sql = "SELECT DISTINCT(`{}`) FROM `hospitals`;".format(colname)
    print(sql)

    try:
        res = db.sql(sql, result_format="json")
    except:
        try:
            res = db.sql(sql, result_format="json")
        except:
            return

    for row in res["rows"]:
        try:
            orig_urls = row.get(list(row.keys())[0])
        except:
            print(row)
            continue
        if orig_urls is None:
            continue

        orig_urls = orig_urls.split("|")
        valid_urls = []

        for url in orig_urls:
            o = urlparse(url)
            domain = o.netloc
            if not domain_not_resolving("1.1.1.1", domain):
                valid_urls.append(url)

        if orig_urls != valid_urls:
            orig_urls = "|".join(orig_urls)
            valid_urls = "|".join(valid_urls)

            if len(valid_urls) == 0:
                sql = 'UPDATE `hospitals` SET `{}` = NULL WHERE `{}` = "{}";'.format(
                    colname, colname, orig_urls
                )
            else:
                sql = 'UPDATE `hospitals` SET `{}` = "{}" WHERE `{}` = "{}";'.format(
                    colname, valid_urls, colname, orig_urls
                )

            print(sql)

            try:
                db.sql(sql, result_format="json")
            except Exception as e:
                print(e)


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    dolt_db_dir = sys.argv[1]

    db = dolt.Dolt(dolt_db_dir)

    check_urls_in_col(db, "homepage")
    check_urls_in_col(db, "cdm_url")
    check_urls_in_col(db, "cdm_indirect_url")


if __name__ == "__main__":
    main()
