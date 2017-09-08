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


def download_gene_list(filepath, verbose=False):
    url = 'http://59.110.46.8:4000/api/v1/open/search/gene?letter=%s&lang=zh'
    if verbose:
        print('Download gene list')
    genes = []
    for i in range(26):
        res = requests.get(url % chr(65 + i))
        js = res.json()
        if js['error']:
            print('Error ' + js['error'])
        else:
            genes.extend(js['data'])
    with open(filepath, 'w') as fh:
        json.dump(genes, fh)


def download_gene(gene_id, outdir, version='37', verbose=False):
    url = 'http://59.110.46.8:4000/api/v1/open/search/detail?id=%s&type=gene&version=%s&userId=&lang=zh' % (gene_id, version)
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


def download_genes(gene_list, outdir, version='37', processes=3, verbose=False):
    if isinstance(gene_list, str):
        with open(gene_list) as fh:
            gene_list = json.load(fh)
    pool = multiprocessing.Pool(processes=processes)
    n = 0
    for d in gene_list:
        did = d['id']
        ver = version if version is not None else d['version']
        pool.apply_async(download_gene, (did, outdir, ver, verbose))
        n += 1
    pool.close()
    pool.join()
    print('Processed %d gene' % n)


def init_arguments(parser):
    """

    :param argparse.ArgumentParser parser:
    :return:
    """
    parser.add_argument('--genelist', help='Gene list file path (default data/genelist.json)', default='data/genelist.json')
    parser.add_argument('--output', help='Output dir (default data/gene)', default='data/gene')
    parser.add_argument('--ver', help='Gene version (default from gene list)')
    parser.add_argument('--processes', help='Number of processes (default 3)', default=3, type=int)
    parser.add_argument('-v', '--verbose', help='Show more information', action='store_true')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    init_arguments(parser)
    args = parser.parse_args()
    download_gene_list(args.genelist, args.verbose)
    download_genes(args.genelist, args.output, args.ver, args.processes, args.verbose)
