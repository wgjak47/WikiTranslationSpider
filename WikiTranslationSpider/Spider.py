#!/usr/bin/python2
import mwclient
import json

class ConfigSpider():
    def __init__(self, config):
        with open(config, 'r') as f:
            self.config = json.load(f)
        address = (self.config["Protocol"],self.config["URL"])
        path = self.config['path']
        self.Site = mwclient.Site(address,path)

    def filter(self, page):
        pass

    def get_translation_page(self,OriginPages):
        pass

    def get_origin_page(self):
        OriginPages = []
        for page in self.Site.Pages:
            if self.filter(page):
                self.OriginPages.append(page)
        return OriginPages

    def get_status(self, OriginPages, TranslationPages):
        pass

    def sort_result(self, PagesToTranslate):
        pass

    def send_mail(self, PagesToTranslate):
        pass

    def main(self):
        OriginPages = self.get_origin_page()
        TranslationPages = self.get_translation_page(OriginPages)
        PagesToTranslate = self.get_status(OriginPages, TranslationPages)
        self.sort_result(PagesToTranslate)
        self.send_mail(PagesToTranslate)

if __name__ == '__main__':
    Spider = ConfigSpider("config.json");
    Spider.main()

