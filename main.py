# -*- coding: utf-8 -*-

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from search import search_json_bookmarks
from pinboard import start_async_pinboard_download

class PinboardSearchExtension(Extension):

    def __init__(self):
        super(PinboardSearchExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        search_value = event.get_argument()

        bookmarks = search_json_bookmarks(search_value, extension.json_bookmark_file)

        hosts = []
        items = []
        if bookmarks:
            for bookmark in bookmarks[:extension.limit]:
                if extension.aggregate:
                    hostname = get_hostname(bookmark.url)
                    if (not hosts.__contains__(hostname)):
                        hosts.append(hostname)
                else:
                    items.append(ExtensionResultItem(icon='images/icon.png',
                                                     name=bookmark.description.encode("utf8"),
                                                     description=bookmark.description.encode("utf8"),
                                                     on_enter=HideWindowAction()))

        if extension.aggregate:
            for host in hosts[:extension.limit]:
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name=get_name(host),
                                                 description=host.encode("utf8"),
                                                 on_enter=HideWindowAction()))

        return RenderResultListAction(items)

class PreferencesEventListener(EventListener):
    def on_event(self,event,extension):
        try:
            n = int(event.preferences['limit'])
            aggregate = event.preferences['aggregate']
            json_bookmark_file = event.preferences['pinboard_bookmark_file']
            pinboard_api_token = event.preferences['pinboard_api_token']
        except:
            n = 10
            aggregate = False
            json_bookmark_file = '/tmp/Pinboard.json'
            pinboard_api_token = 'username:token'

        extension.limit = n
        extension.aggregate = (aggregate == "true")
        extension.json_bookmark_file = json_bookmark_file
        extension.pinboard_api_token = pinboard_api_token

        start_async_pinboard_download(extension.pinboard_api_token, extension.json_bookmark_file)

class PreferencesUpdateEventListener(EventListener):
    def on_event(self,event,extension):
        if event.id == 'limit':
            try:
                n = int(event.new_value)
                extension.limit = n
            except:
                pass
        elif event.id == 'aggregate':
            extension.aggregate = (event.new_value == "true")
        elif event.id == 'pinboard_bookmark_file':
            extension.json_bookmark_file = event.new_value
        elif event.id == 'pinboard_api_token':
            extension.pinboard_api_token = event.new_value

def get_hostname(str):
    url = str.split('/')
    if len(url) > 2:
        return url[2]
    else:
        return 'Unknown'

def get_name(hostname):
    dm = hostname.split('.')
    if dm[0]=='www':
        i = 1
    else:
        i = 0
    return ''.join(dm[i:len(dm)-1]).title()


if __name__ == '__main__':
    PinboardSearchExtension().run()
