ascii = (''' !"#$%&'()*+,-./'''
          '0123456789'
          ':;<=>?@'
          'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
          '[\\]^_`'
          'abcdefghijklmnopqrstuvwxyz'
          '{|}~')
full = ('''　！＂＃＄％＆＇（）＊＋，ー．／'''
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
             'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴩQʀsᴛᴜᴠᴡxYᴢ'
             '[\\]^_`'
             'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴩqʀsᴛᴜᴠᴡxyᴢ'
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
    return ''.join([_translate(c, ascii, full) for c in text])

def asciiToParenthesized(text):
    return ''.join([_translate(c, ascii, parenthesized) for c in text])

def asciiToCircled(text):
    return ''.join([_translate(c, ascii, circled) for c in text])

def asciiToSmallCaps(text):
    return ''.join([_translate(c, ascii, smallcaps) for c in text])

def asciiToUpsideDown(text):
    return ''.join([_translate(c, ascii, upsidedown) for c in text[::-1]])

def allToAscii(text):
    return ''.join([_translateAsciiChain(c, ascii, upsidedown)
                    for c in text[::-1]])

def _translateAsciiChain(c):
    c = _translate(c, full, ascii)
    c = _translate(c, parenthesized, ascii)
    c = _translate(c, circled, ascii)
    c = _translate(c, smallcaps, ascii)
    c = _translate(c, upsidedown, ascii)
    return c

def commandFull(db, channel, nick, message, msgParts, permissions):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(asciiToFullWidth(parts[1]))
    return True

def commandParenthesized(db, channel, nick, message, msgParts, permissions):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(asciiToParenthesized(parts[1]))
    return True

def commandCircled(db, channel, nick, message, msgParts, permissions):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(asciiToCircled(parts[1]))
    return True

def commandSmallCaps(db, channel, nick, message, msgParts, permissions):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(asciiToSmallCaps(parts[1]))
    return True

def commandUpsideDown(channel, nick, message, msgParts, permissions):
    if not db.hasFeature(channel.channel, 'textconvert'):
        return False
    
    parts = message.split(None, 1)
    if len(parts) < 2:
        return False
    channel.sendMessage(asciiToUpsideDown(parts[1]))
    return True
