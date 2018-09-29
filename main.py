# -*- coding: utf-8 -*-

import webbrowser

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

import os

from pinboard import start_async_pinboard_download
from search import search_json_bookmarks, search_json_tags

PINBOARD_URL = 'https://pinboard.in/u:%s%s'


class PinboardSearchExtension(Extension):

    def __init__(self):
        super(PinboardSearchExtension, self).__init__()
        self.limit = 10
        self.browser = 'default'

        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

    def build_bookmark_items(self, bookmarks, start_index):
        items = []

        prev_data = {'type': 'bookmarks', 'start': start_index - self.limit}
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

    def build_tag_items(self, event, search_value, tags):
        items = []

        user_keyword = event.get_keyword()
        for tag in tags[:self.limit]:
            if search_value == '':
                query = tag[0]
            else:
                query = search_value + '/' + tag[0]

            data = {'type': 'tags', 'query': query}
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name=tag[0].encode('utf8'),
                                             description=str(tag[1]),
                                             on_enter=SetUserQueryAction('%s %s' % (user_keyword, query)),
                                             on_alt_enter=ExtensionCustomAction(data)))
        if len(tags) == 0:
            data = {'type': 'tags', 'query': search_value}
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name='Open link'.encode('utf8'),
                                             on_enter=ExtensionCustomAction(data)))
        return items


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        search_value = event.get_argument()
        if search_value == None:
            search_value = ''

        keyword_id = get_keyword_id(event, extension.preferences)

        items = []

        if keyword_id == 'pb_kw':
            bookmarks = search_json_bookmarks(search_value, extension.json_bookmark_file)

            if bookmarks:
                extension.bookmarks = bookmarks
                items = extension.build_bookmark_items(bookmarks, 0)
        elif keyword_id == 'pt_kw':
            tags = search_json_tags(search_value, extension.json_bookmark_file)
            items = extension.build_tag_items(event, search_value, tags)

        return RenderResultListAction(items)


def get_keyword_id(event, preferences):
    keyword = event.get_keyword()
    for key in preferences.keys():
        if preferences[key] == keyword:
            return key

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
            items = extension.build_bookmark_items(extension.bookmarks, start_index)
            return RenderResultListAction(items)
        elif data['type'] == 'tags':
            tags = data['query'].split('/')
            tag_filters = ''
            for tag in tags:
                tag_filters += '/t:%s' % tag

            url = PINBOARD_URL % (extension.username, tag_filters)
            browser = extension.browser
            if browser == 'default':
                webbrowser.open_new_tab(url)
            else:
                webbrowser.get(browser).open_new_tab(url)


class PreferencesEventListener(EventListener):

    def on_event(self,event,extension):
        try:
            n = int(event.preferences['limit'])
        except:
            n = 10

        json_bookmark_file = event.preferences['pinboard_bookmark_file']
        pinboard_api_token = event.preferences['pinboard_api_token']
        username = event.preferences['pinboard_username']
        browser = event.preferences['browser']

        extension.limit = n
        extension.json_bookmark_file = json_bookmark_file
        extension.pinboard_api_token = pinboard_api_token
        extension.username = username
        extension.browser = browser
        extension.preferences = event.preferences

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
        elif event.id == 'pinboard_username':
            extension.username = event.new_value
        elif event.id == 'browser':
            extension.browser = event.new_value


if __name__ == '__main__':
    PinboardSearchExtension().run()
