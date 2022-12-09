#!/usr/bin/python3

import subprocess
import sys
from urllib.parse import urlparse, urljoin

import doltcli as dolt
from lxml import html
import requests

PROXY_URL = "http://brd-customer-hl_cecd546c-zone-zone_dc_gau-country-us:oeodmyfnaa7r@zproxy.lum-superproxy.io:22225"


def looks_like_pt_url(url):
    look_for = [ "pricing", "price", "chargemaster", "billing", "transparency", "financial", "pay", "charges" ]

    for w in look_for:
        if w in url.lower():
            return True

    return False

def looks_like_cdm_url(url):
    look_for_words  = [ "cdm", "machine", "readable", "standard", "charges", "master", "pricing" ]
    look_for_ext = ["zip", "json", "csv", "xlsx", "xls", "pdf"]

    for w in look_for_words:
        if w in url.lower():
            o = urlparse(url)
            
            for e in look_for_ext:
                if e in o.path.lower():
                    return True

    return False

def scrape_direct_url(indirect_url):
    print("Scraping:", indirect_url)

    # https://splash.readthedocs.io/en/stable/api.html#render-html
    params = {
        "url": indirect_url,
        "timeout": "10",
        "proxy": PROXY_URL,
        "images": "0"
    }

    try:
        resp = requests.get("http://147.182.252.177:8050/render", params=params)
        tree = html.fromstring(resp.text)
    except Exception as e:
        print(e)
        return None

    for link in tree.xpath('//a/@href'):
        url = urljoin(page.url, link)

        if looks_like_cdm_url(url):
            print("Direct URL:", url)
            return url

    return None

def serp_crawl(domain):
    query = 'site:{} "price transparency" OR "standard charges" OR "chargemaster" OR "machine readable"'.format(domain)
    
    params = {
        'q': query,
        'lum_json': '1',
    }

    proxies = {
        "http": "http://brd-customer-hl_cecd546c-zone-zone_search:d7gv8z8umqte@zproxy.lum-superproxy.io:22225",
        "https": "http://brd-customer-hl_cecd546c-zone-zone_search:d7gv8z8umqte@zproxy.lum-superproxy.io:22225"
    }

    urls = []

    resp = requests.get("https://www.google.com/search", params=params, proxies=proxies, verify=False)
    print(resp.url)

    organic = resp.json().get("organic", [])

    for o in organic:
        urls.append(o.get("link"))

    return urls

def do_recon(db, homepage_url):
    if ".gov" in homepage_url or "facebook.com" in homepage_url:
        return

    o = urlparse(homepage_url)
    domain = o.netloc

    for url in serp_crawl(domain):
        if looks_like_pt_url(url):
            indirect_url = url
            direct_url = scrape_direct_url(url)

            if direct_url is None:
                continue

            print(indirect_url, "->", direct_url)
            
            sql = 'UPDATE `hospitals` SET `cdm_url` = "{}", `cdm_indirect_url` = "{}" WHERE `homepage` = "{}" AND `cdm_url` IS NULL;'.format(direct_url, indirect_url, homepage_url)
            print(sql)
            
            try:
                db.sql(sql, result_format="json")
            except:
                pass

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
        
        sql = "SELECT COUNT(*) FROM `hospitals` WHERE `homepage` = \"{}\";".format(homepage_url)
        print(sql)

        try:
            res2 = db.sql(sql, result_format="json")
            k = list(res2["rows"][0].keys())[0]
            n = res2["rows"][0][k]
            if n != 1:
                continue
        except Exception as e:
            print(e)

        print(homepage_url)

        do_recon(db, homepage_url)

    browser.close()


if __name__ == "__main__":
    main()
