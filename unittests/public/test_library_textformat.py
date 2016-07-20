import unittest
from source.public.library import textformat
from unittest.mock import Mock, patch

def translate(text):
    return text


class TestLibraryTextToFormat(unittest.TestCase):
    def test(self):
        to = (''' 1'3457"908=<_>?'''
              ')!@#$%^&*('
              ';:,+./2'
              'abcdefghijklmnopqrstuvwxyz'
              '{|}6-~'
              'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
              r'[\]`')
        trans = textformat._createAsciiTo('test', to)
        self.assertEqual(trans(''), '')
        self.assertEqual(trans('abcABC1²'), 'ABCabc!²')
        self.assertEqual(trans('Kappa'), 'kAPPA')

    def test_full(self):
        self.assertEqual(
            textformat.to_full_width('abcABC1²'), 'ａｂｃＡＢＣ１²')
        self.assertEqual(textformat.to_full_width('Kappa'), 'Ｋａｐｐａ')

    def test_parenthesized(self):
        self.assertEqual(
            textformat.to_parenthesized('abcABC1²'), '⒜⒝⒞⒜⒝⒞⑴²')
        self.assertEqual(textformat.to_parenthesized('Kappa'), '⒦⒜⒫⒫⒜')

    def test_circled(self):
        self.assertEqual(textformat.to_circled('abcABC1²'), 'ⓐⓑⓒⒶⒷⒸ①²')
        self.assertEqual(textformat.to_circled('Kappa'), 'Ⓚⓐⓟⓟⓐ')

    def test_small_caps(self):
        self.assertEqual(textformat.to_small_caps('abcABC1²'), 'ᴀʙᴄᴀʙᴄ1²')
        self.assertEqual(textformat.to_small_caps('Kappa'), 'ᴋᴀᴩᴩᴀ')

    def test_upside_down(self):
        self.assertEqual(textformat.to_upside_down('abcABC1²'), '²1ɔqɐɔqɐ')
        self.assertEqual(textformat.to_upside_down('Kappa'), 'ɐddɐʞ')

    def test_serif_bold(self):
        self.assertEqual(textformat.to_serif_bold('abcABC1²'), '𝐚𝐛𝐜𝐀𝐁𝐂𝟏²')
        self.assertEqual(textformat.to_serif_bold('Kappa'), '𝐊𝐚𝐩𝐩𝐚')

    def test_serif_italic(self):
        self.assertEqual(textformat.to_serif_italic('abcABC1²'), '𝑎𝑏𝑐𝐴𝐵𝐶1²')
        self.assertEqual(textformat.to_serif_italic('Kappa'), '𝐾𝑎𝑝𝑝𝑎')

    def test_serif_bold_italic(self):
        self.assertEqual(
            textformat.to_serif_bold_italic('abcABC1²'), '𝒂𝒃𝒄𝑨𝑩𝑪𝟏²')
        self.assertEqual(
            textformat.to_serif_bold_italic('Kappa'), '𝑲𝒂𝒑𝒑𝒂')

    def test_sanserif(self):
        self.assertEqual(textformat.to_sanserif('abcABC1²'), '𝖺𝖻𝖼𝖠𝖡𝖢𝟣²')
        self.assertEqual(textformat.to_sanserif('Kappa'), '𝖪𝖺𝗉𝗉𝖺')

    def test_sanserif_bold(self):
        self.assertEqual(textformat.to_sanserif_bold('abcABC1²'), '𝗮𝗯𝗰𝗔𝗕𝗖𝟭²')
        self.assertEqual(textformat.to_sanserif_bold('Kappa'), '𝗞𝗮𝗽𝗽𝗮')

    def test_sanserif_italic(self):
        self.assertEqual(textformat.to_sanserif_italic('abcABC1²'), '𝘢𝘣𝘤𝘈𝘉𝘊𝟣²')
        self.assertEqual(textformat.to_sanserif_italic('Kappa'), '𝘒𝘢𝘱𝘱𝘢')

    def test_sanserif_bold_italic(self):
        self.assertEqual(
            textformat.to_sanserif_bold_italic('abcABC1²'), '𝙖𝙗𝙘𝘼𝘽𝘾𝟭²')
        self.assertEqual(textformat.to_sanserif_bold_italic('Kappa'), '𝙆𝙖𝙥𝙥𝙖')

    def test_script(self):
        self.assertEqual(textformat.to_script('abcABC1²'), '𝒶𝒷𝒸𝒜ℬ𝒞1²')
        self.assertEqual(textformat.to_script('Kappa'), '𝒦𝒶𝓅𝓅𝒶')

    def test_script_bold(self):
        self.assertEqual(textformat.to_script_bold('abcABC1²'), '𝓪𝓫𝓬𝓐𝓑𝓒𝟏²')
        self.assertEqual(textformat.to_script_bold('Kappa'), '𝓚𝓪𝓹𝓹𝓪')

    def test_fraktur(self):
        self.assertEqual(textformat.to_fraktur('abcABC1²'), '𝔞𝔟𝔠𝔄𝔅ℭ1²')
        self.assertEqual(textformat.to_fraktur('Kappa'), '𝔎𝔞𝔭𝔭𝔞')

    def test_fraktur_bold(self):
        self.assertEqual(textformat.to_fraktur_bold('abcABC1²'), '𝖆𝖇𝖈𝕬𝕭𝕮𝟏²')
        self.assertEqual(textformat.to_fraktur_bold('Kappa'), '𝕶𝖆𝖕𝖕𝖆')

    def test_monospace(self):
        self.assertEqual(textformat.to_monospace('abcABC1²'), '𝚊𝚋𝚌𝙰𝙱𝙲𝟷²')
        self.assertEqual(textformat.to_monospace('Kappa'), '𝙺𝚊𝚙𝚙𝚊')

    def test_double_struck(self):
        self.assertEqual(textformat.to_double_struck('abcABC1²'), '𝕒𝕓𝕔𝔸𝔹ℂ𝟙²')
        self.assertEqual(textformat.to_double_struck('Kappa'), '𝕂𝕒𝕡𝕡𝕒')

    def test_ascii(self):
        self.assertEqual(
            textformat.to_ascii('ZＺⓏ𝐙𝑍𝒁𝖹𝗭𝘡𝙕𝒵𝓩ℨ𝖅𝚉ℤ⒵ᴢz'), 'Z' * 16 + 'zzz')
        self.assertEqual(textformat.to_ascii('9９⑼⑨𝟗𝟫𝟵𝟫𝟵𝟗𝟗𝟿𝟡'), '9' * 13)
        self.assertEqual(textformat.to_ascii('Ⓚ⒜𝐩𝒑𝔞𝙋r𝔦𝑑ᴇ'), 'KappaPride')
        self.assertEqual(textformat.to_ascii('𝐹𝗿𝙖𝐧𝔨𝖊rℤ'), 'FrankerZ')


