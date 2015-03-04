import database.factory
import ircbot.irc

ascii = (''' !"#$%&'()*+,-./'''
          '0123456789'
          ':;<=>?@'
          'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
          '[\\]^_`'
          'abcdefghijklmnopqrstuvwxyz'
          '{|}~')
wide = ('''　！＂＃＄％＆＇（）＊＋，ー．／'''
        '０１２３４５６７８９'
        '：；〈＝〉？＠'
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
        '［＼］＾＿｀'
        'ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        '｛｜｝～')
parenthesized = (''' !"#$%&'()*+,-./'''
                 '0⑴⑵⑶⑷⑸⑹⑺⑻⑼'
                 ':;<=>?@'
                 '⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵'
                 '[\\]^_`'
                 '⒜⒝⒞⒟⒠⒡⒢⒣⒤⒥⒦⒧⒨⒩⒪⒫⒬⒭⒮⒯⒰⒱⒲⒳⒴⒵'
                 '{|}~')
circled = (''' !"#$%&'()*+,-./'''
           '⓪①②③④⑤⑥⑦⑧⑨'
           ':;<=>?@'
           'ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ'
           '[\\]^_`'
           'ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ'
           '{|}~')
smallcaps = (''' !"#$%&'()*+,-./'''
             '0123456789'
             ':;<=>?@'
             'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴩQʀꜱᴛᴜᴠᴡxYᴢ'
             '[\\]^_`'
             'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴩqʀꜱᴛᴜᴠᴡxyᴢ'
             '{|}~')
upsidedown = (''' ¡"#$%⅋,()*+‘-./'''
              '0123456789'
              ':;<=>¿@'
              'ɐqɔpǝɟƃɥıɾʞןɯuodbɹsʇnʌʍxʎz'
              '[\\]^_`'
              'ɐqɔpǝɟƃɥıɾʞןɯuodbɹsʇnʌʍxʎz'
              '{|}~')

def _translate(character, fromTable, toTable):
    if len(character) != 1:
        raise ValueError("Character needs to be length 1")
    j = fromTable.find(character)
    return toTable[j] if j != -1 else character

def asciiToFullWidth(text):
    return ''.join([_translate(c, ascii, wide) for c in text])

def asciiToParenthesized(text):
    return ''.join([_translate(c, ascii, parenthesized) for c in text])

def asciiToCircled(text):
    return ''.join([_translate(c, ascii, circled) for c in text])

def asciiToSmallCaps(text):
    return ''.join([_translate(c, ascii, smallcaps) for c in text])

def asciiToUpsideDown(text):
    return ''.join([_translate(c, ascii, upsidedown) for c in text[::-1]])

def commandFull(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if not db.hasFeature(channelData.channel[1:], 'textconvert'):                                   
            return False
    
    msg = message.split(None, 1)[1]
    return channelData.sendMessage(asciiToFullWidth(msg))

def commandParenthesized(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if not db.hasFeature(channelData.channel[1:], 'textconvert'):                                   
            return False
    
    msg = message.split(None, 1)[1]
    return channelData.sendMessage(asciiToParenthesized(msg))

def commandCircled(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if not db.hasFeature(channelData.channel[1:], 'textconvert'):                                   
            return False
    
    msg = message.split(None, 1)[1]
    return channelData.sendMessage(asciiToCircled(msg))

def commandSmallCaps(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if not db.hasFeature(channelData.channel[1:], 'textconvert'):                                   
            return False
    
    msg = message.split(None, 1)[1]
    return channelData.sendMessage(asciiToSmallCaps(msg))

def commandUpsideDown(channelData, nick, message, msgParts, permissions):
    with database.factory.getDatabase() as db:
        if not db.hasFeature(channelData.channel[1:], 'textconvert'):                                   
            return False
    
    msg = message.split(None, 1)[1]
    return channelData.sendMessage(asciiToUpsideDown(msg))
