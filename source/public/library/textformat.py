import re

ascii = (''' !"#$%&'()*+,-./'''
         '0123456789'
         ':;<=>?@'
         'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
         r'[\]^_`'
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
                 r'[\]^_`'
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
             r'[\]^_`'
             'ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴩqʀsᴛᴜᴠᴡxyᴢ'
             '{|}~')
upsidedown = (''' ¡"#$%⅋,()*+‘-./'''
              '0123456789'
              ':;<=>¿@'
              'ɐqɔpǝɟƃɥıɾʞןɯuodbɹsʇnʌʍxʎz'
              r'[\]^_`'
              'ɐqɔpǝɟƃɥıɾʞןɯuodbɹsʇnʌʍxʎz'
              '{|}~')
serifBold = (''' !"#$%&'()*+,-./'''
             '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
             ':;<=>?@'
             '𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙'
             r'[\]^_`'
             '𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳'
             '{|}~')
serifItalic = (''' !"#$%&'()*+,-./'''
               '0123456789'
               ':;<=>?@'
               '𝐴𝐵𝐶𝐷𝐸𝐹𝐺𝐻𝐼𝐽𝐾𝐿𝑀𝑁𝑂𝑃𝑄𝑅𝑆𝑇𝑈𝑉𝑊𝑋𝑌𝑍'
               r'[\]^_`'
               '𝑎𝑏𝑐𝑑𝑒𝑓𝑔ℎ𝑖𝑗𝑘𝑙𝑚𝑛𝑜𝑝𝑞𝑟𝑠𝑡𝑢𝑣𝑤𝑥𝑦𝑧'
               '{|}~')
serifBoldItalic = (''' !"#$%&'()*+,-./'''
                   '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
                   ':;<=>?@'
                   '𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁'
                   r'[\]^_`'
                   '𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛'
                   '{|}~')
sanSerif = (''' !"#$%&'()*+,-./'''
            '𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫'
            ':;<=>?@'
            '𝖠𝖡𝖢𝖣𝖤𝖥𝖦𝖧𝖨𝖩𝖪𝖫𝖬𝖭𝖮𝖯𝖰𝖱𝖲𝖳𝖴𝖵𝖶𝖷𝖸𝖹'
            r'[\]^_`'
            '𝖺𝖻𝖼𝖽𝖾𝖿𝗀𝗁𝗂𝗃𝗄𝗅𝗆𝗇𝗈𝗉𝗊𝗋𝗌𝗍𝗎𝗏𝗐𝗑𝗒𝗓'
            '{|}~')
sanSerifBold = (''' !"#$%&'()*+,-./'''
                '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵'
                ':;<=>?@'
                '𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭'
                r'[\]^_`'
                '𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇'
                '{|}~')
sanSerifItalic = (''' !"#$%&'()*+,-./'''
                  '𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫'
                  ':;<=>?@'
                  '𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡'
                  r'[\]^_`'
                  '𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻'
                  '{|}~')
sanSerifBoldItalic = (''' !"#$%&'()*+,-./'''
                      '𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵'
                      ':;<=>?@'
                      '𝘼𝘽𝘾𝘿𝙀𝙁𝙂𝙃𝙄𝙅𝙆𝙇𝙈𝙉𝙊𝙋𝙌𝙍𝙎𝙏𝙐𝙑𝙒𝙓𝙔𝙕'
                      r'[\]^_`'
                      '𝙖𝙗𝙘𝙙𝙚𝙛𝙜𝙝𝙞𝙟𝙠𝙡𝙢𝙣𝙤𝙥𝙦𝙧𝙨𝙩𝙪𝙫𝙬𝙭𝙮𝙯'
                      '{|}~')
script = (''' !"#$%&'()*+,-./'''
          '0123456789'
          ':;<=>?@'
          '𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵'
          r'[\]^_`'
          '𝒶𝒷𝒸𝒹ℯ𝒻ℊ𝒽𝒾𝒿𝓀𝓁𝓂𝓃ℴ𝓅𝓆𝓇𝓈𝓉𝓊𝓋𝓌𝓍𝓎𝓏'
          '{|}~')
scriptBold = (''' !"#$%&'()*+,-./'''
              '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
              ':;<=>?@'
              '𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩'
              r'[\]^_`'
              '𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃'
              '{|}~')
fraktur = (''' !"#$%&'()*+,-./'''
           '0123456789'
           ':;<=>?@'
           '𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ'
           r'[\]^_`'
           '𝔞𝔟𝔠𝔡𝔢𝔣𝔤𝔥𝔦𝔧𝔨𝔩𝔪𝔫𝔬𝔭𝔮𝔯𝔰𝔱𝔲𝔳𝔴𝔵𝔶𝔷'
           '{|}~')
