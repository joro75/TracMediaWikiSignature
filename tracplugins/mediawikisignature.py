# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2020 John de Rooij
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

"""Provide the Trac plugin: TracMediaWikiSignature and the supporting
classes.

Classes:
* MediaWikiSignature -- Component that replaces the signature when a
  Wiki page is being saved.
* UserTracLinkProvider -- SyntaxProvider to provide used TracLinks.
* SignatureMacro -- Provide the implementation of the Signature Macro.
"""

from datetime import datetime
import re

from trac.core import Component, implements, TracError
from trac.util import get_reporter_id
from trac.util.text import cleandoc
from trac.util.datefmt import format_datetime, localtz, user_time, \
            parse_date, pretty_timedelta
from trac.wiki.api import IWikiPageManipulator, IWikiSyntaxProvider, \
            WikiSystem
from trac.util.html import tag
from trac.wiki.formatter import format_to_oneliner
from trac.wiki.macros import WikiMacroBase

__all__ = [
            'MediaWikiSignature',
            'UserTracLinkProvider',
            'SignatureMacro'
          ]

class MediaWikiSignature(Component):
    """[required] Provides the functionality that MediaWiki signatures
    (`~~~~`) can be used when editing Wiki pages.

    During the saving of the Wiki page the !MediaWiki signature is
    replaced by the username and/or the timestamp of the edit. 

    Three different variants are possible:
    * The `~~~` will be replaced by the username only
    * The `~~~~` will be replaced by the username and timestamp
    * The `~~~~~` will be replaced by the timestamp only

    With all these variants also a separating `--` prefix will
    automatically be included.  The actual showing of the signature is
    handled by the `[[Signature(...)]]` macro, to be able to show a
    pretty formatted username and timestamp.
    """
    
    _description = cleandoc(__doc__)

    implements(IWikiPageManipulator)

    # IWikiPageManipulator

    def prepare_wiki_page(self, req, page, fields):
        pass

    def _count_characters(self, text, character):
        # Counts and returns how many of the 'characters' are present
        # at the begin of 'text'. 
        count = 0
        max = len(text)
        while count < max and text[count] == character:
            count += 1 
        return count

    def validate_wiki_page(self, req, page):
        """Validate a Wiki page and add warnings when needed."""
        startpos = page.text.find('~~~')
        if startpos >= 0:
            # Only search and replace in the part that we found
            # a 3-tilde signature.
            donetext = page.text[:startpos]
            searchtext = page.text[startpos:]

            # Prepare the name and the date that we are probably 
            # going to insert.
            fullname = req.session.get('name')
            username = get_reporter_id(req)

            tzinfo = getattr(req, 'tz', None)
            now = datetime.now(tzinfo or localtz)
            today = format_datetime(now, 'iso8601', tzinfo)

            signatures = {}
            signatures[3] = ''.join(["-- ", '[[Signature(', username, ', , ',
                            fullname or '', ')]]'])
            signatures[4] = ''.join(["-- ", '[[Signature(', username, ', ',
                            today, ', ', fullname or '', ')]]'])
            signatures[5] = ''.join(["-- ", '[[Signature(,', today, ')]]'])

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


class UserTracLinkProvider(Component):
    """[optional] Provides the `user:` and `full-username:` TracLinks.

    The `user:` !TracLink will show the username in the standard Trac
    formatting style. This !TracLink could in the future be adjusted to
    link to the relevant user specific page of that user.
    
    The `full-username:` !TracLink will show the full name of the user
    in the standard Trac formatting style. Because no username is
    present when this !TracLink is used, no linking to another page or
    URL is possible.

    This part of the !TracMediaWikiSignature plugin can be disabled to
    allow that a more appropriate `user:` !TracLink of another plugin
    can be enabled and used.
    """

    _description = cleandoc(__doc__)

    implements(IWikiSyntaxProvider)

    # IWikiSyntaxProvider methods

    def get_wiki_syntax(self):
        return []

    def get_link_resolvers(self):
        """Build link resolvers, and return them in a list."""

        def _username_link_resolver(formatter, ns, target, label):
            """Create and return the HTML fragment for the user:
            TracLink. Including a link to the Wiki page of the user
            if that is available.
            """
            username = target
            kwargs = {
                        'title': "username: " + username,
                        'class_': 'trac-author-user'
                     }
            ws = WikiSystem(formatter.env)
            if 'WIKI_VIEW' in formatter.perm and ws.has_page(username):
                kwargs['href'] = formatter.href.wiki(username)
            return tag.a(label, **kwargs)

        def _fullname_resolver(formatter, ns, target, label):
            """Create and return the HTML fragment for the
            full-username: TracLink.
            """
            fullname = target
            return tag.a(label, class_='trac-author-user')

        return [
            ('user', _username_link_resolver),
            ('full-username', _fullname_resolver)
            ]


