import json
import os
import time

import dns
from bs4 import BeautifulSoup
import sublist3r
import requests


def get_keyword(path):
    with open(path, 'r') as f:
        keywords = f.readlines()
    return [key.split(',') for key in keywords if key.find(',') > 0]


def get_ip(subdomain):
    # 影响效率：直接调用dns查询域名的A记录，如果保证记录的准确，需要设置为一个不常见的dns服务器，访问这种服务器的时间会过长
    try:
        results = dns.resolver.query(subdomain, 'A')
    except:
        return ['无A记录']
    ips = []
    for result in results:
        ips.append(result.to_text())
    return ips


def get_title(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/53.0.2785.143 Safari/537.36 '
    }
    try:
        # 影响效率：1. 无法断定域名采取的是http还是https 2. 无法断定网页编码格式 3.如果网页失效，将会耗费大量连接时间
        test_web = requests.get(url, headers=header, timeout=5)
    except requests.exceptions.RequestException as e:
        return 'none'
    # 此处设置网页编码
    test_web.encoding = 'utf-8'
    # encode = chardet.detect(test_web.content)['encoding']
    soup = BeautifulSoup(test_web.text, 'lxml')
    try:
        title = soup.title.string
    except:
        title = 'none'
    return title


def get_subdomains(infos):
    url = infos[0]
    title = infos[1]
    subdomains_path = './out/subdomains/' + title + '_subdomains.txt'
    k = (os.path.isfile(subdomains_path))
    if not os.path.isfile(subdomains_path):
        subdomains = sublist3r.main(url, 40, 'yahoo_subdomains1.txt', ports=None, silent=False, verbose=True,
                                    enable_bruteforce=False, engines='baidu,netcraft')
        with open('./out/subdomains/' + title + "_subdomains.txt", 'w+', encoding='utf-8') as f:
            f.write(','.join(subdomains))
    with open(subdomains_path, 'r', encoding='utf-8') as f:
        subdomains = f.read().split(',')
    return save_results(subdomains, title)


def save_results(subdomains, title):
    results = {}
    one_sub_results = []
    results[title] = one_sub_results

    for subdomain in subdomains:
        result = {'ip': get_ip(subdomain), 'title': get_title("http://" + subdomain), 'subdomain': subdomain}
        print(result)
        one_sub_results.append(result)

    path_out = "./out/out-" + time.strftime("%Y%m%d%H%M%S", time.localtime()) + "-" + title + ".json"

    with open(path_out, 'w+', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False)
    return results


if __name__ == '__main__':
    all_infos = []
    for key in get_keyword('./Sublist3r/data/xy.txt'):
        print(key)
        per = get_subdomains(key)
        all_infos.append(per)

    with open('./out/all.json', 'w+', encoding='utf-8') as f:
        json.dump(all_infos, f, ensure_ascii=False)
