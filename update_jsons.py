import json
import re
import time
import urllib.request
import urllib.error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("A")

rdap = {}
whois = {}


def req(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode()


def main():
    logger.info("Fetching root...")
    with urllib.request.urlopen("https://www.iana.org/domains/root/db") as response:
        html = response.read().decode()
        domains = re.findall(r'href="(/domains/root/db/.*?\.html)">', html)

    for d in domains:
        domain = re.findall(r"db\/(.*?\.html)", d)[0].strip("/").split(".")[0]
        logger.info(domain)

        while True:
            time.sleep(1)
            try:
                logger.info("Fetching domain registry...")
                html = req("https://www.iana.org" + d)
                break
            except urllib.error.HTTPError as e:
                logger.error(f"{str(e)} // Retrying...")

        r = re.search(r"RDAP.*?(https://.*?)\n", html)
        if r:
            r = r.group(1)
            if r[-1] != "/":
                r += "/"
            rdap[domain] = r
        logger.info("RDAP: " + r)

        w = re.search(r"WHOIS.*?<\/b>\s(.*?)\s", html)
        if w:
            whois[domain] = w
        logger.info("WHOIS: " + w + "\n")

    with open("rdap.json", "w") as f:
        json.dump(dict(sorted(rdap.items())), f, indent=4)

    with open("whois.json", "w") as f:
        json.dump(dict(sorted(whois.items())), f, indent=4)


main()
