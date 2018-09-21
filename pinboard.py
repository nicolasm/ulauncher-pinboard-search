# -*- coding: utf-8 -*-

import requests
import simplejson as json
import os.path, time
import tempfile
from shutil import copyfile
from threading import Thread

PINBOARD_API_ALL_POSTS_URL = 'https://api.pinboard.in/v1/posts/all?format=json&auth_token=%s'


def start_async_pinboard_download(token, path_to_file):
    thread = Thread(target = download_pinboard_bookmarks_to_file, args= (token, path_to_file))
    thread.start()

def download_pinboard_bookmarks_to_file(token, path_to_file):
    if not os.path.isfile(path_to_file) or is_older_than_one_day(path_to_file):
        r = requests.get(PINBOARD_API_ALL_POSTS_URL % token)

        temp_file = tempfile.NamedTemporaryFile()
        with open(temp_file.name, 'w') as outfile:
            json.dump(r.json(), outfile, sort_keys=True, indent=4, separators=(',', ': '))

        copyfile(temp_file.name, path_to_file)
        temp_file.close()


def is_older_than_one_day(path_to_file):
    return (time.time() - os.path.getmtime(path_to_file) > 24 * 60 * 60)