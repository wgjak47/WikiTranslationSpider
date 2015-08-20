#!/usr/bin/env python
# encoding=utf-8
from Spider import ConfigSpider

class ArchSpider(ConfigSpider):
    # archlinux的所有中文页面的pagelanguage属性全是en，只能用这种方法判断
    def filter(self, page):
        if '(' not in page.page_title and \
                page.redirect is False:
            return True
        return False

if __name__ == '__main__':
    Spider = ArchSpider();
    Spider.main()

