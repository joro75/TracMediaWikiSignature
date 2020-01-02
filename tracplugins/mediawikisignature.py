# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2020 John de Rooij
# All rights reserved.
#
# This software is licensed as described in the file LICENSE, which
# you should have received as part of this distribution.

from trac.core import Component, implements
from trac.util import get_reporter_id
from trac.wiki.api import IWikiPageManipulator

class MediaWikiSignatureManipulator(Component):
    _description = "Replaces the MediaWiki signature with the author name."

    implements(IWikiPageManipulator)

    # IWikiPageManipulator

    def prepare_wiki_page(self, req, page, fields):
        pass

    def validate_wiki_page(self, req, page):
        text = page.text
        if len(text):
            fullname = req.session.get('name') or ''
            username = get_reporter_id(req)
            signature = username
            if len(fullname):
                signature = fullname + ' (%s)' % username

            page.text = text.replace('~~~~', signature)

        return []
