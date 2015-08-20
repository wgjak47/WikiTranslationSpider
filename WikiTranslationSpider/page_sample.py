# coding=utf-8
import mwclient
site = mwclient.Site(('https','wiki.gentoo.org'),'/')
page=site.Pages['AMD64/FAQ/zh-cn']
for i in page.templates():
    print i.page_title
print page.pagelanguage
print page.last_rev_time
page.text()
print page.last_rev_time
