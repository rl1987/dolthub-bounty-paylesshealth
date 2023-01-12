#!/usr/bin/python3

import sys

import doltcli as dolt
import requests


def url_goes_404(url):
    if ".gov/" in url:
        return False

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    }

    try:
        resp = requests.get(
            url,
            headers=headers,
            timeout=5.0,
            allow_redirects=True,
            stream=True,
            verify=False,
        )
        print(resp.url + " " + str(resp.status_code))
        return resp.status_code == 404
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        return False

    return False


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
            if not url_goes_404(url):
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
    
    check_urls_in_col(db, 'homepage')
    check_urls_in_col(db, 'cdm_url')
    check_urls_in_col(db, 'cdm_indirect_url')

if __name__ == "__main__":
    main()
