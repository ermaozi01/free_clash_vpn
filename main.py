import base64
import binascii
import html
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import time

import feedparser
import requests
import yaml

RSS_URL = 'https://www.cfmem.com/feeds/posts/default?alt=rss'
SUBSCRIPTIONS = {'v2ray': 'v2ray.txt', 'clash': 'clash.yml'}


class SubscriptionLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.url = ''
        self.label = ''
        self.urls = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.url = dict(attrs).get('href', '')
            self.label = ''

    def handle_data(self, data):
        self.label += data

    def handle_endtag(self, tag):
        if tag == 'a':
            for kind in SUBSCRIPTIONS:
                if re.fullmatch(rf'\s*{kind}\s*订阅链接\s*', self.label, re.I) and self.url.startswith(('https://', 'http://')):
                    self.urls.setdefault(kind, self.url)
            self.url = ''
            self.label = ''


def write_log(content, level='INFO'):
    message = f'[{time.strftime("%Y-%m-%d %H:%M:%S")}] [{level}] {content}\n'
    print(message, end='')
    Path('log').mkdir(exist_ok=True)
    with Path(f'log/{time.strftime("%Y-%m")}-update.log').open('a', encoding='utf-8') as f:
        f.write(message)


def validate_subscription(kind, content):
    if kind == 'clash':
        data = yaml.safe_load(content)
        if not isinstance(data, dict) or not isinstance(data.get('proxies'), list) or not data['proxies']:
            raise ValueError('Clash 配置缺少非空 proxies 列表')
        if not all(isinstance(proxy, dict) and proxy.get('type') and proxy.get('server') for proxy in data['proxies']):
            raise ValueError('Clash 节点缺少 type 或 server')
    else:
        node_pattern = r'^(vmess|vless|trojan|ss|ssr|hysteria2?|hy2|tuic|anytls|mieru)://\S+$'
        if re.match(node_pattern, content.strip().splitlines()[0] if content.strip() else ''):
            content = base64.b64encode(content.strip().encode('utf-8')).decode('ascii')
        compact = ''.join(content.split())
        try:
            decoded = base64.b64decode(compact, validate=True).decode('utf-8')
        except (ValueError, binascii.Error, UnicodeError) as exc:
            raise ValueError('V2Ray 订阅不是有效的 UTF-8 Base64 内容') from exc
        nodes = [node.strip() for node in decoded.splitlines() if node.strip()]
        if not nodes or not all(re.match(node_pattern, node) for node in nodes):
            raise ValueError('V2Ray 订阅缺少有效节点链接')
    return content


def get_subscribe_url():
    response = requests.get(RSS_URL, timeout=30)
    response.raise_for_status()
    entries = feedparser.parse(response.content).get('entries', [])
    urls = {}
    for entry in entries:
        summary = entry.get('summary', '')
        links = SubscriptionLinks()
        links.feed(summary)
        for kind, url in links.urls.items():
            urls.setdefault(kind, url)
        text = html.unescape(re.sub(r'<[^>]+>', ' ', summary))
        for kind in SUBSCRIPTIONS:
            match = re.search(rf'{kind}\s*订阅链接\s*[:：]\s*(https?://[^\s<>"\'\u4e00-\u9fff]+)', text, re.I)
            if match and kind not in urls:
                urls[kind] = match.group(1)
        if len(urls) == len(SUBSCRIPTIONS):
            break
    if len(urls) != len(SUBSCRIPTIONS):
        raise ValueError('RSS 未提供完整的 Clash 和 V2Ray 订阅链接，保留旧订阅')

    # 两种订阅均下载并校验通过后才写入，防止错误页覆盖旧文件。
    downloads = {}
    for kind, url in urls.items():
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        content = response.content.decode('utf-8-sig')
        downloads[kind] = validate_subscription(kind, content)
    Path('subscribe').mkdir(exist_ok=True)
    changed = []
    for kind, content in downloads.items():
        target = Path('subscribe') / SUBSCRIPTIONS[kind]
        if not target.exists() or target.read_text(encoding='utf-8') != content:
            temporary = target.with_suffix(target.suffix + '.tmp')
            temporary.write_text(content, encoding='utf-8')
            temporary.replace(target)
            changed.append(kind)
    write_log('更新成功：' + ', '.join(changed) if changed else '订阅内容未变化')


if __name__ == '__main__':
    try:
        get_subscribe_url()
    except (requests.RequestException, ValueError, yaml.YAMLError, OSError) as exc:
        # 不在日志输出完整订阅地址，地址可能带有访问令牌。
        write_log(f'采集失败（{type(exc).__name__}），请检查源站状态和订阅格式', 'ERROR')
        sys.exit(1)
