#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jq import jq
import simplejson as json
import os.path


def search_json_bookmarks(search_value, path_to_pinboard_json):
    bookmarks = []
    if os.path.isfile(path_to_pinboard_json):
        with open(path_to_pinboard_json) as json_file:
            json_data = json.load(json_file, encoding='us-ascii')

            json_search_results = jq('.[] | select((.description | contains("' + search_value + '")) '
            + 'or (.tags | contains("' + search_value + '")) '
            + 'or (.href | contains("' + search_value + '")) '
            + 'or (.extended | contains("' + search_value + '"))) '
            + '| {description: .description, href: .href}').transform(json_data, multiple_output=True)

            for bookmark in json_search_results:
                bookmarks.append(Bookmark(description=bookmark['description'], url=bookmark['href']))

    return bookmarks


class Bookmark:
    def __init__(self, description, url):
        self.description = description
        self.url = url
