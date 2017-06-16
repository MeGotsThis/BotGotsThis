from source.data.message import Message
from tests.unittest.base_channel import TestChannel

# Needs to be imported last
from source.public.channel import textformat


class TestChannelTextFormat(TestChannel):
    async def test_text_command(self):
        command = textformat.text_command('command', lambda s: s)
        self.assertIs(await command(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        self.assertIs(await command(self.args._replace(message=message)), True)
        self.channel.send.assert_called_once_with('Kappa')

    async def test_full(self):
        self.assertIs(await textformat.commandFull(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandFull(args), True)
        self.channel.send.assert_called_once_with('Ｋａｐｐａ')

    async def test_parenthesized(self):
        self.assertIs(await textformat.commandParenthesized(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandParenthesized(args), True)
        self.channel.send.assert_called_once_with('⒦⒜⒫⒫⒜')

    async def test_circled(self):
        self.assertIs(await textformat.commandCircled(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandCircled(args), True)
        self.channel.send.assert_called_once_with('Ⓚⓐⓟⓟⓐ')

    async def test_small_caps(self):
        self.assertIs(await textformat.commandSmallCaps(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandSmallCaps(args), True)
        self.channel.send.assert_called_once_with('ᴋᴀᴩᴩᴀ')

    async def test_upsidedown(self):
        self.assertIs(await textformat.commandUpsideDown(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandUpsideDown(args), True)
        self.channel.send.assert_called_once_with('ɐddɐʞ')

    async def test_serif_bold(self):
        self.assertIs(await textformat.commandSerifBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandSerifBold(args), True)
        self.channel.send.assert_called_once_with('𝐊𝐚𝐩𝐩𝐚')

    async def test_serif_italic(self):
        self.assertIs(await textformat.commandSerifItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandSerifItalic(args), True)
        self.channel.send.assert_called_once_with('𝐾𝑎𝑝𝑝𝑎')

    async def test_serif_bold_italic(self):
        self.assertIs(await textformat.commandSerifBoldItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandSerifBoldItalic(args), True)
        self.channel.send.assert_called_once_with('𝑲𝒂𝒑𝒑𝒂')

    async def test_sanserif(self):
        self.assertIs(await textformat.commandSanSerif(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandSanSerif(args), True)
        self.channel.send.assert_called_once_with('𝖪𝖺𝗉𝗉𝖺')

    async def test_sanserif_bold(self):
        self.assertIs(await textformat.commandSanSerifBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandSanSerifBold(args), True)
        self.channel.send.assert_called_once_with('𝗞𝗮𝗽𝗽𝗮')

    async def test_sanserif_italic(self):
        self.assertIs(await textformat.commandSanSerifItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandSanSerifItalic(args), True)
        self.channel.send.assert_called_once_with('𝘒𝘢𝘱𝘱𝘢')

    async def test_sanserif_bold_italic(self):
        self.assertIs(await textformat.commandSanSerifBoldItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandSanSerifBoldItalic(args), True)
        self.channel.send.assert_called_once_with('𝙆𝙖𝙥𝙥𝙖')

    async def test_script(self):
        self.assertIs(await textformat.commandScript(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandScript(args), True)
        self.channel.send.assert_called_once_with('𝒦𝒶𝓅𝓅𝒶')

    async def test_script_bold(self):
        self.assertIs(await textformat.commandScriptBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandScriptBold(args), True)
        self.channel.send.assert_called_once_with('𝓚𝓪𝓹𝓹𝓪')

    async def test_fraktur(self):
        self.assertIs(await textformat.commandFraktur(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandFraktur(args), True)
        self.channel.send.assert_called_once_with('𝔎𝔞𝔭𝔭𝔞')

    async def test_fraktur_bold(self):
        self.assertIs(await textformat.commandFrakturBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandFrakturBold(args), True)
        self.channel.send.assert_called_once_with('𝕶𝖆𝖕𝖕𝖆')

    async def test_monospace(self):
        self.assertIs(await textformat.commandMonospace(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandMonospace(args), True)
        self.channel.send.assert_called_once_with('𝙺𝚊𝚙𝚙𝚊')

    async def test_double_struck(self):
        self.assertIs(await textformat.commandDoubleStruck(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await textformat.commandDoubleStruck(args), True)
        self.channel.send.assert_called_once_with('𝕂𝕒𝕡𝕡𝕒')
