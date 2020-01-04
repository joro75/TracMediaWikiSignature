# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2020 John de Rooij
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

from datetime import datetime
import re

from trac.core import Component, implements, TracError
from trac.util import get_reporter_id
from trac.util.datefmt import format_datetime, localtz, user_time, parse_date, pretty_timedelta
from trac.wiki.api import IWikiPageManipulator, IWikiSyntaxProvider
from trac.util.html import tag
from trac.wiki.formatter import format_to_oneliner
from trac.wiki.macros import WikiMacroBase

class MediaWikiSignatureManipulator(Component):
    _description = "Replaces the MediaWiki signature with the author name."

    implements(IWikiPageManipulator)

    # IWikiPageManipulator

    def prepare_wiki_page(self, req, page, fields):
        pass

    def _count_characters(self, text, character):
        count = 0
        max = len(text)
        while count < max and text[count] == character:
            count += 1 
        return count

    def validate_wiki_page(self, req, page):
        startpos = page.text.find('~~~')
        if startpos >= 0:
            # Only search and replace in the part that we found
            # a 3-tilde signature
            donetext = page.text[:startpos]
            searchtext = page.text[startpos:]

            # Prepare the name and the date that we are probably going to insert
            fullname = req.session.get('name')
            username = get_reporter_id(req)

            tzinfo = getattr(req, 'tz', None)
            now = datetime.now(tzinfo or localtz)
            today = format_datetime(now, 'iso8601', tzinfo)

            signatures = {}
            signatures[3] = ''.join(['-- [[Signature(', username, ', , ', fullname or '', ')]]'])
            signatures[4] = ''.join(['-- [[Signature(', username, ', ', today, ', ', fullname or '', ')]]'])
            signatures[5] = ''.join(['-- [[Signature(,', today, ')]]'])

            # Find and replace all the signatures
            sigstart = searchtext.find('~~~')
            while sigstart >= 0:
                # Determine how many tildes are present here
                count = self._count_characters(searchtext[sigstart:], '~')
                macroCode = signatures.get(count, None) 
                if macroCode:
                    donetext += searchtext[:sigstart]
                    donetext += macroCode
                else:
                    donetext += searchtext[:sigstart + count]                
                searchtext = searchtext[sigstart + count:]
                sigstart = searchtext.find('~~~')
            donetext += searchtext

            page.text = donetext

        return []

class TracLinkUsernameProvider(Component):
    _description = "Provides the user: and full-username: TracLinks."

    implements(IWikiSyntaxProvider)

    # IWikiSyntaxProvider methods

    def get_wiki_syntax(self):
        return []

    def get_link_resolvers(self):
        def username_link_resolver(formatter, ns, target, label):
            username = target
            return tag.a(label, title='Link to user: ' + username, href='https://www.google.com', class_='trac-author-user')
        def fullname_resolver(formatter, ns, target, label):
            fullname = target
            return tag.a(label, class_='trac-author-user')
        return [('user', username_link_resolver), ('full-username', fullname_resolver)]

class SignatureMacro(WikiMacroBase):
    _description = (
    """Expands the passed username, date and full-username to a MediaWiki like signature""")
    
    regexp = "^\s*(?P<username>[^,]*)?\s*(?:,\s*(?P<timestamp>[^,]*)?\s*(?:,\s*(?P<fullname>.*)?)?)?$"
    
    def __init__(self):
        self.contentRegexp = re.compile(self.regexp)

    def expand_macro(self, formatter, name, content, args):
        args = self.contentRegexp.match(content or '')
        if args: 
            username = args.groupdict().get('username')
            timestamp = args.groupdict().get('timestamp')
            fullname = args.groupdict().get('fullname')

            if not fullname or len(fullname) == 0:
                fullname = username

            signature = fullname or ''
            if username and len(username):
                signature = ''.join(['[[user:', username, '|', fullname or username, ']]'])
            elif fullname and len(fullname):
                signature = ''.join(['[[full-username:', fullname, '|', fullname, ']]'])
                
            timeline = ''
            if timestamp and len(timestamp):
                tzinfo = getattr(formatter.context.req, 'tz', None)
                try:
                    dateobject = parse_date(timestamp)
                    now = datetime.now(tzinfo or localtz)
                    pretty_diff = pretty_timedelta(dateobject, now) + ' ago'
                    timeline = ''.join(['[[timeline:', timestamp, '|', pretty_diff, ']]'])
                except TracError:
                    pass

            result = ''.join([signature or '', ' ', timeline or '']).strip()
            # Convert Wiki markup to HTML
            return format_to_oneliner(self.env, formatter.context, result)
        else:
            # No content is parsed
            return ''
