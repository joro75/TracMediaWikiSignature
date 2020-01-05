# TracMediaWikiSignature
TracMediaWikiSignature is a Trac plugin that allows to use the MediaWiki signatures ("~~~~") on the Trac Wiki pages.

During the saving of the Wiki page the MediaWiki signature is replaced by the username and/or the timestamp of the edit. 

Three different variants are possible: 
* The `~~~` will be replaced by the username only 
* The `~~~~` will be replaced by the username and timestamp 
* The `~~~~~` will be replaced by the timestamp only 
With all these variants also a seperating `--` prefix will automatically be included. 

During the editing, and in the preview of the Trac Wiki page, the tildes of the signature and the Username and date-time stamp will not be visible. The replaced signature is only visible when the Trac Wiki page is succesfully saved and shown.

The actual showing of the signature is handled by the `[[Signature(...)]]` macro, to be able to show a pretty formatted username and timestamp. 

# Implementation details
The `[[Signature(...)]]` macro accepts the following three positional parameters: 
* first parameter (username): the (short) username of the person that placed the signature. 
* second parameter (timestamp): an ISO8601 formatted date that specifies the date and time when then signature was placed. 
* third parameter (fullname): the fullname of the person that placed the signature. This fullname will be the text that will be shown as being the signature. 
All the parameters are optional, but at least one of them should be specified. 

If the username or fullname is specified, the `user:` TracLink will be used to show the username in the standard Trac formatting style. 

If the timestamp is specified, a pretty formatted difference to the actual time is being shown. This can for example result in the text: "12 minutes ago". The shown text is also linked to the Timeline for the moment of the timestamp. This linking is achieved by using the `timeline:` TracLink. The exact timestamp is available in the tooltip of the pretty formatted timestamp.

`[[Signature(joro, 2019-10-19T14:56, John de Rooij)]]` will for example result in: "John de Rooij 3 months ago"

The plugin also provides a standard implementation of the `user:` TracLink, which will show the specified username in the standard Trac formatting. This implementation of the `user:` TracLink can be disabled, to allow other plugins to provide a more relevant implementation that links to a specific user page.

# Installation
The plugin is provided through the GitHub repository at https://github.com/joro75/TracMediaWikiSignature

Install the plugin by creating a Python Egg, as instructed on the Trac Wiki at: https://trac.edgewall.org/wiki/TracPlugins#Forasingleproject
 * Checkout or download and unpack the source.
 * Change to the directory containing setup.py.
 * Run:
    `$ python setup.py bdist_egg`
 * The egg file will be created in the dist subdirectory.
 * Copy the egg file to the plugins directory of the project environment.
 * Make sure the web server has sufficient permissions to read the plugin egg and restart the web server. If you are running as a "tracd" standalone server, restart tracd (i.e. kill the process and run again).

# Problems
An initial 1.0 release has not been released yet, and problems could thus still be present. If you have notice a problem, please let me know by creating an issue on the GitHub repository at https://github.com/joro75/TracMediaWikiSignature/issues.
On that same location also a list of all known bugs is available.
