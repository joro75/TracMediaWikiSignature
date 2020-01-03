# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2020 John de Rooij
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

from datetime import datetime

from trac.core import Component, implements
from trac.util import get_reporter_id
from trac.util.datefmt import format_datetime, localtz, user_time
from trac.wiki.api import IWikiPageManipulator, IWikiSyntaxProvider
from trac.util.html import tag

class MediaWikiSignatureManipulator(Component):
    _description = "Replaces the MediaWiki signature with the author name."

    implements(IWikiPageManipulator, IWikiSyntaxProvider)

    # IWikiPageManipulator

    def prepare_wiki_page(self, req, page, fields):
        pass

    def validate_wiki_page(self, req, page):
        startpos = page.text.find('~~~')
        if startpos >= 0:
            # Only search and replace in the part that we found
            # a 3-tilde signature
            prefix = page.text[:startpos]
            replacetext = page.text[startpos:]

            fullname = req.session.get('name')
            username = get_reporter_id(req)
            signature = ''.join(['[[user:', username, '|', fullname or username, ']]'])

            tzinfo = getattr(req, 'tz', None)
            now = datetime.now(tzinfo or localtz)
            today = format_datetime(now, 'iso8601', tzinfo)
            today_user = user_time(req, format_datetime, now, tzinfo=tzinfo)
            timestamp = ''.join(['[[timeline:', today, '|', today_user, ']]'])

            # Replace the tilde signature starting with the longest
            replacetext = replacetext.replace('~~~~~', '-- ' + timestamp)
            replacetext = replacetext.replace('~~~~', '-- ' + signature + ' ' + timestamp)
            replacetext = replacetext.replace('~~~', '-- ' + signature)

            page.text = prefix + replacetext

        return []

    # IWikiSyntaxProvider methods

    def get_wiki_syntax(self):
        return []

    def get_link_resolvers(self):
        def link_resolver(formatter, ns, target, label):
            username = target
            return tag.a(label, title='Link to user: ' + username, href='https://www.google.com')

        yield 'user', link_resolver
