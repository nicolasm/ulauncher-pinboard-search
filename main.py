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
from search import search_bookmarks, search_bookmarks_by_tags

PT_KEYWORD = 'pt_kw'

PB_KEYWORD = 'pb_kw'

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
            if bookmark.private:
                icon = 'images/lock.png'
            else:
                icon = 'images/bookmark.png'
            bookmark_data = {'type': 'bookmark', 'url': bookmark.url, 'browser': self.browser}
            tag_data = {'type': 'tags', 'tags': bookmark.tags}
            items.append(ExtensionResultItem(icon=icon,
                                             name=bookmark.description.encode('utf8'),
                                             description=bookmark.url,
                                             on_enter=ExtensionCustomAction(bookmark_data),
                                             on_alt_enter=ExtensionCustomAction(tag_data, keep_app_open=True)))

        next_data = {'type': 'bookmarks', 'start': start_index + self.limit}
        if start_index + self.limit < bookmarks.__len__():
            items.append(ExtensionResultItem(icon='images/next.png',
                                             name='Next bookmarks',
                                             on_enter=ExtensionCustomAction(next_data, keep_app_open=True)))
        return items

    def build_tag_items(self, tags, user_keyword):
        items = []
        for tag in tags:
            data = {'type': 'pinboard', 'tags': [tag], 'browser': self.browser}
            items.append(ExtensionResultItem(icon='images/tag.png',
                                             name=tag.encode('utf8'),
                                             on_enter=SetUserQueryAction('%s %s' % (user_keyword, tag)),
                                             on_alt_enter=ExtensionCustomAction(data)))
        if items:
            data = {'type': 'pinboard', 'tags': tags, 'browser': self.browser}
            items.append(ExtensionResultItem(icon='images/tag.png',
                                             name='#all',
                                             on_enter=SetUserQueryAction('%s %s' % (user_keyword, '/'.join(tags))),
                                             on_alt_enter=ExtensionCustomAction(data)))
        return items


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        search_value = event.get_argument()
        if search_value is None:
            search_value = ''

        keyword_id = get_keyword_id(event, extension.preferences)

        items = []

        if keyword_id == PB_KEYWORD:
            bookmarks = search_bookmarks(search_value, extension.json_bookmark_file)

            if bookmarks:
                extension.bookmarks = bookmarks
                items = extension.build_bookmark_items(bookmarks, 0)
        elif keyword_id == PT_KEYWORD:
            bookmarks = search_bookmarks_by_tags(search_value, extension.json_bookmark_file)

            if bookmarks:
                extension.bookmarks = bookmarks
                items = extension.build_bookmark_items(bookmarks, 0)

        return RenderResultListAction(items)


def get_keyword_id(event, preferences):
    keyword = event.get_keyword()
    for key in preferences.keys():
        if preferences[key] == keyword:
            return key


class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):
        data = event.get_data()
        user_keyword = extension.preferences[PT_KEYWORD]

        if data['type'] == 'bookmark':
            extension.bookmarks = []

            ItemEnterEventListener.open_url_in_browser(data, data['url'])
        elif data['type'] == 'bookmarks':
            start_index = data['start']
            items = extension.build_bookmark_items(extension.bookmarks, start_index)
            return RenderResultListAction(items)
        elif data['type'] == 'tags':
            extension.bookmarks = []

            tags = data['tags']
            items = extension.build_tag_items(tags, user_keyword)
            return RenderResultListAction(items)
        elif data['type'] == 'pinboard':
            extension.bookmarks = []
            tags = data['tags']

            url = PINBOARD_URL % (extension.username, '/t:' + '/t:'.join(tags))

            ItemEnterEventListener.open_url_in_browser(data, url)

    @staticmethod
    def open_url_in_browser(data, url):
        if data['browser'] == 'default':
            webbrowser.open_new_tab(url)
        else:
            webbrowser.get(data['browser']).open_new_tab(url)


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
