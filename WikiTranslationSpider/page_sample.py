# coding=utf-8
import mwclient
site = mwclient.Site(('https','wiki.archlinux.org'),'/')
page=site.Pages['Main_page']
print page.pagelanguage
page.text()
print page.edit_time
print page.last_rev_time
page=site.Pages[u'List_of_Applications_(简体中文)']
for i in page.templates():
    print i.page_title
for page in site.Categories["English"]:
    print page.page_title
#for i in site.Pages:
#    print i.pagelanguage
