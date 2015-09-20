#!/usr/bin/python2
# coding=utf-8
from gevent import monkey
monkey.patch_all()

import json
import logging
import time
import smtplib
import argparse
from email.mime.text import MIMEText
from logging import getLogger

import mwclient
import markdown2
import gevent

from LitePage import LitePage

def SpiderLogger(Object):
    logger = getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    fmt = '([%(asctime)s] %(name)s:%(levelname)s: %(message)s)'
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = SpiderLogger()

class ConfigSpider():
    def __init__(self):
        logger.info('Spider start')
        parser = argparse.ArgumentParser(
            description='WikiSpider'
        )
        parser.add_argument(
            'config',
            type=argparse.FileType('r'),
        )
        arg = parser.parse_args()

        self.config = json.loads(arg.config.read())
        address = (self.config["protocol"],self.config["URL"])
        path = self.config['path']
        self.Site = mwclient.Site(address,path)

    # 过滤函数，用于找出源语言页面。通过pagelanguage属性判别
    def filter(self, page):
        if page.pagelanguage == self.config['OriginLang'] and \
                page.redirect is False:
            return True
        return False

    # 添加对应的翻译页面。
    def add_page(self, page, TranslationPages):
        title = page.page_title
        suffix = self.config['suffix']
        translation = self.Site.Pages[u''.join([title,suffix])]
        logger.debug('get %s page' % translation.page_title)
        TranslationPages.append(
            (
                LitePage(page,self.config),
                LitePage(translation,self.config)
            )
        )

    # 获取翻译页面，由于一个一个找比较慢，使用了gevent提高并发，但是
    # 带来了内存问题。800MB Orz
    def get_translation_page(self,OriginPages):
        TranslationPages = []
        task = [gevent.spawn(self.add_page,page,TranslationPages)
                for page in OriginPages]
        gevent.joinall(task, timeout=300)
        logger.debug('get %s translation pages' % len(task))
        return TranslationPages

    # 获取所有页面，通过filter获取。
    def get_origin_page(self):
        OriginPages = []
        for page in self.Site.Pages:
            if self.filter(page):
                OriginPages.append(page)
        logger.info('get %s origin pages' % len(OriginPages))
        return OriginPages

    # 计算翻译时间和源语言更新时间之差
    time_from_change = lambda self, x,y: time.mktime(x) - time.mktime(y)

    # 对比源页面和翻译页面，根据特殊模版，翻译时间和翻译页面是否存在判断。
    def compare(self, o_page, t_page):
        if not t_page.exists:
            return True
        if t_page.translateme is True:
            return True
        if (self.time_from_change(o_page.last_rev_time,
                                  t_page.last_rev_time) > 0):
            return True
        return False

    # 获取需要翻译的页面
    def get_status(self, TranslationPages):
        PagesToTranslate = []
        for o_page,t_page in TranslationPages:
            if self.compare(o_page,t_page):
                PagesToTranslate.append((o_page,t_page))
        logger.info('get %s to translate' % len(PagesToTranslate))
        return PagesToTranslate

    # 对结果进行排序，有特殊模版标记的优先，其次是已翻译但未及时更新，最后是未翻译
    def sort_result(self, x, y):
        o_page_x,t_page_x = x
        o_page_y,t_page_y = y
        if t_page_x.exists and t_page_y.exists:
            if t_page_x.translateme is True and t_page_y.translateme is True:
                x_time = self.time_from_change(
                    o_page_x.last_rev_time,
                    t_page_x.last_rev_time
                )
                y_time = self.time_from_change(
                    o_page_y.last_rev_time,
                    t_page_y.last_rev_time
                )
                return int(x_time - y_time)
            elif t_page_x.translateme == True:
                return -1
            else:
                return 1
        elif t_page_x.exists:
            return -1
        else:
            return 1

    # 将结果先转化为markdown再导出为html
    def format_to_html(self,PagesToTranslate):
        markdown_content = [u'',u'|原文|翻译|状态|\n|---|---|---|\n']
        for o_page,t_page in PagesToTranslate:
            markdown_content.append(
                u'|[%s](%s)|[%s](%s)|' % (
                    o_page.page_title,
                    o_page.url,
                    t_page.page_title,
                    t_page.url
                )
            )
            if not t_page.exists:
                markdown_content.append(u'未翻译|')
            elif t_page.translateme:
                markdown_content.append(u'需要翻译|')
            else:
                markdown_content.append(u'已有%s小时未更新翻译|' %
                    ((time.mktime(o_page.last_rev_time)
                      - time.mktime(t_page.last_rev_time)) // 3600))
            markdown_content.append('\n')
        markdown_content = ''.join(markdown_content)
        return markdown2.markdown(markdown_content, extras=["tables"])

    # 发送邮件
    def send_mail(self, PagesToTranslate):
        content = self.format_to_html(PagesToTranslate)

        host = self.config['mhost']
        port = self.config['mport']
        user = self.config['muser']
        passwd = self.config['mpasswd']
        receivers = self.config['receivers']

        s = smtplib.SMTP_SSL(host, port)
        s.login(user, passwd)
        msg = MIMEText(unicode(content), 'html', 'utf-8')
        msg['subject'] = self.config['subject']
        msg['from'] = user
        msg['to'] = unicode(receivers)
        for receiver in receivers:
            s.sendmail(user, receiver, msg.as_string())
            logger.info('send mail to %s' % receiver);
        s.close()

    def main(self):
        OriginPages = self.get_origin_page()
        TranslationPages = self.get_translation_page(OriginPages)
        PagesToTranslate = self.get_status(TranslationPages)
        PagesToTranslate = sorted(PagesToTranslate, self.sort_result)
        mail = gevent.spawn(self.send_mail,PagesToTranslate)
        mail.join()

def main():
    Spider = ConfigSpider();
    Spider.main()

if __name__ == '__main__':
    main()

