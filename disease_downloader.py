"""
Download disease list from diseasedx
"""

import requests
import json
import os
import time
import multiprocessing
import argparse
import re


def download_disease_list(filepath, verbose=False):
    url = 'http://59.110.46.8:4000/api/v1/open/search/disease?type=all&letter=ALL&lang=zh'
    if verbose:
        print('Download disease list')
    res = requests.get(url)
    with open(filepath, 'w') as fh:
        json.dump(res.json(), fh)


def download_disease(disease_id, outdir, version='37', verbose=False):
    url = 'http://59.110.46.8:4000/api/v1/open/search/detail?id=%s&type=disease&version=%s&userId=&lang=zh' % (disease_id, version)
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    if verbose:
        print('Request for %s' % url)
    start = time.time()
    js = None
    try:
        res = requests.get(url)
        js = res.json()
    except Exception as err:
        print(err)
    if js is None:
        print('Error for %s' % url)
        return
    if js['error']:
        print('Error ' + js['error'])
        return
    try:
        outf = re.sub(r'\W', '_', js['title']) + '.json'
        outf = os.path.join(outdir, outf)
        if os.path.exists(outf):
            print('Exists for %s' % outf)
        with open(outf, 'w', encoding='utf-8') as fh:
            json.dump(js['data'], fh, ensure_ascii=False, indent=2)
        end = time.time()
        if verbose:
            print('Request finished for %s, time %0.2f s' % (js['title'], end - start))
    except Exception as err:
        print(err)


def download_diseases(disease_list, outdir, processes=3, verbose=False):
    if isinstance(disease_list, str):
        with open(disease_list) as fh:
            disease_list = json.load(fh)
    pool = multiprocessing.Pool(processes=processes)
    n = 0
    for d in disease_list['data']:
        did = d['id']
        ver = d['version']
        pool.apply_async(download_disease, (did, outdir, ver, verbose))
        n += 1
    pool.close()
    pool.join()
    print('Processed %d disease' % n)


def init_arguments(parser):
    """

    :param argparse.ArgumentParser parser:
    :return:
    """
    parser.add_argument('--diseaselist', help='Disease list file path (default data/diseaselist.json)', default='data/diseaselist.json')
    parser.add_argument('--output', help='Output dir (default data/disease)', default='data/disease')
    parser.add_argument('--processes', help='Number of processes (default 3)', default=3, type=int)
    parser.add_argument('-v', '--verbose', help='Show more information', action='store_true')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_arguments(parser)
    args = parser.parse_args()
    download_disease_list(args.diseaselist, args.verbose)
    download_diseases(args.diseaselist, args.output, args.processes, args.verbose)
