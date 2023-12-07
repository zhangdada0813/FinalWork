import requests
import traceback
import cchardet


def downloader(url, timeout=10, headers=None, debug=False, binary=False,params={"p":1}):
    _headers = {
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    }
    redirected_url = url
    if headers:
        _headers = headers
    try:
        # print(kwargs)
        r = requests.get(url, headers=_headers, timeout=timeout,params=params)
        if binary:
            html = r.content
        else:
            encoding = cchardet.detect(r.content)['encoding']
            html = r.content.decode(encoding)
        status = r.status_code
        redirected_url = r.url
    except:
        if debug:
            traceback.print_exc()
        msg = 'failed download: {}'.format(url)
        print(msg)
        if binary:
            html = b''
        else:
            html = ''
        status = 0
    return status, html, redirected_url