frakturBold = (''' !"#$%&'()*+,-./'''
               '𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗'
               ':;<=>?@'
               '𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅'
               r'[\]^_`'
               '𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟'
               '{|}~')
monospace = (''' !"#$%&'()*+,-./'''
             '𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿'
             ':;<=>?@'
             '𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉'
             r'[\]^_`'
             '𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣'
             '{|}~')
doubleStruck = (''' !"#$%&'()*+,-./'''
                '𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡'
                ':;<=>?@'
                '𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ'
                r'[\]^_`'
                '𝕒𝕓𝕔𝕕𝕖𝕗𝕘𝕙𝕚𝕛𝕜𝕝𝕞𝕟𝕠𝕡𝕢𝕣𝕤𝕥𝕦𝕧𝕨𝕩𝕪𝕫'
                '{|}~')


def _translate(character, fromTable, toTable):
    if len(character) != 1:
        raise ValueError("Character needs to be length 1")
    j = fromTable.find(character)
    return toTable[j] if j != -1 else character


def _createAsciiTo(name, toTable):
    def asciiTo(text):
        return ''.join(_translate(c, ascii, toTable) for c in text)
    asciiTo.__name__ = name
    return asciiTo

asciiToFullWidth = _createAsciiTo('asciiToFullWidth', full)
asciiToParenthesized = _createAsciiTo('asciiToParenthesized', parenthesized)
asciiToCircled = _createAsciiTo('asciiToCircled', circled)
asciiToSmallCaps = _createAsciiTo('asciiToSmallCaps', smallcaps)
asciiToUpsideDown = _createAsciiTo('asciiToUpsideDown', upsidedown)
asciiToSerifBold = _createAsciiTo('asciiToSerifBold', serifBold)
asciiToSerifItalic = _createAsciiTo('asciiToSerifItalic', serifItalic)
asciiToSerifBoldItalic = _createAsciiTo('asciiToSerifBoldItalic',
                                        serifBoldItalic)
asciiToSanSerif = _createAsciiTo('asciiToSanSerif', sanSerif)
asciiToSanSerifBold = _createAsciiTo('asciiToSanSerifBold', sanSerifBold)
asciiToSanSerifItalic = _createAsciiTo('asciiToSanSerifItalic', sanSerifItalic)
asciiToSanSerifBoldItalic = _createAsciiTo('asciiToSanSerifBoldItalic',
                                           sanSerifBoldItalic)
asciiToScript = _createAsciiTo('asciiToScript', script)
asciiToScriptBold = _createAsciiTo('asciiToScriptBold', scriptBold)
asciiToFraktur = _createAsciiTo('asciiToFraktur', fraktur)
asciiToFrakturBold = _createAsciiTo('asciiToFrakturBold', frakturBold)
asciiToMonospace = _createAsciiTo('asciiToMonospace', monospace)
asciiToDoubleStruck = _createAsciiTo('asciiToDoubleStruck', doubleStruck)


def allToAscii(text):
    return ''.join([_translateAsciiChain(c) for c in text])


def _translateAsciiChain(c):
    fromTable = [full, parenthesized, circled, smallcaps, upsidedown,
                 serifBold, serifItalic, serifBoldItalic, sanSerif,
                 sanSerifBold, sanSerifItalic, sanSerifBoldItalic, script,
                 scriptBold, fraktur, frakturBold, monospace, doubleStruck]
    for table in fromTable:
        c = _translate(c, table, ascii)
    return c


def format(string, format):
    format = format.lower()
    strTable = {
        'ascii': allToAscii,
        'full': asciiToFullWidth,
        'parenthesized': asciiToParenthesized,
        'circled': asciiToCircled,
        'smallcaps': asciiToParenthesized,
        'upsidedown': asciiToUpsideDown,
        'sanserif': asciiToSanSerif,
        'script': asciiToScript,
        'cursive': asciiToScript,
        'fraktur': asciiToFraktur,
        'monospace': asciiToMonospace,
        'doublestruck': asciiToDoubleStruck,
        }
    reTable = {
        r'serif-?bold': asciiToSerifBold,
        r'serif-?italic': asciiToSerifItalic,
        r'serif-?bold-?italic': asciiToSerifBoldItalic,
        r'sanserif-?bold': asciiToSanSerifBold,
        r'sanserif-?italic': asciiToSanSerifBold,
        r'(sanserif-?)?(bold-?italic|italic-?bold)': asciiToSanSerifBoldItalic,
        r'(script|cursive)-?bold': asciiToScriptBold,
        r'fraktur-?bold': asciiToFrakturBold,
        }
    if format in strTable:
        return strTable[format](string)
    for pattern in reTable:
        if re.search(pattern, string):
            return reTable[pattern](string)
    return string
