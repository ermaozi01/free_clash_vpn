import base64
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

import main

CLASH = 'proxies:\n  - {name: test, type: ss, server: example.com, port: 443}\n'
V2RAY = base64.b64encode(b'vmess://example').decode()


def response(content):
    return Mock(content=content.encode(), raise_for_status=Mock())


class UpdateTests(unittest.TestCase):
    def test_update_and_keep_old_files_on_invalid_download(self):
        feed = {'entries': [{'summary': 'unrelated article'}, {'summary':
            '<span>v2ray订阅链接：https://example.com/v?a=1&amp;b=2</span>'
            '<span>clash订阅链接：https://example.com/c</span>'}]}
        with tempfile.TemporaryDirectory() as directory:
            previous = os.getcwd()
            os.chdir(directory)
            try:
                with patch.object(main.feedparser, 'parse', return_value=feed), patch.object(
                    main.requests, 'get', side_effect=[response('rss'), response(V2RAY), response(CLASH)]
                ) as get:
                    main.get_subscribe_url()
                    self.assertEqual(get.call_args_list[1].args[0], 'https://example.com/v?a=1&b=2')
                    self.assertTrue(all(call.kwargs == {'timeout': 30} for call in get.call_args_list))
                self.assertEqual(Path('subscribe/clash.yml').read_text(), CLASH)
                self.assertEqual(Path('subscribe/v2ray.txt').read_text(), V2RAY)
                with patch.object(main.feedparser, 'parse', return_value=feed), patch.object(
                    main.requests, 'get', side_effect=[response('rss'), response(V2RAY), response('<html>403</html>')]
                ), self.assertRaises(ValueError):
                    main.get_subscribe_url()
                self.assertEqual(Path('subscribe/clash.yml').read_text(), CLASH)
                self.assertEqual(Path('subscribe/v2ray.txt').read_text(), V2RAY)
            finally:
                os.chdir(previous)

    def test_current_source_anchor_links(self):
        parser = main.SubscriptionLinks()
        parser.feed('<a href="https://example.com/c?a=1&amp;b=2"><b>Clash</b> 订阅链接</a>'
                    '<a href="https://example.com/v">V2Ray 订阅链接</a>'
                    '<a href="javascript:alert(1)">V2Ray 订阅链接</a>')
        self.assertEqual(parser.urls, {'clash': 'https://example.com/c?a=1&b=2', 'v2ray': 'https://example.com/v'})

    def test_plain_v2ray_is_saved_as_base64(self):
        self.assertEqual(main.validate_subscription('v2ray', 'vmess://example'), V2RAY)

    def test_reject_empty_or_error_subscriptions(self):
        for kind, content in [('clash', 'proxies: []'), ('v2ray', ''), ('v2ray', base64.b64encode(b'<html>403</html>').decode())]:
            with self.subTest(kind=kind, content=content), self.assertRaises(ValueError):
                main.validate_subscription(kind, content)

    def test_empty_github_history_and_http_failure(self):
        from get_projaec_info import get_project_info
        with patch('get_projaec_info.requests.get', return_value=Mock(json=Mock(return_value=[]))) as get:
            self.assertEqual(get_project_info('u', 'p', 'star', 'stargazers', 'starred_at')['num_list'], [0])
            get.return_value.raise_for_status.assert_called_once()
        with patch('get_projaec_info.requests.get', return_value=Mock(raise_for_status=Mock(side_effect=main.requests.HTTPError))):
            with self.assertRaises(main.requests.HTTPError):
                get_project_info('u', 'p', 'star', 'stargazers', 'starred_at')
