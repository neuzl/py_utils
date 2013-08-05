# -*- coding: utf-8 -*-
"""
A collection of string related tools.
In order to keep innocence with the system module, a prefix 'ab' is added.
@change log
    api dedup_con_str:add bufeng 2009-10-15
       duplicated concatenated string
       设计用来去除点评中的连续垃圾点评
"""
import os
import re
#from umg.util.abwords import ABWORDS

# global regexs
ncr_pattern = re.compile("&#[0-9]+;|&#[xX][0-9a-fA-F]+;")
par_pattern = re.compile("\([^)]*\)|（[^）]*）")
esc_pattern = re.compile("&[a-zA-Z0-9]+;$")
u_punctuations = "。？！，、；／.?!,;`/".decode('utf-8')
end_punctuations = ['.', u'\u3002', '?', u'\uff1f', '!', u'\uff01']

# GBK1/2 ranges: (high_byte, low_byte) 
gbk1_range = (('\xA1', '\xA9'), ('\xA0', '\xFE')) 
gbk2_range = (('\xB0', '\xF7'), ('\xA1', '\xFE')) 

# init abwords
#dictList = []
#dictList.append(os.environ['UMGDATA_HOME'] + '/dict/Aibang_basicDict.txt')
#dictList.append(os.environ['UMGDATA_HOME'] + '/dict/Aibang_groupDict.txt')
#wordparser = ABWORDS(dictList)

#------------------------------------------#
# Convert characters to Unicode before use #
#------------------------------------------#
def is_chinese(uchar):
    '''
    is uchar(unicode) a chinese character
    '''
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

def is_number(uchar):
    '''
    is uchar a number
    '''
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False

