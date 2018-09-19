# -*- coding: utf-8 -*-

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from search import search_json_bookmarks
from search import Bookmark

class PinboardSearchExtension(Extension):

    def __init__(self):
        super(PinboardSearchExtension, self).__init__()
        self.aggregate = False
        self.limit = 10
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

json_bookmark_file = "/home/nicolas/Documents/Pinboard/Pinboard.json"

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        search_value = event.get_argument()

        print(search_value)
        print(json_bookmark_file)

        bookmarks = search_json_bookmarks(search_value, json_bookmark_file)

        hosts = []

        items = []
        if bookmarks:
            for bookmark in bookmarks[:extension.limit]:
                if extension.aggregate:
                    hostname = getHostname(bookmark.url)
                    if (not hosts.__contains__(hostname)):
                        hosts.append(hostname)
                else:
                    items.append(ExtensionResultItem(icon='images/icon.png',
                                                     name=bookmark.description.encode("utf8"),
                                                     description=bookmark.description.encode("utf8"),
                                                     on_enter=HideWindowAction()))

        if extension.aggregate:
            for host in hosts[:30]:
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name=getName(host),
                                                 description=host.encode("utf8"),
                                                 on_enter=HideWindowAction()))

        return RenderResultListAction(items)

class PreferencesEventListener(EventListener):
    def on_event(self,event,extension):
        extension.aggregate = event.preferences['aggregate']
        try:
            n = int(event.preferences['limit'])
        except:
            n = 10
        extension.limit = n

class PreferencesUpdateEventListener(EventListener):
    def on_event(self,event,extension):
        if event.id == 'limit':
            try:
                n = int(event.new_value)
                extension.limit = n
            except:
                pass
        elif event.id == 'aggregate':
            extension.aggregate = event.new_value

def getHostname(str):
    url = str.split('/')
    if len(url) > 2:
        return url[2]
    else:
        return 'Unknown'

def getName(hostname):
    dm = hostname.split('.')
    #   Remove WWW
    if dm[0]=='www':
        i = 1
    else:
        i = 0
    #   Join remaining domains and capitalize
    return ''.join(dm[i:len(dm)-1]).title()


if __name__ == '__main__':
    PinboardSearchExtension().run()
