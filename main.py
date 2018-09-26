# -*- coding: utf-8 -*-

import webbrowser

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

import os

from pinboard import start_async_pinboard_download
from search import search_json_bookmarks


class PinboardSearchExtension(Extension):

    def __init__(self):
        super(PinboardSearchExtension, self).__init__()
        self.limit = 10
        self.browser = 'default'

        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

    def build_result_items(self, bookmarks, start_index):
        items = []

        prev_data = {'type': 'bookmark', 'start': start_index - self.limit}
        if start_index >= self.limit:
            items.append(ExtensionResultItem(icon='images/prev.png',
                                             name='Previous bookmarks',
                                             on_enter=ExtensionCustomAction(prev_data, keep_app_open=True)))

        for bookmark in bookmarks[start_index:start_index + self.limit]:
            bookmark_data = {'type': 'bookmark', 'url': bookmark.url, 'browser': self.browser}
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name=bookmark.description.encode('utf8'),
                                             description=bookmark.url,
                                             on_enter=ExtensionCustomAction(bookmark_data)))

        next_data = {'type': 'bookmarks', 'start': start_index + self.limit}
        if start_index + self.limit < bookmarks.__len__():
            items.append(ExtensionResultItem(icon='images/next.png',
                                             name='Next bookmarks',
                                             on_enter=ExtensionCustomAction(next_data, keep_app_open=True)))
        return items


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        search_value = event.get_argument()
        if search_value == None:
            search_value = ''

        bookmarks = search_json_bookmarks(search_value, extension.json_bookmark_file)

        items = []

        if bookmarks:
            extension.bookmarks = bookmarks
            items = extension.build_result_items(bookmarks, 0)

        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()

        if data['type'] == 'bookmark':
            extension.bookmarks = []
            if data['browser'] == 'default':
                webbrowser.open_new_tab(data['url'])
            else:
                webbrowser.get(data['browser']).open_new_tab(data['url'])
        elif data['type'] == 'bookmarks':
            start_index = data['start']
            items = extension.build_result_items(extension.bookmarks, start_index)
            return RenderResultListAction(items)


class PreferencesEventListener(EventListener):

    def on_event(self,event,extension):
        try:
            n = int(event.preferences['limit'])
        except:
            n = 10

        json_bookmark_file = event.preferences['pinboard_bookmark_file']
        pinboard_api_token = event.preferences['pinboard_api_token']
        browser = event.preferences['browser']

        extension.limit = n
        extension.json_bookmark_file = json_bookmark_file
        extension.pinboard_api_token = pinboard_api_token
        extension.browser = browser

        start_async_pinboard_download(extension.pinboard_api_token, extension.json_bookmark_file)


class PreferencesUpdateEventListener(EventListener):

    def on_event(self,event,extension):
        if event.id == 'limit':
            try:
                n = int(event.new_value)
                extension.limit = n
            except:
                pass
        elif event.id == 'pinboard_bookmark_file':
            extension.json_bookmark_file = event.new_value
            start_async_pinboard_download(extension.pinboard_api_token, extension.json_bookmark_file)
        elif event.id == 'pinboard_api_token':
            extension.pinboard_api_token = event.new_value

            if os.path.isfile(extension.json_bookmark_file):
                os.remove(extension.json_bookmark_file)

            start_async_pinboard_download(extension.pinboard_api_token, extension.json_bookmark_file)
        elif event.id == 'browser':
            extension.browser = event.new_value


if __name__ == '__main__':
    PinboardSearchExtension().run()
