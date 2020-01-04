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
