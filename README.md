# Ulauncher Pinboard Search

### [Ulauncher](https://ulauncher.io) extension for searching your [Pinboard.in](https://pinboard.in) bookmarks.

![demo](demo.gif)

![demo](demo.jpg)

## Description

Search and browse your Pinboard bookmarks and tags.

## Use
> pb

List your most recent bookmarks.

> pb query

Search your bookmarks matching the search query and list them.

A bookmark is listed when at least one of the following elements contains the search query:
* description
* tags
* href
* extended

All bookmarks are downloaded into a local json file. It is refreshed when Ulaunch starts
if the existing file is older than 24 hours.

> pt

List your most used tags.

> pt query

Explore and browse your Pinboard tags.

-----

Each time you press Enter the selected tag is added to the search value.

If your press Alt-Enter, the search url, selected tag included is opened in the browser.

## Requirements

* jq no longer required. Simple filtering is way faster!
* simplejson --> sudo pip2 install simplejson

## Install

> https://github.com/nicolasm/ulauncher-pinboard-search

## Usage

You must fill your Pinboard API token and username in the extension settings.
