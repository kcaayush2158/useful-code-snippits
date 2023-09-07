import os
import sys
import markdown
import re
import codecs
from markdown.extensions.codehilite import CodeHilite, CodeHiliteExtension, parse_hl_lines
from markdown.extensions.extra import ExtraExtension

CODE_WRAP = '<ac:structured-macro ac:name="code">%s<ac:plain-text-body><![CDATA[%s]]></ac:plain-text-body></ac:structured-macro>'
LANG_TAG = '<ac:parameter ac:name="language">%s</ac:parameter>'


class FencedCodeExtension(markdown.Extension):
    def __init__(self, *args, **kwargs):
        self.config = {
            'escape': ['True', 'Escape HTML special chars'],
            'code_wrap': ['<pre><code%s>%s</code></pre>', 'Code wrapper tag'],
            'lang_tag': [' class="%s"', 'Code wrapper\'s tag']
        }
        super(FencedCodeExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)
        processor = FencedBlockPreprocessor(md)
        processor.config = self.getConfigs()
        md.preprocessors.add('fenced_code_block',
                             processor,
                             ">normalize_whitespace")


class FencedBlockPreprocessor(markdown.preprocessors.Preprocessor):
    FENCED_BLOCK_RE = re.compile(r'''
        (?P<fence>^(?:~{3,}|`{3,}))[ ]*         # Opening ``` or ~~~
        (\{?\.?(?P<lang>[a-zA-Z0-9_+-]*))?[ ]*  # Optional {, and lang
        # Optional highlight lines, single- or double-quote-delimited
        (hl_lines=(?P<quot>"|')(?P<hl_lines>.*?)(?P=quot))?[ ]*
        }?[ ]*\n                                # Optional closing }
        (?P<code>.*?)(?<=\n)
        (?P=fence)[ ]*$''', re.MULTILINE | re.DOTALL | re.VERBOSE)

    def __init__(self, md):
        super(FencedBlockPreprocessor, self).__init__(md)
        self.checked_for_codehilite = False
        self.codehilite_conf = {}

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        # Check for code hilite extension
        if not self.checked_for_codehilite:
            for ext in self.markdown.registeredExtensions:
                if isinstance(ext, CodeHiliteExtension):
                    self.codehilite_conf = ext.config
                    break

            self.checked_for_codehilite = True

        text = "\n".join(lines)
        while 1:
            m = self.FENCED_BLOCK_RE.search(text)
            if m:
                lang = ''
                if m.group('lang'):
                    lang = self.config['lang_tag'] % m.group('lang')

                # If config is not empty, then the codehilite extension
                # is enabled, so we call it to highlight the code
                if self.codehilite_conf:
                    highliter = CodeHilite(
                        m.group('code'),
                        linenums=self.codehilite_conf['linenums'][0],
                        guess_lang=self.codehilite_conf['guess_lang'][0],
                        css_class=self.codehilite_conf['css_class'][0],
                        style=self.codehilite_conf['pygments_style'][0],
                        use_pygments=self.codehilite_conf['use_pygments'][0],
                        lang=(m.group('lang') or None),
                        noclasses=self.codehilite_conf['noclasses'][0],
                        hl_lines=parse_hl_lines(m.group('hl_lines'))
                    )

                    code = highliter.hilite()
                else:
                    if self.config['escape']:
                        code = self._escape(m.group('code'))
                    else:
                        code = m.group('code')
                    code = self.config['code_wrap'] % (lang, code)

                placeholder = self.markdown.htmlStash.store(code, safe=True)
                text = '%s\n%s\n%s' % (text[:m.start()],
                                       placeholder,
                                       text[m.end():])
            else:
                break
        return text.split("\n")

    def _escape(self, txt):
        """ Basic HTML escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt


def find_md_files(folder_path):
    md_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))

    return md_files


def makedirs_p2(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    # Check if the output folder exists and remove it if it does
    # Create the output directory if it doesn't exist
    makedirs_p2(output_folder)

    if not os.path.exists(input_folder):
        print("Input folder '{0}' does not exist.".format(input_folder))
        sys.exit(1)

        # Create the output directory if it doesn't exist
    makedirs_p2(output_folder)

    md_files = find_md_files(input_folder)

    for md_file in md_files:

        # Extract the relative path of the input file
        relative_path = os.path.relpath(md_file, input_folder)
        # Create the subfolders within the output directory based on the relative path
        subfolder_path = os.path.join(output_folder, os.path.dirname(relative_path))

        makedirs_p2(subfolder_path)

        with codecs.open(md_file, 'r', encoding="utf-8") as f:
            md_content = f.read()
            ext = FencedCodeExtension(escape=False, code_wrap=CODE_WRAP, lang_tag=LANG_TAG)
            html = markdown.markdown(md_content, extensions=[ext, ExtraExtension()], output_format="xhtml", safe_mode='replace')

            # Extract the relative path of the input file and use it to create the output file path
            relative_path = os.path.relpath(md_file, input_folder)
            output_file = os.path.join(output_folder, os.path.splitext(relative_path)[0] + '.xhtml')

            # Write the XHTML to the output file
            with codecs.open(output_file, "w", encoding="utf-8") as output:
                    # Wrap the converted XHTML content with the required HTML structure
                        # Wrap the converted XHTML content with the required HTML structure
                    full_html = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" '
                    '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n')
                    full_html += ('<html xmlns="http://www.w3.org/1999/xhtml">\n<head>\n'
                    '<title></title>\n</head>\n<body>\n')
                    full_html += html
                    full_html += '\n</body>\n</html>'
                    output.write(full_html)
            
            print("Conversion to XHTML completed.")
