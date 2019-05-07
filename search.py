#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

import simplejson as json


def search_bookmarks(search_value, path_to_pinboard_json):
    bookmarks = []
    if os.path.isfile(path_to_pinboard_json):
        with open(path_to_pinboard_json) as json_file:
            json_data = json.load(json_file, encoding='us-ascii')

            for bookmark in json_data:
                description = bookmark['description']
                tags = bookmark['tags']
                href = bookmark['href']
                extended = bookmark['extended']

                bookmark_tags = tags.lower().split(' ')
                if search_value.lower() in description.lower() \
                        or {search_value.lower()}.issubset(set(bookmark_tags)) \
                        or search_value.lower() in href \
                        or search_value.lower() in extended.lower():
                    bookmarks.append(
                        Bookmark(description=description,
                                 url=href,
                                 private=(bookmark['shared'] == 'no'),
                                 tags=tags.split(' ')))

    return bookmarks


def search_bookmarks_by_tags(search_tags, path_to_pinboard_json):
    bookmarks = []
    if os.path.isfile(path_to_pinboard_json):
        with open(path_to_pinboard_json) as json_file:
            json_data = json.load(json_file, encoding='us-ascii')
            tags = search_tags.split('/')

            for bookmark in json_data:
                bookmark_tags = bookmark['tags'].split(' ')
                if set(tags).issubset(bookmark_tags):
                    bookmarks.append(
                        Bookmark(description=bookmark['description'],
                                 url=bookmark['href'],
                                 private=(bookmark['shared'] == 'no'),
                                 tags=bookmark_tags))
    return bookmarks


class Bookmark:

    def __init__(self, description, url, private, tags):
        self.description = description
        self.url = url
        self.private = private
        self.tags = tags
