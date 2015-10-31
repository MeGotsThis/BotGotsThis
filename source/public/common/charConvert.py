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
    return ''.join([_translateAsciiChain(c) for c in text[::-1]])

def _translateAsciiChain(c):
    c = _translate(c, full, ascii)
    c = _translate(c, parenthesized, ascii)
    c = _translate(c, circled, ascii)
    c = _translate(c, smallcaps, ascii)
    c = _translate(c, upsidedown, ascii)
    return c