class SignatureMacro(WikiMacroBase):
    """[required] Provides the `[[Signature(....)]]` macro to generate
    a signature with an username and/or timestamp.
    
    The macro accepts the following three positional parameters:
    * first parameter (username): the (short) username of the person
      that placed the signature.
    * second parameter (timestamp): an ISO8601 formatted date that
      specifies the date and time when then signature was placed.
    * third parameter (fullname): the fullname of the person that
      placed the signature. This fullname will be the text that will be
      shown as being the signature.
    All the parameters are optional, but at least one of them should be
    specified.
    
    If the username or fullname is specified, the `user:` !TracLink will
    be used to show the username in the standard Trac formatting style.
    If the username has a Wiki page, the shown username will also be
    linked to that Wiki page.
    If the timestamp is specified, a pretty formatted difference to the
    actual time is being shown. This can for example result in the text:
    `12 minutes ago`. The shown text is also linked to the Timeline for
    the moment of the timestamp. This linking is achieved by using the
    `timeline:` !TracLink. The exact timestamp is available in the 
    tooltip of the pretty formatted timestamp.
    
    `[[Signature(joro, 2019-10-19T14:56, John de Rooij)]]` will for
    example result in: \"John de Rooij 3 months ago\"
    """

    _description = cleandoc(__doc__)

    regexp = r'''
            ^\s*
            (?P<username>[^,]*)?\s*
            (?:,
                \s*(?P<timestamp>[^,]*)?\s*
                (?:,
                    \s*(?P<fullname>.*)?
                )?
            )?
            $
            '''
    
    def __init__(self):
        """Construct the instance, and create the precompiled
        regular expression for the macro arguments.
        """
        self.contentRegexp = re.compile(self.regexp, re.VERBOSE)

    def expand_macro(self, formatter, name, content, args):
        """Interpret the macro, perform the macro action and
        return the corresponding HTML fragment.
        """
        args = self.contentRegexp.match(content or '')
        if args: 
            username = args.groupdict().get('username')
            timestamp = args.groupdict().get('timestamp')
            fullname = args.groupdict().get('fullname')

            if not fullname or len(fullname) == 0:
                fullname = username

            signature = fullname or ''
            if username and len(username):
                signature = ''.join([
                                    '[[user:', username, '|',
                                    fullname or username, ']]'
                                    ])
            elif fullname and len(fullname):
                signature = ''.join([
                                    '[[full-username:', fullname,
                                    '|', fullname, ']]'
                                    ])
                
            timeline = ''
            if timestamp and len(timestamp):
                tzinfo = getattr(formatter.context.req, 'tz', None)
                try:
                    dateobject = parse_date(timestamp)
                    now = datetime.now(tzinfo or localtz)
                    date_suffix = "ago" if dateobject <= now else "in the future"
                    timeline = ''.join([
                                        '[[timeline:', timestamp, '|',
                                        pretty_timedelta(dateobject, now),
                                        " ", date_suffix, ']]'
                                       ])
                except TracError:
                    pass

            result = ''.join([signature or '', " ", timeline or '']).strip()
            # Convert Wiki markup to HTML
            return format_to_oneliner(self.env, formatter.context, result)
        else:
            # No content is parsed
            return ''

