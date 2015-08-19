#!/usr/bin/python2
# coding=utf-8

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
        if config['translateme'] is not None:
            for template in page.templates():
                if template.page_title == config['translateme']:
                    self.translateme = True

