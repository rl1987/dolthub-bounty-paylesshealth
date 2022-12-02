#!/usr/bin/python3

import sys

import doltcli as dolt
import requests

PROXY_URL = "http://brd-customer-hl_cecd546c-zone-zone_residential_test-country-us:kncs4g88b3ca@zproxy.lum-superproxy.io:22225"

def check_url(url):
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

    proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL
    }

    try:
        resp = requests.head(url, headers=headers, timeout=5.0, proxies=proxies)
        print(resp.url + " " + str(resp.status_code))
        return resp.status_code != 404
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        return False

    return False


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    dolt_db_dir = sys.argv[1]

    db = dolt.Dolt(dolt_db_dir)

    sql = "SELECT * FROM `hospitals` WHERE `homepage_url` IS NOT NULL OR `chargemaster_direct_url` IS NOT NULL OR `chargemaster_indirect_url` IS NOT NULL;"
    print(sql)

    res = db.sql(sql, result_format="json")

    bad_homepage_urls = set()
    bad_direct_urls = set()
    bad_indirect_urls = set()

    for row in res["rows"]:
        print(row)

        homepage_url = row.get("homepage_url")
        chargemaster_direct_url = row.get("chargemaster_direct_url")
        chargemaster_indirect_url = row.get("chargemaster_indirect_url")

        if homepage_url is not None:
            if not check_url(homepage_url):
                bad_homepage_urls.add(homepage_url)

        if chargemaster_direct_url is not None:
            if not check_url(chargemaster_direct_url):
                bad_direct_urls.add(chargemaster_direct_url)

        if chargemaster_indirect_url is not None:
            if not check_url(chargemaster_indirect_url):
                bad_indirect_urls.add(chargemaster_indirect_url)

    for url in bad_homepage_urls:
        sql = 'UPDATE `hospitals` SET `homepage_url` = NULL WHERE `homepage_url` = "{}"'.format(
            url
        )
        print(sql)
        try:
            db.sql(sql, result_format="json")
        except Exception as e:
            print(e)

    for url in bad_direct_urls:
        sql = 'UPDATE `hospitals` SET `chargemaster_direct_url` = NULL WHERE `chargemaster_direct_url` = "{}"'.format(
            url
        )
        print(sql)
        try:
            db.sql(sql, result_format="json")
        except Exception as e:
            print(e)

    for url in bad_indirect_urls:
        sql = 'UPDATE `hospitals` SET `chargemaster_indirect_url` = NULL WHERE `chargemaster_indirect_url` = "{}"'.format(
            url
        )
        print(sql)
        try:
            db.sql(sql, result_format="json")
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
