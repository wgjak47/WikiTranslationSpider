import mwclient
site = mwclient.Site(('https','wiki.gentoo.org'),'/')
page=site.Pages['Handbook:Main_Page']
print page.pagelanguage
page=site.Pages['Handbook:Main_Page/zh_cn']
print page.pagelanguage

for i in site.Pages:
    print i.pagelanguage

