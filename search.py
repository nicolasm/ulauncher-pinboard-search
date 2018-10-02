#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson as json
import os.path
import operator


def search_json_bookmarks(search_value, path_to_pinboard_json):
    bookmarks = []
    if os.path.isfile(path_to_pinboard_json):
        with open(path_to_pinboard_json) as json_file:
            json_data = json.load(json_file, encoding='us-ascii')

            for item in json_data:
                description = item['description']
                tags = item['tags']
                href = item['href']
                extended = item['extended']

                if search_value.lower() in description.lower() \
                        or search_value.lower() in tags.lower() \
                        or search_value.lower() in href \
                        or search_value.lower() in extended.lower():
                    bookmarks.append(Bookmark(description=description, url=href))

    return bookmarks


class Bookmark:

    def __init__(self, description, url):
        self.description = description
        self.url = url


def search_json_tags(search_tags, path_to_pinboard_json):
    tags_map = dict()
    sorted_tags = []
    if os.path.isfile(path_to_pinboard_json):
        with open(path_to_pinboard_json) as json_file:
            json_data = json.load(json_file, encoding='us-ascii')
            tags = search_tags.split('/')

            json_search_results = []
            for bookmark in json_data:
                if all(tag in bookmark['tags'] for tag in tags):
                    json_search_results.append(bookmark)

            __build_tags_map(json_search_results, tags, tags_map)
            sorted_tags = sorted(tags_map.items(), key=operator.itemgetter(1), reverse = True)

    return sorted_tags


def __build_tags_map(json_search_results, tags, tags_map):
    for bookmark in json_search_results:
        bookmark_tags = bookmark['tags'].split(' ')

        for tag in bookmark_tags:
            if not tags_map.has_key(tag):
                tags_map[tag] = 1
            else:
                tags_map[tag] = tags_map[tag] + 1

    for tag in tags:
        if tags_map.has_key(tag):
            del tags_map[tag]