def is_alphabet(uchar):
    '''
    is uchar a alphabet
    '''
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or \
            (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False

def is_japanese(uchar):
    '''
    is uchar a japanese
    '''
    if (uchar >= u'\u3040' and uchar <= u'\u30FF'): 
        return True
    else:
        return False

def is_other(uchar):
    '''
    is uchar a character other than chinese character, number or alphabet
    '''
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False

def char2SBC(uchar):
    '''
    transfer DBC case to SBC case
    '''
    inside_code = ord(uchar)
    # if uchar is not DBC case, return it without change
    if inside_code < 0x0020 or inside_code > 0x7e:  
        return uchar
    # transfer formula: SBC = DBC + 0xfee0, except space
    if inside_code == 0x0020:   
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return unichr(inside_code)

def char2DBC(uchar):
    '''
    transfer SBC case to DBC case
    '''
    inside_code = ord(uchar)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:   
        return uchar
    return unichr(inside_code)

def str2DBC(ustring):
    '''
    transfer a string to DBC case
    '''
    return "".join([ char2DBC(uchar) for uchar in ustring ])

def strUniform(ustring):
    '''
    uniform a string, transfer it to DBC case and lower case 
    '''
    return str2DBC(ustring).lower()

def str2List(ustring):
    '''
    separate a string into chinese chars, numbers and alphabets
    '''
    retList = []
    utmp = []
    for uchar in ustring:
        if is_other(uchar):
            if len(utmp) == 0:
                continue
            else:
                retList.append("".join(utmp))
                utmp = []
        else:
            utmp.append(uchar)
    if len(utmp) != 0:
        retList.append("".join(utmp))
    return retList

def convert_spaces(a_string, in_coding='utf-8', out_coding='utf-8'):
    '''
    convert SBC spaces to DBC spaces for a specified string  
    '''
    u_src = a_string.decode(in_coding, 'ignore')
    u_blank = "　".decode('utf-8')
    u_des = u_src.replace(u_blank, " ")
    return u_des.encode(out_coding, 'ignore')

#-------------------------------------------------#
# Transfer numeric character references to utf-8  #
#-------------------------------------------------#
def str2utf(a_string):
    '''
    transfer numeric character references(NCR) to utf-8,
    there are two syntaxs for NCR:
     1) "&#D;", where D is a decimal number, refers to the ISO 10646 
        decimal character number D.
     2) "&#xH;" or "&#XH;", where H is a hexadecimal number, refers to 
        the ISO 10646 hexadecimal character number H. Hexadecimal numbers 
        in numeric character references are case-insensitive.
    '''
    result = ""
    last_m_end = 0

    m_iterator = ncr_pattern.finditer(a_string)
    for m in m_iterator:
        curr_m_begin = m.start()
        curr_m_end = m.end()
        unchanged_begin = last_m_end
        unchanged_end = curr_m_begin
        last_m_end = curr_m_end

        m_string = a_string[curr_m_begin : curr_m_end]
        # the hexadecimal pattern
        if m_string.startswith('&#x') or m_string.startswith('&#X'):
            hexcode = m_string[3 :-1]
        # the decimal pattern
        else:
            hexcode = hex(int(m_string[2:-1]))[2:]
        if len(hexcode) < 4:
            hexcode = '0'*(4 - int(len(hexcode))) + hexcode

        # decode utf-8 string, and joint with unicode string 
        result += a_string[unchanged_begin : unchanged_end].decode('utf-8', 'ignore') + \
                  ("\\u%s" % hexcode).decode("unicode_escape")

    # unicode result
    result += a_string[last_m_end:].decode('utf-8', 'ignore')
    # utf-8 result
    result = result.encode('utf-8', 'ignore')
    # replace \r\n with whitespace
    for c in ['\r', '\n']:
        result = result.replace(c, ' ')
    return result

def dedup(string_list):
    '''
    dedup a list of strings
    '''
    results = []
    bag = set()
    for a_string in string_list:
        if a_string not in bag:
            results.append(a_string)
            bag.add(a_string)
    return results

#----------------------------------#
# longest common string            #
#----------------------------------#
def lcs(left, right):
    """
    longest common string
    dynamic programming
    if without lcs, return empty string
    """
    (left_len, right_len, left_lcspos, lcs_len) = (len(left), len(right), 0, 0)
    matrix = []
    for row in xrange(left_len + 1):
        matrix.append([0] * (right_len + 1))

    for row in range(0, left_len):
        for col in range(0, right_len):
            if left[row] == right[col]:
                matrix[row + 1][col + 1] = matrix[row][col] + 1
                if matrix[row + 1][col + 1] > lcs_len:
                    lcs_len = matrix[row + 1][col + 1]
                    left_lcspos = row + 1 - lcs_len
            else:
                matrix[row][col] = 0  
      
    return left[left_lcspos:left_lcspos + lcs_len]

#----------------------------------#
# String edit distance/similarity  #
#----------------------------------#
def levenshtein(a, b):
    '''
    edit distance/levenshtein distance between a and b
    '''
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n

    current = range(n+1)
    for i in range(1, m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1, n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 2
            current[j] = min(add, delete, change)
    return current[n]

def similarity(a, b):
    '''
    similarity between a and b
    '''
    t = len(a) + len(b)
    if t == 0:
        return 0.0
    mx = max(len(a), len(b))
    mn = min(len(a), len(b))
    ld = levenshtein(a, b)
    return float(t - ld) / float(t)

def clear_parentheses(a_string):
    '''
    clear the contents surrounded by parentheses (including parentheses)
    * GBK only *
    '''
    return par_pattern.sub('', a_string)

def clear_punctuations(a_string, encoding='utf-8', include='', exclude=''):
    '''
    convert breaking punctuations (both DBC and SBC) into spaces
    '''
    result = ""
    ustring = a_string.decode(encoding, 'ignore')
    u_include = include.decode(encoding, 'ignore')
    u_exclude = exclude.decode(encoding, 'ignore')
    #dbc_ustring = str2DBC(ustring)
    #for char in dbc_ustring:
    index = 0
    for char in ustring:
        if char == ';':
            # look ahead for 12 chars, detect whether it's a html escape string
            end = index + 1
            start = index - 11
            start = start >= 0 and start or 0
            look_ahead = ustring[start : end] 
            if esc_pattern.search(look_ahead):
                result += char
            else:
                result += ' '
        elif char not in u_exclude and \
            (char in u_punctuations or char in u_include):
            result += ' '
        else:
            result += char
        index += 1
    result = result.encode(encoding, 'ignore')
    return result.strip()

def detect_messy_code(a_string, threshold=20):
    '''
    detect whether there exists messy codes in a given string,
    if there are more than THRESHOLD continuous individual words after segmentation, 
    it will be considered as messy code.
    '''
    #seg_list = wordparser.seg(a_string)
    '''
    modify by linZhang 2010-05-12
    '''
    seg_list =None
    seg_len = len(seg_list)
    count = 0
    for i in xrange(0, seg_len):
        word = seg_list[i].word
        if len(word) == 2:
            count += 1
            if count >= threshold:
                break
        else:
            count = 0
    if count >= threshold:
        return True
    else:
        return False

def load_tradi_dict():
    '''
    load traditional to simplified dict
    '''
    umgdata_home = os.environ['UMGDATA_HOME']
    dict_file = os.path.join(umgdata_home, 'conf/traditional_zh_cn')
    tradi_dict = {}

    dict_fd = open(dict_file)
    line_index = 0
    upper_list = None
    lower_list = None
    for line in dict_fd:
        if line_index > 1:
            line_index = 0
            upper_list = []
            lower_list = []
            continue
        line = line.strip()
        u_line = line.decode('utf-8')
        # generate upper list
        if line_index == 0:
            upper_list = [ u.encode('utf-8') for u in u_line ]
        # generate lower list and get mapping
        elif line_index == 1:
            lower_list = [ u.encode('utf-8') for u in u_line ]
            assert(len(upper_list) == len(lower_list))
            length = len(upper_list)
            for i in xrange(length):
                tradi_word = upper_list[i]
                simp_word = lower_list[i]
                if tradi_word == simp_word:
                    continue
                if tradi_word in tradi_dict:
                    if simp_word != tradi_dict[tradi_word]:
                        print "dup simp_word for %s: [%s] [%s]" % (tradi_word, simp_word, tradi_dict[tradi_word])
                else:
                    tradi_dict[tradi_word] = simp_word
        else:
            pass
        line_index += 1
    dict_fd.close()
    return tradi_dict

#load traditional mapping dict
tradi_dict = load_tradi_dict()

def tradi2simp(a_string):
    '''
    convert traditional chinese to simplified chinese 
    '''
    result = ''
    u_string = a_string.decode('utf-8', 'ignore')
    for u_word in u_string:
        utf_word = u_word.encode('utf-8', 'ignore')
        if utf_word in tradi_dict:
            simp_word = tradi_dict[utf_word]
        else:
            simp_word = utf_word
        result += simp_word
    return result

def is_common_word(u_word):
    '''
    is the u_word a common word (fall in the gbk2 range)
    '''
    gbk_word = u_word.encode('gbk')
    if gbk_word[0] >= gbk2_range[0][0] and gbk_word[0] <= gbk2_range[0][1] and \
            gbk_word[1] >= gbk2_range[1][0] and gbk_word[1] <= gbk2_range[1][1]: 
        return True
    else:
        return False

def limit_length(a_string, length):
    '''
    limit the a_string length, return new string, the limit place is the last end punctuation before length, include chinese and english end punctuation
    '''
    u_string = a_string.decode('utf-8', 'ignore')
    sum = 0
    end_place = 0
    char_index = 0
    if len(u_string) <= length:
        return a_string
    else:
        new_result = ''
        for i in u_string:
            if sum >= length:
                if i in end_punctuations:
                    new_result = u_string[:end_place]
                elif end_place > 0:
                    new_result = u_string[:end_place+1]
                else:
                    new_result = u_string[:char_index]
                break
            if i in end_punctuations:
                end_place = char_index
            char_index += 1
            sum += 1
        new_result = new_result.encode('utf-8', 'ignore')
        return new_result

def dedup_con_str(a_string, encoding='utf-8'):
    """
    该函数一个使用场景:去除同一个点评中的连续重复部分,来获取点评中的有效信息
    example
    pre:这个餐馆真难吃真难吃这个餐馆真难吃真难吃
    post:这个餐馆真难吃
    该函数算法要作多次循环,效率不高        
    """
    pre_string = a_string             
    while True:
        post_string = _dedup_con_str_loop(pre_string, encoding)
        if post_string == pre_string:
            break
        else:
            pre_string = post_string
    return post_string

def _dedup_con_str_loop(a_string, encoding = 'utf-8'):    
    """dedup_con_str 子函数"""
    u_string = a_string.decode(encoding, 'ignore')
    u_string_len = len(u_string)    
    u_list = []
    i = 0
    while i < u_string_len:
        #find maxcover
        (max_cover, max_cover_step) = (1, 1)
        step = 1
        while step <= (u_string_len - i) / 2:
            cover = 0
            if u_string[i:i + step] == u_string[i + step:i + 2 * step]:
                cover += 2 * step               
                for j in range(i + 2 * step, u_string_len - step + 1, step):
                    if u_string[i:i + step] == u_string[j:j + step]:
                        cover += step
                    else:
                        break
            if cover > max_cover:
                (max_cover, max_cover_step) = (cover, step)                
            step += 1
        #add cluster                    
        cluster_list = []
        for j in range(i, i + max_cover, max_cover_step):
            cluster_list.append(u_string[i:i + max_cover_step])
        u_list.append(cluster_list)
        #loop        
        i += max_cover
    dedup_u_list = []
    for i in range(0, len(u_list)):
        dedup_u_list.append(u_list[i][0])
    return ''.join(dedup_u_list).encode(encoding, 'ignore') 

if __name__ == '__main__':
     print similarity('1223', '1234')

