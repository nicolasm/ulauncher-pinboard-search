#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jq import jq
import simplejson as json
import os.path
import operator


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


def search_json_tags(search_tags, path_to_pinboard_json):
    tags_map = dict()
    sorted_tags = []
    if os.path.isfile(path_to_pinboard_json):
        with open(path_to_pinboard_json) as json_file:
            json_data = json.load(json_file, encoding='us-ascii')
            tags = search_tags.split('/')

            jq_query = __build_jq_query(tags)

            json_search_results = jq(jq_query).transform(json_data, multiple_output=True)

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


def __build_jq_query(tags):
    jq_start = '.[] | select('
    jq_contains = '(.tags | contains("%s"))'
    jq_end = ') | {tags: .tags}'
    jq_query = jq_start
    for index in range(len(tags)):
        jq_query += jq_contains % tags[index]
        if index < len(tags) - 1:
            jq_query += ' and '
    jq_query += jq_end
    return jq_query