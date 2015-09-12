# coding=utf-8
import mwclient
site = mwclient.Site(('https','wiki.archlinux.org'),'/')
page=site.Pages[u"Main_page_(简体中文)"]
for i in page.templates():
    print i.page_title
print page.pagelanguage
print page.touched
revs = page.revisions(prop='timestamp', limit=1, section=None, expandtemplates=None)
rev = revs.next()
print rev['timestamp']
page.text()
print page.last_rev_time
