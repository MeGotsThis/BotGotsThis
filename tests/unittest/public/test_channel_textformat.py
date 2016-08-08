from source.data.message import Message
from source.public.channel import textformat
from tests.unittest.base_channel import TestChannel


class TestChannelTextFormat(TestChannel):
    def test_text_command(self):
        command = textformat.text_command('command', lambda s: s)
        self.assertIs(command(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        self.assertIs(command(self.args._replace(message=message)), True)
        self.channel.send.assert_called_once_with('Kappa')

    def test_full(self):
        self.assertIs(textformat.commandFull(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandFull(args), True)
        self.channel.send.assert_called_once_with('Ｋａｐｐａ')

    def test_parenthesized(self):
        self.assertIs(textformat.commandParenthesized(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandParenthesized(args), True)
        self.channel.send.assert_called_once_with('⒦⒜⒫⒫⒜')

    def test_circled(self):
        self.assertIs(textformat.commandCircled(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandCircled(args), True)
        self.channel.send.assert_called_once_with('Ⓚⓐⓟⓟⓐ')

    def test_small_caps(self):
        self.assertIs(textformat.commandSmallCaps(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandSmallCaps(args), True)
        self.channel.send.assert_called_once_with('ᴋᴀᴩᴩᴀ')

    def test_upsidedown(self):
        self.assertIs(textformat.commandUpsideDown(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandUpsideDown(args), True)
        self.channel.send.assert_called_once_with('ɐddɐʞ')

    def test_serif_bold(self):
        self.assertIs(textformat.commandSerifBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandSerifBold(args), True)
        self.channel.send.assert_called_once_with('𝐊𝐚𝐩𝐩𝐚')

    def test_serif_italic(self):
        self.assertIs(textformat.commandSerifItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandSerifItalic(args), True)
        self.channel.send.assert_called_once_with('𝐾𝑎𝑝𝑝𝑎')

    def test_serif_bold_italic(self):
        self.assertIs(textformat.commandSerifBoldItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandSerifBoldItalic(args), True)
        self.channel.send.assert_called_once_with('𝑲𝒂𝒑𝒑𝒂')

    def test_sanserif(self):
        self.assertIs(textformat.commandSanSerif(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandSanSerif(args), True)
        self.channel.send.assert_called_once_with('𝖪𝖺𝗉𝗉𝖺')

    def test_sanserif_bold(self):
        self.assertIs(textformat.commandSanSerifBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandSanSerifBold(args), True)
        self.channel.send.assert_called_once_with('𝗞𝗮𝗽𝗽𝗮')

    def test_sanserif_italic(self):
        self.assertIs(textformat.commandSanSerifItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandSanSerifItalic(args), True)
        self.channel.send.assert_called_once_with('𝘒𝘢𝘱𝘱𝘢')

    def test_sanserif_bold_italic(self):
        self.assertIs(textformat.commandSanSerifBoldItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandSanSerifBoldItalic(args), True)
        self.channel.send.assert_called_once_with('𝙆𝙖𝙥𝙥𝙖')

    def test_script(self):
        self.assertIs(textformat.commandScript(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandScript(args), True)
        self.channel.send.assert_called_once_with('𝒦𝒶𝓅𝓅𝒶')

    def test_script_bold(self):
        self.assertIs(textformat.commandScriptBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandScriptBold(args), True)
        self.channel.send.assert_called_once_with('𝓚𝓪𝓹𝓹𝓪')

    def test_fraktur(self):
        self.assertIs(textformat.commandFraktur(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandFraktur(args), True)
        self.channel.send.assert_called_once_with('𝔎𝔞𝔭𝔭𝔞')

    def test_fraktur_bold(self):
        self.assertIs(textformat.commandFrakturBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandFrakturBold(args), True)
        self.channel.send.assert_called_once_with('𝕶𝖆𝖕𝖕𝖆')

    def test_monospace(self):
        self.assertIs(textformat.commandMonospace(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandMonospace(args), True)
        self.channel.send.assert_called_once_with('𝙺𝚊𝚙𝚙𝚊')

    def test_double_struck(self):
        self.assertIs(textformat.commandDoubleStruck(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(textformat.commandDoubleStruck(args), True)
        self.channel.send.assert_called_once_with('𝕂𝕒𝕡𝕡𝕒')