class TestLibraryTextFormat(unittest.TestCase):
    def test_blank(self):
        self.assertEqual(textformat.format('', ''), '')
        self.assertEqual(textformat.format('Kappa', ''), 'Kappa')

    @patch('source.public.library.textformat.to_ascii',
           autospec=True, side_effect=translate)
    def test_ascii(self, mock_to):
        self.assertEqual(textformat.format('', 'ascii'), '')
        mock_to.assert_called_once_with('')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'AsCiI'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'ASCII'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_full_width',
           autospec=True, side_effect=translate)
    def test_full(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'full'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_parenthesized',
           autospec=True, side_effect=translate)
    def test_parenthesized(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'parenthesized'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_circled',
           autospec=True, side_effect=translate)
    def test_circled(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'circled'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_small_caps',
           autospec=True, side_effect=translate)
    def test_smallcaps(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'smallcaps'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_upside_down',
           autospec=True, side_effect=translate)
    def test_upsidedown(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'upsidedown'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_serif_bold',
           autospec=True, side_effect=translate)
    def test_serif_bold(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'serif-bold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'serifbold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_serif_italic',
           autospec=True, side_effect=translate)
    def test_serif_italic(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'serif-italic'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'serifitalic'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_serif_bold_italic',
           autospec=True, side_effect=translate)
    def test_serif_bold_italic(self, mock_to):
        formats = ['serif-bold-italic',
                   'serifbold-italic',
                   'serif-bolditalic',
                   'serifbolditalic',
                   'serif-italic-bold',
                   'serifitalic-bold',
                   'serif-italicbold',
                   'serifitalicbold',
                   ]
        for format_ in formats:
            self.assertEqual(textformat.format('Kappa', format_), 'Kappa',
                             format_)
            mock_to.assert_called_once_with('Kappa')
            mock_to.reset_mock()

    @patch('source.public.library.textformat.to_sanserif',
           autospec=True, side_effect=translate)
    def test_sanserif(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'sanserif'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_sanserif_bold',
           autospec=True, side_effect=translate)
    def test_sanserif_bold(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'sanserif-bold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'bold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_sanserif_italic',
           autospec=True, side_effect=translate)
    def test_sanserif_italic(self, mock_to):
        self.assertEqual(
            textformat.format('Kappa', 'sanserif-italic'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'italic'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_sanserif_bold_italic',
           autospec=True, side_effect=translate)
    def test_sanserif_bold_italic(self, mock_to):
        formats = ['sanserif-bold-italic',
                   'sanserifbold-italic',
                   'sanserif-bolditalic',
                   'sanserifbolditalic',
                   'sanserif-italic-bold',
                   'sanserifitalic-bold',
                   'sanserif-italicbold',
                   'sanserifitalicbold',
                   'bold-italic',
                   'bolditalic',
                   'italic-bold',
                   'italicbold',
                   ]
        for format_ in formats:
            self.assertEqual(textformat.format('Kappa', format_), 'Kappa',
                             format_)
            mock_to.assert_called_once_with('Kappa')
            mock_to.reset_mock()

    @patch('source.public.library.textformat.to_script',
           autospec=True, side_effect=translate)
    def test_script(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'script'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'cursive'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()

    @patch('source.public.library.textformat.to_script_bold',
           autospec=True, side_effect=translate)
    def test_script_bold(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'script-bold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'scriptbold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'cursive-bold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'cursivebold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_fraktur',
           autospec=True, side_effect=translate)
    def test_fraktur(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'fraktur'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_fraktur_bold',
           autospec=True, side_effect=translate)
    def test_fraktur_bold(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'fraktur-bold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
        mock_to.reset_mock()
        self.assertEqual(textformat.format('Kappa', 'frakturbold'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_monospace',
           autospec=True, side_effect=translate)
    def test_monospace(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'monospace'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')

    @patch('source.public.library.textformat.to_double_struck',
           autospec=True, side_effect=translate)
    def test_doublestruck(self, mock_to):
        self.assertEqual(textformat.format('Kappa', 'doublestruck'), 'Kappa')
        mock_to.assert_called_once_with('Kappa')
