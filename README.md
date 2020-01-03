# TracMediaWikiSignature
TracMediaWikiSignature is a Trac plugin that allows to use the MediaWiki signatures ("~~~~") on the Trac Wiki pages.

For the behaviour of the MediaWiki signature see: https://www.mediawiki.org/wiki/Help:Signatures

# Specifications
When the TracMediaWikiSignature plugin is installed in a Trac installation, the MediaWikiSignature can be used on Wiki pages that are edited. 

The 4 tildes signature "~~~~" will be replaced with the Username and the timestamp.

The 3 tildes signature "~~~" will be replaced with the Username only.

The 5 tildes signature "~~~~~" will be replaced with the timestamp only.



The Username will be the full username if that is known within the Trac system. Otherwise the short username will be used, and otherwise it will be replaced by the IP address of the editor. The username is not linked to a specific page of the user, it will only be a simple text. While it is possible to customize the signature of the username on a MediaWiki website, that will not be possible with this plugin.

The timestamp is expressed as the local time of the editor and will be formatted as the default date and time format as it is configured in the Trac system for that user.

The signatures will be replaced at the moment that the Trac Wiki page is succesfully saved. Any validation error that triggers that the Trac Wiki page cannot be saved will also prevent that the replacement of the MediaWiki signature is performed.

During the editing, and in the preview of the Trac Wiki page, the tildes of the signature and the Username and date-time stamp will not be visible. The replaced signature is only visible when the Trac Wiki page is succesfully saved and shown.

# Installation
The plugin is provided through the GitHub repository at https://github.com/joro75/TracMediaWikiSignature

Install the plugin by creating a Python Egg, as instructed on the Trac Wiki at: https://trac.edgewall.org/wiki/TracPlugins#Forasingleproject
 * Checkout or download and unpack the source.
 * Change to the directory containing setup.py.
 * Run:
    '$ python setup.py bdist_egg'
 * The egg file will be created in the dist subdirectory.
 * Copy the egg file to the plugins directory of the project environment.
 * Make sure the web server has sufficient permissions to read the plugin egg and restart the web server. If you are running as a "tracd" standalone server, restart tracd (i.e. kill the process and run again).

# Known problems
No problems are known yet. If you have notice a problem, please let me know by creating an issue on the GitHub repository at https://github.com/joro75/TracMediaWikiSignature/issues.
