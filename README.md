# Ulauncher Pinboard Search

### [Ulauncher](https://ulauncher.io) extension for searching your [Pinboard.in](https://pinboard.in) bookmarks.

![demo](demo.gif)

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

## Requirements

* jq
* simplejson

## Install

> https://github.com/nicolasm/ulauncher-pinboard-search

## Usage

You must fill your Pinboard API token in the extension settings.
