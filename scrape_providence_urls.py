#!/usr/bin/python3

import csv
from urllib.parse import urljoin

import requests
from lxml import html

FIELDNAMES = ["name", "cdm_url"]


def main():
    out_f = open("providence.csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=["name", "url"], lineterminator="\n")
    csv_writer.writeheader()

    url = "https://www.providence.org/obp/pricing-transparency"

    proxies = {
        "http": "http://brd-customer-c_cecd546c-zone-zone_unlocker_test2:i2jv2kwowy6r@zproxy.lum-superproxy.io:22225",
        "https": "http://brd-customer-c_cecd546c-zone-zone_unlocker_test2:i2jv2kwowy6r@zproxy.lum-superproxy.io:22225",
    }

    resp = requests.get(url, proxies=proxies, verify=False)
    print(resp.url)
    print(resp)

    tree = html.fromstring(resp.text)

    links = tree.xpath(
        '//a[contains(@href, "StandardCharges") or contains(@href, "standardcharges")]'
    )
    print(links)

    for link in links:
        name = link.text
        url = link.get("href")

        name = name.replace(
            "Machine-readable (JSON) file of standard hospital charges for ", ""
        )
        name = name.replace(
            "Download the machine-readable (JSON) file of standard hospital charges for ",
            "",
        )
        name = name.replace(
            "Download the machine-readable (JSON) files of standard hospital charges for ",
            "",
        )
        name = name.strip()

        url = urljoin(resp.url, url)

        row = {"name": name, "url": url}

        print(row)

        csv_writer.writerow(row)

    out_f.close()


if __name__ == "__main__":
    main()
