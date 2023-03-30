#!/usr/bin/python3

import csv

import doltcli as dolt
import requests

def main():
    sql = "SELECT enrollment_id, enrollment_state, organization_name, doing_business_as_name, city, state, zip_code FROM hospitals WHERE homepage IS NULL AND standard_charge_file_url IS NULL AND standard_charge_file_indirect_url IS NULL;"

    # TODO: use BrightData SERP Crawler API to find hospital homepage URL based
    # on organization_name/doing_business_as_name, city, state, zip_code fields and set 
    # the homepage field based on the first search result.

if __name__ == "__main__":
    main()
