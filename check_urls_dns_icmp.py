#!/usr/bin/python3

import sys
from urllib.parse import urlparse

import doltcli as dolt
from scapy.all import *

def resolve_dns(domain):
    try:
        pkt = IP(dst="1.1.1.1") / UDP() / DNS(rd=1, qd=DNSQR(qname=domain))
        print(pkt.show())
        ans = sr1(pkt)
    except Exception as e:
        print(e)
        return None
    
    dns_pkt = ans["DNS"]

    ip_addrs = []
    ancount = dns_pkt.ancount

    for i in range(ancount):
        ip_addrs.append(dns_pkt.an[i].rdata)
    
    return ip_addrs


def is_it_reachable(ip):
    pkt = IP(dst=ip) / ICMP()
    print(pkt.show())

    for _ in range(5):
        try:
            pkt = IP(dst=ip) / ICMP()
            ans = sr1(pkt, timeout=1.0)
            if ans is not None:
                return True
        except:
            continue

    return False

def is_webserver_gone(url):
    o = urlparse(url)
    domain = o.netloc

    ip_addrs = resolve_dns(domain)
    if ip_addrs is None or len(ip_addrs) == 0:
        return True
    
    for ip_addr in ip_addrs:
        if is_it_reachable(ip_addr):
            return False

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
            if not is_webserver_gone(url):
                valid_urls.append(url)
        
        if orig_urls != valid_urls:
            orig_urls = "|".join(orig_urls)
            valid_urls = "|".join(valid_urls)
            
            if len(valid_urls) == 0:
                sql = "UPDATE `hospitals` SET `{}` = NULL WHERE `{}` = \"{}\";".format(colname, colname, orig_urls)
            else:
                sql = "UPDATE `hospitals` SET `{}` = \"{}\" WHERE `{}` = \"{}\";".format(colname, valid_urls, colname, orig_urls)

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
