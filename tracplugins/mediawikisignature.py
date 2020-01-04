# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2020 John de Rooij
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

from datetime import datetime

from trac.core import Component, implements, TracError
from trac.util import get_reporter_id
from trac.util.datefmt import format_datetime, localtz, user_time, parse_date
from trac.wiki.api import IWikiPageManipulator, IWikiSyntaxProvider
from trac.util.html import tag
from trac.wiki.formatter import format_to_oneliner
from trac.wiki.macros import WikiMacroBase

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

            tzinfo = getattr(req, 'tz', None)
            now = datetime.now(tzinfo or localtz)
            today = format_datetime(now, 'iso8601', tzinfo)

            # Replace the tilde signature starting with the longest
            replacetext = replacetext.replace('~~~~~', ''.join(['-- [[Signature(,', today, ')]]']))
            replacetext = replacetext.replace('~~~~', ''.join(['-- [[Signature(', username, ', ', today, ', ', fullname or '', ')]]']))
            replacetext = replacetext.replace('~~~', ''.join(['-- [[Signature(', username, ', , ', fullname or '', ')]]']))

            page.text = prefix + replacetext

        return []

    # IWikiSyntaxProvider methods

    def get_wiki_syntax(self):
        return []

    def get_link_resolvers(self):
        def link_resolver(formatter, ns, target, label):
            username = target
            return tag.a(label, title='Link to user: ' + username, href='https://www.google.com', class_='trac-author-user')

        yield 'user', link_resolver

class SignatureMacro(WikiMacroBase):
    _description = (
    """Expands the passed username, date and full-username to a MediaWiki like signature""")

    def expand_macro(self, formatter, name, content, args):
        if content:
            args = content.split(',')

            username = None
            timestamp = None
            fullusername = None
            if len(args) > 0:
                username = args[0]
                if not username:
                    username = username.strip()
            if len(args) > 1:
                timestamp = args[1]
                if not timestamp:
                    timestamp = timestamp.strip()
            if len(args) > 2:
                # Need to handle the situation that a , is present in the fullname
                fullusername = args[2]
                if not fullusername:
                    fullusername = fullusername.strip()

            if not username or len(username) == 0:
                username = None
            if not timestamp or len(timestamp) == 0:
                timestamp = None
            if not fullusername or len(fullusername) == 0:
                fullusername = None

            if not fullusername:
                fullusername = username

            signature = fullusername
            if username:
                signature = ''.join(['[[user:', username, '|', fullusername or username, ']]'])

            timeline = ''
            if timestamp:
                tzinfo = getattr(formatter.context.req, 'tz', None)
                try:
                    dateobject = parse_date(timestamp)
                    today_user = user_time(formatter.context.req, format_datetime, dateobject, tzinfo=tzinfo)
                    timeline = ''.join(['[[timeline:', timestamp, '|', today_user, ']]'])
                except TracError:
                    pass

            result = ''.join([signature or '', ' ', timeline or '']).strip()
            # Convert Wiki markup to HTML
            return format_to_oneliner(self.env, formatter.context, result)
        else:
            # No content is parsed
            return ''
