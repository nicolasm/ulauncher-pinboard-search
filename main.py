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
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

json_bookmark_file = "/home/nicolas/Documents/Pinboard/Pinboard.json"

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        search_value = event.get_argument()

        print(search_value)
        print(json_bookmark_file)

        bookmarks = search_json_bookmarks(search_value, json_bookmark_file)

        items = []
        if bookmarks:
            for bookmark in bookmarks[0:10]:
                print(bookmark.description.encode('utf8'),
                      bookmark.url.encode('utf8'))
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name=bookmark.description,
                                                 description=bookmark.url,
                                                 on_enter=HideWindowAction()))

        return RenderResultListAction(items)

if __name__ == '__main__':
    PinboardSearchExtension().run()