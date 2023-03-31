#!/usr/bin/python3

import sys

import doltcli as dolt
import requests


def try_finding_homepage(
    db, enrollment_id, organization_name, doing_business_as_name, city, state, zip_code
):
    hospital_name = doing_business_as_name
    if hospital_name is None or hospital_name.strip() == "":
        hospital_name = organization_name

    google_query = "{} {} {} {}".format(hospital_name, city, state, zip_code)
    print(google_query)

    params = {
        "q": google_query,
        "lum_json": "1",
    }

    proxies = {
        "http": "http://brd-customer-hl_cecd546c-zone-zone_search:d7gv8z8umqte@zproxy.lum-superproxy.io:22225",
        "https": "http://brd-customer-hl_cecd546c-zone-zone_search:d7gv8z8umqte@zproxy.lum-superproxy.io:22225",
    }

    urls = []

    resp = requests.get(
        "https://www.google.com/search", params=params, proxies=proxies, verify=False
    )
    print(resp.url)

    organic = resp.json().get("organic", [])

    if len(organic) == 0:
        return

    first_result = organic[0]

    print(first_result)

    # XXX: maybe check if it looks like the same hospital

    title = first_result.get("title")

    homepage = first_result.get("display_link").split(" ")[0]

    sql = 'UPDATE hospitals SET homepage = "{}" WHERE enrollment_id = "{}"'.format(
        homepage, enrollment_id
    )

    print(sql)

    db.sql(sql, result_format="csv")


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    dolt_db_dir = sys.argv[1]

    db = dolt.Dolt(dolt_db_dir)

    sql = "SELECT enrollment_id, enrollment_state, organization_name, doing_business_as_name, city, state, zip_code FROM hospitals WHERE homepage IS NULL AND standard_charge_file_url IS NULL AND standard_charge_file_indirect_url IS NULL;"

    res = db.sql(sql, result_format="json")

    for row in res["rows"]:
        enrollment_id = row.get("enrollment_id")
        organization_name = row.get("organization_name")
        doing_business_as_name = row.get("doing_business_as_name")
        city = row.get("city")
        state = row.get("state")
        zip_code = row.get("zip_code")
        
        try:
            try_finding_homepage(
                db,
                enrollment_id,
                organization_name,
                doing_business_as_name,
                city,
                state,
                zip_code,
            )
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
