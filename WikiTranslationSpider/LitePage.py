#!/usr/bin/python2
# coding=utf-8

# 精简版mwclient的page，试图减少内存占用，然并卵。
# last_rev_time必须要获取page.text才有值Orz，没找到单独的API，
# 所以都要制造大量请求，干脆不从所有的page里找对应的翻译（懒
class LitePage():
     def __init__(self, page, config):
        self.page_title = page.page_title
        self.exists = page.exists
        page.text()
        self.last_rev_time = page.last_rev_time
        self.url = u''.join([
            config['protocol'],
            "://",
            config['URL'],
            config['route'],
            page.normalize_title(page.page_title)
        ])
        self.translateme = False
        if config.get('translateme', None) is not None:
            for template in page.templates():
                if template.page_title == config['translateme']:
                    self.translateme = True

