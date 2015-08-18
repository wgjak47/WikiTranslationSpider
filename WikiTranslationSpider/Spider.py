#!/usr/bin/python2
# coding=utf-8
import mwclient
import json
import time
import markdown2
from gevent import monkey
monkey.patch_all()
import gevent
from mailthon import email, postman

class ConfigSpider():
    def __init__(self, config):
        with open(config, 'r') as f:
            self.config = json.load(f)
        address = (self.config["Protocol"],self.config["URL"])
        path = self.config['path']
        self.Site = mwclient.Site(address,path)

#    def filter(self, page):
#        if page.pagelanguage == self.config['OriginLang'] and \
#                page.redirect is False:
#            return True
#        return False

    def filter(self, page):
        if '(' not in page.page_title and \
                page.redirect is False:
            return True
        return False

    def add_page(self, page, TranslationPages):
        title = page.page_title
        suffix = self.config['suffix']
        TranslationPages.append(self.Site.Pages[u''.join([title,suffix])])
        print u'haha %s' % unicode(page)

    def get_translation_page(self,OriginPages):
        TranslationPages = []
        task = [gevent.spawn(self.add_page,page,TranslationPages)
                for page in OriginPages]
        gevent.joinall(task,timeout=300)
        return TranslationPages

    def get_origin_page(self):
        OriginPages = []
        for page in self.Site.Pages:
            if self.filter(page):
                OriginPages.append(page)
                print unicode(page)
        return OriginPages


    def compare(self, o_page, t_page):
        if not t_page.exists:
            return True
        o_page.text()
        t_page.text()
        for template in t_page.templates():
            if template.page_title == unicode(self.config['template']):
                t_page.translateme = True
                return True
            else:
                t_page.translateme = False
            time_from_change = time.mktime(o_page.last_rev_time) - \
                time.mktime(t_page.last_rev_time)
            if (time_from_change > 0):
                t_page.time_from_change = time_from_change
            return True


    def get_status(self, OriginPages, TranslationPages):
        PagesToTranslate = []
        for o_page,t_page in zip(OriginPages,TranslationPages):
            if self.compare(o_page,t_page):
                PagesToTranslate.append((o_page,t_page))
        return PagesToTranslate

    def sort_result(self, x, y):
        o_page_x,t_page_x = x
        o_page_y,t_page_y = y
        if t_page_x.exists and t_page_y.exists:
            if t_page_x.translateme == True and t_page_y.translateme == True:
                return t_page_x.time_from_change - t_page_y.time_from_change
            elif t_page_x.translateme == True:
                return 1
            else:
                return -1
        elif t_page_x.exists:
            return 1
        else:
            return -1

    def format_to_html(self,PagesToTranslate):
        markdown_content = [u'',u'|原文|翻译|状态|  \n|---|---|---|']
        for o_page,t_page in PagesToTranslate:
            markdown_content.append(
                u'|[%s](%s)|[%s](%s)|' % (
                    o_page.page_title,
                    u''.join([unicode(self.config['base_url']),o_page.page_title]),
                    t_page.page_title,
                    u''.join([unicode(self.config['base_url']),t_page.page_title])
                )
            )
            if not t_page.exists:
                markdown_content.append(u'未翻译|')
            elif t_page.translateme:
                markdown_content.append(u'需要翻译|')
            else:
                markdown_content.append(u'已有%s小时未翻译' %
                    t_page.last_rev_time - o_page.last_rev_time)
            markdown_content.append('  \n')
        markdown_content = ''.join(markdown_content)
        print unicode(markdown_content)
        return markdown2.markdown(markdown_content)

    def send_mail(self, PagesToTranslate):
        print 'start email'
        content = self.format_to_html(PagesToTranslate)
        poster = postman(
            host=self.config['mhost'],
            auth=(self.config['muser'],self.config['mpasswd'])
        )
        result = poster.send(
            email(
                content,
                subject=self.config['Subject'],
                sender=self.config['sender'],
                receivers=self.config['receivers']
            )
        )
        if not result.ok:
            pass

    def main(self):
        OriginPages = self.get_origin_page()
        TranslationPages = self.get_translation_page(OriginPages)
        PagesToTranslate = self.get_status(OriginPages, TranslationPages)
        sorted(PagesToTranslate, self.sort_result)
        self.send_mail(PagesToTranslate)

if __name__ == '__main__':
    Spider = ConfigSpider("config.json");
    Spider.main()

