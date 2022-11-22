#!/usr/bin/python3

import sys

import doltcli as dolt
import requests

def check_ccn(ccn):
    params = {
        "filter[ccn][condition][path]": "Rndrng_Prvdr_CCN",
        "filter[ccn][condition][operator]": "=",
        "filter[ccn][condition][value]": ccn,
        "size": "10",
        "sort": "Rndrng_Prvdr_Org_Name,Rndrng_Prvdr_State_Abrvtn",
        "offset": "0",
        "_table": "lookup",
        "column": "Rndrng_Prvdr_Org_Name,Rndrng_Prvdr_State_Abrvtn,Rndrng_Prvdr_CCN,Rndrng_Prvdr_City,Rndrng_Prvdr_Zip5"
    }

    url = "https://data.cms.gov/data-api/v1/dataset/ad635465-b388-493e-9820-1bc187ef9d46/data-viewer"

    resp = requests.get(url, params=params)
    print(resp.url)

    assert resp.status_code == 200

    found_hospitals = len(resp.json().get("data"))

    return found_hospitals > 0

def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    dolt_db_dir = sys.argv[1]
    db = dolt.Dolt(dolt_db_dir)

    sql = 'SELECT `ccn` FROM `hospitals` WHERE `homepage_url` IS NOT NULL OR `chargemaster_direct_url` IS NOT NULL OR `chargemaster_indirect_url` IS NOT NULL;'
    print(sql)

    res = db.sql(sql, result_format="json")

    for row in res["rows"]:
        print(row)
        ccn = row['ccn']

        if not check_ccn(ccn):
            sql = 'UPDATE `hospitals` SET `homepage_url` = NULL, `chargemaster_direct_url` = NULL, `chargemaster_indirect_url` = NULL WHERE `ccn` = "{}";'.format(ccn)
            print(sql)
            db.sql(sql, result_format="csv")


if __name__ == "__main__":
    main()

