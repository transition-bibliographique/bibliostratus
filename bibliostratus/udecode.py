# coding: utf-8
"""
Ensemble de fonctions ou variables concernant le traitement de l'UTF-8
et les diacritiques, caractères spéciaux, caractères non latins, etc.
"""

# from unidecode_table_full import unidecode_table_full

# coding: utf-8

import html.parser

convert_diacritics = [
    ['ª', 'Á', 'á', 'À', 'à', 'Ă', 'ă', 'Ắ', 'ắ', 'Ằ', 'ằ',
     'Ẵ', 'ẵ', 'Ẳ', 'ẳ', 'Â', 'â', 'Ấ', 'ấ', 'Ầ', 'ầ', 'Ẫ',
     'ẫ', 'Ẩ', 'ẩ', 'Ǎ', 'ǎ', 'Å', 'å', 'Ǻ', 'ǻ', 'Ä', 'ä',
     'Ã', 'ã', 'Ą', 'ą', 'Ā', 'ā', 'Ả', 'ả', 'Ȁ', 'ȁ', 'Ȃ',
     'ȃ', 'Ạ', 'ạ', 'Ặ', 'ặ', 'Ậ', 'ậ', 'Ḁ', 'ḁ', 'Æ', 'æ',
     'Ǽ', 'ǽ', 'ẚ', 'Ⱥ', 'Ḃ', 'ḃ', 'Ḅ', 'ḅ', 'Ḇ', 'ḇ', 'Ć',
     'ć', 'Ĉ', 'ĉ', 'Č', 'č', 'Ċ', 'ċ', 'Ç', 'ç', 'Ḉ', 'ḉ',
     'Ȼ', 'ȼ', 'Ď', 'ď', 'Ḋ', 'ḋ', 'Ḑ', 'ḑ', 'Ḍ', 'ḍ', 'Ḓ',
     'ḓ', 'Ḏ', 'ḏ', 'Đ', 'đ', 'Ð', 'ð', 'Ǳ', 'ǲ', 'ǳ', 'Ǆ',
     'ǅ', 'ǆ', 'É', 'é', 'È', 'è', 'Ĕ', 'ĕ', 'Ê', 'ê', 'Ế',
     'ế', 'Ề', 'ề', 'Ễ', 'ễ', 'Ể', 'ể', 'Ě', 'ě', 'Ë', 'ë',
     'Ẽ', 'ẽ', 'Ė', 'ė', 'Ȩ', 'ȩ', 'Ḝ', 'ḝ', 'Ę', 'ę', 'Ē',
     'ē', 'Ḗ', 'ḗ', 'Ḕ', 'ḕ', 'Ẻ', 'ẻ', 'Ȅ', 'ȅ', 'Ȇ', 'ȇ',
     'Ẹ', 'ẹ', 'Ệ', 'ệ', 'Ḙ', 'ḙ', 'Ḛ', 'ḛ', 'Ḟ', 'ḟ', 'ƒ',
     'Ǵ', 'ǵ', 'Ğ', 'ğ', 'Ĝ', 'ĝ', 'Ġ', 'ġ', 'Ģ', 'ģ', 'Ḡ',
     'ḡ', 'Ĥ', 'ĥ', 'Ḧ', 'ḧ', 'Ḣ', 'ḣ', 'Ḩ', 'ḩ', 'Ḥ', 'ḥ',
     'Ḫ', 'ḫ', 'ẖ', 'Ħ', 'ħ', 'Í', 'í', 'Ì', 'ì', 'Ĭ', 'ĭ',
     'Î', 'î', 'Ǐ', 'ǐ', 'Ï', 'ï', 'Ḯ', 'ḯ', 'Ĩ', 'ĩ', 'İ',
     'Į', 'į', 'Ī', 'ī', 'Ỉ', 'ỉ', 'Ȉ', 'ȉ', 'Ȋ', 'ȋ', 'Ị',
     'ị', 'Ḭ', 'ḭ', 'Ĳ', 'ĳ', 'ı', 'Ĵ', 'ĵ', 'Ḱ', 'ḱ', 'Ķ',
     'ķ', 'Ḳ', 'ḳ', 'Ḵ', 'ḵ', 'Ĺ', 'ĺ', 'Ľ', 'ľ', 'Ļ', 'ļ',
     'Ḷ', 'ḷ', 'Ḹ', 'ḹ', 'Ḽ', 'ḽ', 'Ḻ', 'ḻ', 'Ł', 'ł', 'Ŀ',
     'ŀ', 'Ǉ', 'ǈ', 'ǉ', 'Ƚ', 'Ḿ', 'ḿ', 'Ṁ', 'ṁ', 'Ṃ', 'ṃ',
     'Ń', 'ń', 'Ǹ', 'ǹ', 'Ň', 'ň', 'Ñ', 'ñ', 'Ṅ', 'ṅ', 'Ņ',
     'ņ', 'Ṇ', 'ṇ', 'Ṋ', 'ṋ', 'Ṉ', 'ṉ', 'Ǌ', 'ǋ', 'ǌ', 'º',
     'Ó', 'ó', 'Ò', 'ò', 'Ŏ', 'ŏ', 'Ô', 'ô', 'Ố', 'ố', 'Ồ',
     'ồ', 'Ỗ', 'ỗ', 'Ổ', 'ổ', 'Ǒ', 'ǒ', 'Ö', 'ö', 'Ȫ', 'ȫ',
     'Ő', 'ő', 'Õ', 'õ', 'Ṍ', 'ṍ', 'Ṏ', 'ṏ', 'Ȭ', 'ȭ', 'Ȯ',
     'ȯ', 'Ȱ', 'ȱ', 'Ø', 'ø', 'Ǿ', 'ǿ', 'Ō', 'ō', 'Ṓ', 'ṓ',
     'Ṑ', 'ṑ', 'Ỏ', 'ỏ', 'Ȍ', 'ȍ', 'Ȏ', 'ȏ', 'Ơ', 'ơ', 'Ớ',
     'ớ', 'Ờ', 'ờ', 'Ỡ', 'ỡ', 'Ở', 'ở', 'Ợ', 'ợ', 'Ọ', 'ọ',
     'Ộ', 'ộ', 'Œ', 'œ', 'Ṕ', 'ṕ', 'Ṗ', 'ṗ', 'Ŕ', 'ŕ', 'Ř',
     'ř', 'Ṙ', 'ṙ', 'Ŗ', 'ŗ', 'Ȑ', 'ȑ', 'Ȓ', 'ȓ', 'Ṛ', 'ṛ',
     'Ṝ', 'ṝ', 'Ṟ', 'ṟ', 'Ś', 'ś', 'Ṥ', 'ṥ', 'Ŝ', 'ŝ', 'Š',
     'š', 'Ṧ', 'ṧ', 'Ṡ', 'ṡ', 'Ş', 'ş', 'Ṣ', 'ṣ', 'Ṩ', 'ṩ',
     'Ș', 'ș', 'ſ', 'ẛ', 'ß', 'ẞ', 'ȿ', 'Ť', 'ť', 'ẗ', 'Ṫ',
     'ṫ', 'Ţ', 'ţ', 'Ṭ', 'ṭ', 'Ț', 'ț', 'Ṱ', 'ṱ', 'Ṯ', 'ṯ',
     'Ŧ', 'ŧ', 'Ⱦ', 'Ú', 'ú', 'Ù', 'ù', 'Ŭ', 'ŭ', 'Û', 'û',
     'Ǔ', 'ǔ', 'Ů', 'ů', 'Ü', 'ü', 'Ǘ', 'ǘ', 'Ǜ', 'ǜ', 'Ǚ',
     'ǚ', 'Ǖ', 'ǖ', 'Ű', 'ű', 'Ũ', 'ũ', 'Ṹ', 'ṹ', 'Ų', 'ų',
     'Ū', 'ū', 'Ṻ', 'ṻ', 'Ủ', 'ủ', 'Ȕ', 'ȕ', 'Ȗ', 'ȗ', 'Ư',
     'ư', 'Ứ', 'ứ', 'Ừ', 'ừ', 'Ữ', 'ữ', 'Ử', 'ử', 'Ự', 'ự',
     'Ụ', 'ụ', 'Ṳ', 'ṳ', 'Ṷ', 'ṷ', 'Ṵ', 'ṵ', 'Ṽ', 'ṽ', 'Ṿ',
     'ṿ', 'Ẃ', 'ẃ', 'Ẁ', 'ẁ', 'Ŵ', 'ŵ', 'ẘ', 'Ẅ', 'ẅ', 'Ẇ',
     'ẇ', 'Ẉ', 'ẉ', 'Ẍ', 'ẍ', 'Ẋ', 'ẋ', 'Ý', 'ý', 'Ỳ', 'ỳ',
     'Ŷ', 'ŷ', 'ẙ', 'ÿ', 'Ÿ', 'Ỹ', 'ỹ', 'Ẏ', 'ẏ', 'Ȳ', 'ȳ',
     'Ỷ', 'ỷ', 'Ỵ', 'ỵ', 'Ź', 'ź', 'Ẑ', 'ẑ', 'Ž', 'ž', 'Ż',
     'ż', 'Ẓ', 'ẓ', 'Ẕ', 'ẕ', 'ɀ', 'Þ', 'þ', 'ї', 'і', '᾿Α',
     'ī', 'í', 'ō̃', 'ṓ', 'n', "α"],
    ['a', 'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a',
     'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A',
     'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a',
     'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A',
     'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A', 'a', 'A', 'e',
     'a', 'e', 'A', 'e', 'a', 'e', 'a', 'A', 'B', 'b', 'B',
     'b', 'B', 'b', 'C', 'c', 'C', 'c', 'C', 'c', 'C', 'c',
     'C', 'c', 'C', 'c', 'C', 'c', 'D', 'd', 'D', 'd', 'D',
     'd', 'D', 'd', 'D', 'd', 'D', 'd', 'DZ', 'Dz', 'dz', 'DZ',
     'DZ', 'dz', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E',
     'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E',
     'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E',
     'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E',
     'e', 'E', 'e', 'E', 'e', 'F', 'f', 'f', 'G', 'g', 'G', 'g',
     'G', 'g', 'G', 'g', 'G', 'g', 'G', 'g', 'H', 'h', 'H', 'h',
     'H', 'h', 'H', 'h', 'H', 'h', 'H', 'h', 'h', 'H', 'h', 'I',
     'i', 'I', 'i', 'I', 'i', 'I', 'i', 'I', 'i', 'I', 'i', 'I',
     'i', 'I', 'i', 'I', 'I', 'i', 'I', 'i', 'I', 'i', 'I', 'i',
     'I', 'i', 'I', 'i', 'I', 'i', 'IJ', 'ij', 'i', 'J', 'j', 'K',
     'k', 'K', 'k', 'K', 'k', 'K', 'k', 'L', 'l', 'L', 'l', 'L',
     'l', 'L', 'l', 'L', 'l', 'L', 'l', 'L', 'l', 'L', 'l', 'L',
     'l', 'LJ', 'Lj', 'lj', 'L', 'M', 'm', 'M', 'm', 'M', 'm', 'N',
     'n', 'N', 'n', 'N', 'n', 'N', 'n', 'N', 'n', 'N', 'n', 'N',
     'n', 'N', 'n', 'N', 'n', 'NJ', 'Nj', 'nj', 'o', 'O', 'o', 'O',
     'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O',
     'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O',
     'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O',
     'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O',
     'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O', 'o', 'O',
     'o', 'O', 'o', 'O', 'o', 'OE', 'oe', 'P', 'p', 'P', 'p', 'R',
     'r', 'R', 'r', 'R', 'r', 'R', 'r', 'R', 'r', 'R', 'r', 'R',
     'r', 'R', 'r', 'R', 'r', 'S', 's', 'S', 's', 'S', 's', 'S',
     's', 'S', 's', 'S', 's', 'S', 's', 'S', 's', 'S', 's', 'S',
     's', 's', 's', 'ss', 'Ss', 's', 'T', 't', 't', 'T', 't', 'T',
     't', 'T', 't', 'T', 't', 'T', 't', 'T', 't', 'T', 't', 'T',
     'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u',
     'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u',
     'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u',
     'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u',
     'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u',
     'V', 'v', 'V', 'v', 'W', 'w', 'W', 'w', 'W', 'w', 'w', 'W',
     'w', 'W', 'w', 'W', 'w', 'X', 'x', 'X', 'x', 'Y', 'y', 'Y',
     'y', 'Y', 'y', 'y', 'y', 'Y', 'Y', 'y', 'Y', 'y', 'Y', 'y',
     'Y', 'y', 'Y', 'y', 'Z', 'z', 'Z', 'z', 'Z', 'z', 'Z', 'z',
     'Z', 'z', 'Z', 'z', 'z', 'Th', 'th', 'i', 'i', 'A', 'i', 'i',
     'o', 'o', 'n', "a"]
]



def udecode(string):
    for el in string:
        try:
            i = convert_diacritics[0].index(el)
            string = string.replace(el, convert_diacritics[1][i])
        except ValueError:
            pass
    return string
