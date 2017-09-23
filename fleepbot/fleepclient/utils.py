r"""Convert XML back to text and html.
>>> xml = '<msg><p>Para<br/></p><p><q>&gt; Quote</q></p></msg>'
>>> convert_xml_to_text(xml)
u'Para\n\n\n> Quote\n'
>>> convert_xml_to_text(xml, True)
u'Para\n\n\n'
>>> convert_xml_to_text(u'<msg><p><a flp="https://fleep.io&lt;&lt;" fls="&gt;&gt;" href="https://fleep.io">Fleep</a> is the best</p></msg>', no_markup=True)
u'Fleep is the best\n'
>>> convert_xml_to_text(u'<msg><p><a flp="https://fleep.io&lt;&lt;" fls="&gt;&gt;" href="https://fleep.io">Fleep</a> is the best</p></msg>')
u'https://fleep.io<<Fleep>> is the best\n'
"""

import logging
import xml.sax
import xml.sax.handler

__all__ = ['convert_xml_to_text']

##
## XML to Markup conversion
##

class UnparseText(xml.sax.handler.ContentHandler):
    """Extract original plain text.
    """
    #tag_map = { 'pre': ':::' }
    def __init__(self, skip_quote, skip_refs, no_markup):
        xml.sax.handler.ContentHandler.__init__(self)
        self.txt = []
        self.stack = []
        self.skip_quote = skip_quote
        self.skipping = False
        self.no_markup = no_markup

    def startElement(self, name, attrs):
        oldskip = self.skipping
        if name == 'q':
            if self.skip_quote:
                self.skipping = True
        elif name == 'file':
            # always skip file content
            self.skipping = True

        if self.skipping:
            self.stack.append( (name, oldskip, None) )
            return

        if name == 'p' and self.txt:
            self.txt.append('\n\n')
        elif name == 'br':
            self.txt.append('\n')
        if 'flp' in attrs and not self.no_markup:
            self.txt.append(attrs['flp'])

        if not self.no_markup:
            fls = attrs.get('fls', None)
        else:
            fls = None
        self.stack.append( (name, oldskip, fls) )

    def endElement(self, name):
        curskip = self.skipping
        oldname, oldskip, fls = self.stack.pop()
        self.skipping = oldskip
        if oldname != name:
            raise ValueError("Lost sync, broken XML?")

        if curskip:
            return

        if fls:
            self.txt.append(fls)

    def characters(self, data):
        if self.skipping:
            return
        self.txt.append(data)

    def ignorableWhitespace(self, data):
        if self.skipping:
            return
        self.txt.append(data)

    def unparse_result(self):
        if self.txt:
            last = self.txt[-1]
            if last and last[-1] != '\n':
                self.txt.append('\n')
        return ''.join(self.txt)

def convert_xml_to_text(xmlstr, skip_quote=False, skip_refs=False, no_markup=False):
    """Recover original message from XML data.
    """
    if not xmlstr:
        raise ValueError("Empty XML")
    if isinstance(xmlstr, str):
        xmlstr = xmlstr.encode('utf8')
    handler = UnparseText(skip_quote, skip_refs, no_markup)
    try:
        xml.sax.parseString(xmlstr, handler)
    except xml.sax.SAXException:
        logging.debug("convert_xml_to_text: invalid xml: %r", xmlstr)
        raise
    return handler.unparse_result()


# run tests
if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(raise_on_error=('--raise' in sys.argv))