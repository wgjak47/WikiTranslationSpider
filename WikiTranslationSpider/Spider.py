#!/usr/bin/python2
# coding=utf-8
from gevent import monkey
monkey.patch_all()
import mwclient
import json
import time
import markdown2
import gevent
from LitePage import LitePage
import smtplib
import argparse
from email.mime.text import MIMEText

class ConfigSpider():
    def __init__(self, config):
        self.config = json.loads(config.read())
        address = (self.config["protocol"],self.config["URL"])
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
        translation = self.Site.Pages[u''.join([title,suffix])]
        TranslationPages.append(
            (
                LitePage(page,self.config),
                LitePage(translation,self.config)
            )
        )
        print u'haha %s' % unicode(translation)
        print len(TranslationPages)

    def get_translation_page(self,OriginPages):
        TranslationPages = []
        task = [gevent.spawn(self.add_page,page,TranslationPages)
                for page in OriginPages]
        print len(task)
        gevent.joinall(task, timeout=300)
        return TranslationPages

    def get_origin_page(self):
        OriginPages = []
        for page in self.Site.Pages:
            if self.filter(page):
                OriginPages.append(page)
                print unicode(page)
        return OriginPages

    time_from_change = lambda self, x,y: time.mktime(x) - time.mktime(y)

    def compare(self, o_page, t_page):
        if not t_page.exists:
            return True
        if t_page.translateme is True:
            return True
        if (self.time_from_change(o_page.last_rev_time,
                                  t_page.last_rev_time) > 0):
            return True
        return False


    def get_status(self, TranslationPages):
        PagesToTranslate = []
        for o_page,t_page in TranslationPages:
            if self.compare(o_page,t_page):
                PagesToTranslate.append((o_page,t_page))
        return PagesToTranslate

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
        with open('test.txt','w') as f:
            f.write(markdown_content.encode('utf-8'))
        return markdown2.markdown(markdown_content, extras=["tables"])

    def send_mail(self, PagesToTranslate):
        print 'start email'
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
        s.close()
        print 'mail sended'

    def main(self):
        OriginPages = self.get_origin_page()
        TranslationPages = self.get_translation_page(OriginPages)
        print 'TranslationPages geted'
        PagesToTranslate = self.get_status(TranslationPages)
        PagesToTranslate = sorted(PagesToTranslate, self.sort_result)
        mail = gevent.spawn(self.send_mail,PagesToTranslate)
        mail.join()

def main():
    parser = argparse.ArgumentParser(
        description='WikiSpider'
    )
    parser.add_argument(
        'config',
        type=argparse.FileType('r'),
    )
    arg = parser.parse_args()
    Spider = ConfigSpider(arg.config);
    Spider.main()

if __name__ == '__main__':
    main()

