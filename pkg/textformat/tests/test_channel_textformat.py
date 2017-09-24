from tests.unittest.base_channel import TestChannel
from lib.data.message import Message

# Needs to be imported last
from .. import channel


class TestChannelTextFormat(TestChannel):
    async def test_text_command(self):
        command = channel.text_command('command', lambda s: s)
        self.assertIs(await command(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        self.assertIs(await command(self.args._replace(message=message)), True)
        self.channel.send.assert_called_once_with('Kappa')

    async def test_full(self):
        self.assertIs(await channel.commandFull(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandFull(args), True)
        self.channel.send.assert_called_once_with('Ｋａｐｐａ')

    async def test_parenthesized(self):
        self.assertIs(await channel.commandParenthesized(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandParenthesized(args), True)
        self.channel.send.assert_called_once_with('⒦⒜⒫⒫⒜')

    async def test_circled(self):
        self.assertIs(await channel.commandCircled(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandCircled(args), True)
        self.channel.send.assert_called_once_with('Ⓚⓐⓟⓟⓐ')

    async def test_small_caps(self):
        self.assertIs(await channel.commandSmallCaps(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandSmallCaps(args), True)
        self.channel.send.assert_called_once_with('ᴋᴀᴩᴩᴀ')

    async def test_upsidedown(self):
        self.assertIs(await channel.commandUpsideDown(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandUpsideDown(args), True)
        self.channel.send.assert_called_once_with('ɐddɐʞ')

    async def test_serif_bold(self):
        self.assertIs(await channel.commandSerifBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandSerifBold(args), True)
        self.channel.send.assert_called_once_with('𝐊𝐚𝐩𝐩𝐚')

    async def test_serif_italic(self):
        self.assertIs(await channel.commandSerifItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandSerifItalic(args), True)
        self.channel.send.assert_called_once_with('𝐾𝑎𝑝𝑝𝑎')

    async def test_serif_bold_italic(self):
        self.assertIs(await channel.commandSerifBoldItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandSerifBoldItalic(args), True)
        self.channel.send.assert_called_once_with('𝑲𝒂𝒑𝒑𝒂')

    async def test_sanserif(self):
        self.assertIs(await channel.commandSanSerif(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandSanSerif(args), True)
        self.channel.send.assert_called_once_with('𝖪𝖺𝗉𝗉𝖺')

    async def test_sanserif_bold(self):
        self.assertIs(await channel.commandSanSerifBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandSanSerifBold(args), True)
        self.channel.send.assert_called_once_with('𝗞𝗮𝗽𝗽𝗮')

    async def test_sanserif_italic(self):
        self.assertIs(await channel.commandSanSerifItalic(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandSanSerifItalic(args), True)
        self.channel.send.assert_called_once_with('𝘒𝘢𝘱𝘱𝘢')

    async def test_sanserif_bold_italic(self):
        self.assertIs(await channel.commandSanSerifBoldItalic(self.args),
                      False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandSanSerifBoldItalic(args), True)
        self.channel.send.assert_called_once_with('𝙆𝙖𝙥𝙥𝙖')

    async def test_script(self):
        self.assertIs(await channel.commandScript(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandScript(args), True)
        self.channel.send.assert_called_once_with('𝒦𝒶𝓅𝓅𝒶')

    async def test_script_bold(self):
        self.assertIs(await channel.commandScriptBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandScriptBold(args), True)
        self.channel.send.assert_called_once_with('𝓚𝓪𝓹𝓹𝓪')

    async def test_fraktur(self):
        self.assertIs(await channel.commandFraktur(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandFraktur(args), True)
        self.channel.send.assert_called_once_with('𝔎𝔞𝔭𝔭𝔞')

    async def test_fraktur_bold(self):
        self.assertIs(await channel.commandFrakturBold(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandFrakturBold(args), True)
        self.channel.send.assert_called_once_with('𝕶𝖆𝖕𝖕𝖆')

    async def test_monospace(self):
        self.assertIs(await channel.commandMonospace(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandMonospace(args), True)
        self.channel.send.assert_called_once_with('𝙺𝚊𝚙𝚙𝚊')

    async def test_double_struck(self):
        self.assertIs(await channel.commandDoubleStruck(self.args), False)
        message = Message('!convert Kappa')
        self.permissionSet['moderator'] = True
        self.features.append('textconvert')
        args = self.args._replace(message=message)
        self.assertIs(await channel.commandDoubleStruck(args), True)
        self.channel.send.assert_called_once_with('𝕂𝕒𝕡𝕡𝕒')
