#!/usr/bin/python2
import mwclient
import json
import time
from mailthon import mail, postman

class ConfigSpider():
    def __init__(self, config):
        with open(config, 'r') as f:
            self.config = json.load(f)
        address = (self.config["Protocol"],self.config["URL"])
        path = self.config['path']
        self.Site = mwclient.Site(address,path)

    def filter(self, page):
        if page.pagelanguage == self.config['OriginLang']:
            return True
        return False

    def get_translation_page(self,OriginPages):
        TranslationPages = []
        for page in OriginPages:
            title = page.page_title
            TranslationPages.append(self.Site.Pages[title+self.config['suffix']])

    def get_origin_page(self):
        OriginPages = []
        for page in self.Site.Pages:
            if self.filter(page):
                self.OriginPages.append(page)
        return OriginPages


    def compare(self, o_page, t_page):
        if not t_page.exists():
            return True
        o_page.text()
        t_page.text()
        for template in t_page.templates:
            if template.page_title == unicode(self.config['template']):
                t_page.tranlateme = True
                return True
            else:
                t_page.tranlateme = False
            time_from_change = time.mktime(o_page.last_rev_time) - \
                time.mktime(t_page.last_rev_time)
            if (time_from_change > 0):
                t_page.time_from_change = time_from_change
            return True


    def get_status(self, OriginPages, TranslationPages):
        PagesToTranslate = []
        for o_page,t_page in zip(OriginPages,TranslationPages):
            if self.compare(o_page,t_page):
                PagesToTranslate.append(zip(o_page,t_page))
        return PagesToTranslate

    def sort_result(x, y):
        o_page_x,t_page_x = x
        o_page_y,t_page_y = y
        if t_page_x.exists() and t_page_y.exists():
            if t_page_x.tranlateme == True and t_page_y.tranlateme == True:
                return t_page_x.time_from_change - t_page_y.time_from_change
            elif t_page_x.tranlateme == True:
                return 1
            else:
                return -1
        elif t_page_x.exists():
            return 1
        else:
            return -1

    def send_mail(self, PagesToTranslate):
        content = self.format_to_html(PagesToTranslate)
        poster = postman(
            host=self.config['mhost'],
            auth=(self.config['muser'],self.config['mpasswd'])
        )
        result = poster.send(
            content,
            subject=self.config['Subject'],
            sender=self.config['sender'],
            receivers=self.config['receivers']
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

