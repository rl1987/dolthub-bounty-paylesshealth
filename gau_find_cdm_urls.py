#!/usr/bin/python3

import subprocess
import sys
from urllib.parse import urlparse, urljoin

import doltcli as dolt
import requests
from lxml import html

PROXY_URL = "http://brd-customer-hl_cecd546c-zone-zone_residential_test-country-us:kncs4g88b3ca@zproxy.lum-superproxy.io:22225"

def looks_like_pt_url(url):
    look_for = [ "pricing", "price", "chargemaster", "billing", "transparency", "financial", "pay" ]

    for w in look_for:
        if w in url.lower():
            return True

    return False

def looks_like_cdm_url(url):
    look_for_words  = [ "cdm", "machine", "readable", "standard", "charges" ]
    look_for_ext = ["zip", "json", "csv", "xlsx", "xls", "pdf"]

    for w in look_for_words:
        if w in url.lower():
            o = urlparse(url)
            
            for e in look_for_ext:
                if e in o.path.lower():
                    return True

    return False

def scrape_direct_url(indirect_url):
    proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL
    }

    try:
        resp = requests.get(indirect_url, proxies=proxies, timeout=5.0)
        print(resp.url)
    except:
        return
    
    if resp.status_code != 200:
        return

    try:
        tree = html.fromstring(resp.text)
    except:
        return

    for link in tree.xpath('//a/@href'):
        url = urljoin(resp.url, indirect_url)

        if looks_like_cdm_url(url):
            return url

def do_recon(db, homepage_url):
    print("Checking:", homepage_url)
    p = subprocess.run(["gau", "--mt", "text/html", "--threads", "8", "--providers", "wayback", homepage_url], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    print("!")

    for line in p.stdout.decode('utf-8').split('\n'):
        print(line)
        if not line or line == '':
            continue

        url = line

        if looks_like_pt_url(url):
            indirect_url = url
            direct_url = scrape_direct_url(url)

            if direct_url is None:
                continue

            print(indirect_url, "->", direct_url)
            
            sql = 'UPDATE `hospitals` SET `cdm_url` = "{}", `cdm_indirect_url` = "{}" WHERE `homepage` = "{}" AND `cdm_url` IS NULL;'.format(direct_url, indirect_url, homepage_url)
            print(sql)

            db.sql(sql)

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    dolt_db_dir = sys.argv[1]

    db = dolt.Dolt(dolt_db_dir)

    sql = "SELECT `ccn`, `name`, `homepage` FROM `hospitals` WHERE `cdm_url` IS NULL AND `homepage` IS NOT NULL;"
    print(sql)

    res = db.sql(sql, result_format="json")

    for row in res["rows"]:
        homepage_url = row["homepage"]

        do_recon(db, homepage_url)

if __name__ == "__main__":
    main()
