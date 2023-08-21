import os
import re
import json

from collections import Counter
from util import *
from glob import glob
from category_101 import get_EXP
from utilCapacity import get_capacity

LIMIT_NUM = 20
Brand_list_1 = [i.strip() for i in set(open("Labels/327_brand_list_1",encoding="utf-8").readlines())]
Brand_list_2 = [i.strip() for i in set(open("Labels/327_brand_list_2",encoding="utf-8").readlines())]
Type_list = [i.strip() for i in set(open("Labels/327_type_list",encoding="utf-8").readlines())]
English_list = [i.strip() for i in open("Labels/327_English_list",encoding="utf-8").readlines()]
state_list = [i.strip() for i in open("Labels/327_state_list",encoding="utf-8").readlines()]
effect_list = [i.strip() for i in open("Labels/327_effect_list",encoding="utf-8").readlines()]

Spacial_productname = []
Wort_concentration = ["6","7"]

def get_type(texts_list,product_name):
    type_jiemaogao = ["睫毛膏","睫毛底膏","睫毛打底膏","美睫定型乳","睫毛液","睫毛定型液","睫毛凝露","睫毛营养液等"]
    type_yanying = ["眼影","眼影膏","眼影粉","眼影棒","眼影盘","眼影啫喱","眼影笔","眼部闪粉","卧蚕笔","眼颊彩盘"]
    type_yanxian = ["眼线液","眼线笔","眼线啫喱","眼线膏","眼线胶笔","眼线水笔","眼妆笔"]
    type_meibi = ["眉笔","眉影笔","眉彩笔","眉粉笔","眉蜡笔","眉毛修饰液","眉造型笔"]
    type_runsechungao = ["润唇膏","润色润唇膏"]
    type_chungao = ["口红","唇膏","唇膏笔","唇棒","唇宝","唇霜","唇笔","染唇棒"]
    type_chuncai= ["唇蜜","唇彩","唇蜜乳","唇露","非膏状雨衣","唇漆","唇乳","唇泥","唇部精华蜜"]
    type_yetichungao = ["液体唇膏","液体口红"]
    type_ranchun = ["染唇","染唇液","染唇笔","染唇彩"]
    type_zhijiayou = ["甲油","指甲油","指彩","指甲底油","甲彩","微胶","指釉","指彩蜜"]
    type_zhijiaxiuhu = ["护理油","护甲底油","指缘精华","指缘油","护甲啫喱","甲缘油笔"]
    type_xijiashui = ["卸甲","洗甲","除光液","洁净液","清洁液"]
    type_fendiye = ["粉底液","粉底乳","粉底蜜","水粉霜","高光液","调色霜"]
    type_fendishuang = ["气垫水粉霜","粉底霜","气垫霜","粉凝霜","修容霜","底霜","粉底乳霜","凝霜粉底","粉底膏","轻垫霜"]
    type_liangyongfenbing = ["两用粉饼","干湿粉","干湿两用粉底","双效粉饼","两用蜜粉饼"]
    type_shifenbing = ["气垫湿粉","湿粉膏","湿粉","水粉饼","精华粉"]
    type_yibanfenbing = ["粉饼","修颜饼"]
    type_zhexiagao = ["遮瑕膏","遮瑕液","遮瑕霜","蓋斑膏","遮瑕笔","苹果光笔","毛孔隐形笔","去瑕棒","遮盖霜","无暇粉霜","粉霜"]
    type_fentiao = ["粉条","筒状粉膏","粉妆条","粉底条","粉底棒","粉妆棒"]
    type_mosifensi = ["摩丝粉底","摩司粉底","慕司粉底","慕丝粉底"]
    type_ganfenbing = ["干粉饼","蜜粉饼","定妆粉饼","粉膏"]
    type_sanfen = ["散粉","蜜粉","粉球","高光粉","细肤粉","定妆粉","香粉","BB粉","CC粉"]
    type_shanfen = ["闪粉","提亮粉","亮彩粉"]
    type_saihong = ["腮红","胭脂","颊彩霜","颊彩液","颊彩粉"]
    type_zhaungqiangeli = ["妆前","修颜","修容","粉底隔离液","隔离","饰底乳","美颜霜","修颜隔离素颜霜","妆前隔离乳"]
    type_otherBB = ["白白霜","裸妆霜","皙皙霜","TT霜","BB+CC霜","BB+DD霜","CC+DD霜","EE","AA","CB"]
    type_dingzhuangpenwu = ["定妆喷雾","持妆喷雾","锁妆喷雾","定妆水"]
    type_dandufenlei = ["唇釉","红唇素","唇线笔"]
    type_ranmeigao = ["眉膏"]

    pattern_1 = "("
    for i in Type_list:
        pattern_1 += i + "|"
    pattern_1 = pattern_1[:-1] + ")"
    p_res = get_info_by_pattern(product_name,pattern_1)
    if len(p_res) > 0:
        if p_res[0] in type_jiemaogao:
            return "睫毛膏"
        elif p_res[0] in type_yanying:
            return "眼影"
        elif p_res[0] in type_yanxian:
            return "眼线"
        elif p_res[0] in type_meibi:
            return "眉笔"
        elif p_res[0] in type_runsechungao:
            return "润色唇膏"
        elif p_res[0] in type_chungao:
            return "唇膏"
        elif p_res[0] in type_chuncai:
            return "唇彩"
        elif p_res[0] in type_yetichungao:
            return "液体唇膏"
        elif p_res[0] in type_ranchun:
            return "染唇"
        elif p_res[0] in type_zhijiayou:
            return "指甲油"
        elif p_res[0] in type_zhijiaxiuhu:
            return "指甲修护产品"
        elif p_res[0] in type_xijiashui:
            return "洗甲水"
        elif p_res[0] in type_fendiye:
            return "粉底液"
        elif p_res[0] in type_fendishuang:
            return "粉底霜"
        elif p_res[0] in type_liangyongfenbing:
            return "两用粉饼"
        elif p_res[0] in type_shifenbing:
            return "湿粉饼"
        elif p_res[0] in type_yibanfenbing:
            return "一般粉饼"
        elif p_res[0] in type_zhexiagao:
            return "遮瑕膏/修正液"
        elif p_res[0] in type_fentiao:
            return "粉条"
        elif p_res[0] in type_mosifensi:
            return "摩丝粉底"
        elif p_res[0] in type_ganfenbing:
            return "干/蜜粉饼"
        elif p_res[0] in type_sanfen:
            return "散粉/蜜粉"
        elif p_res[0] in type_shanfen:
            return "闪粉"
        elif p_res[0] in type_saihong:
            return "腮红"
        elif p_res[0] in type_zhaungqiangeli:
            return "妆前隔离霜/防护霜"
        elif p_res[0] in type_otherBB:
            return "其他BB霜"
        elif p_res[0] in type_dingzhuangpenwu:
            return "定妆喷雾"
        elif "BB" in product_name:
            return "BB霜"
        elif "CC" in product_name:
            return "CC霜"
        elif "DD" in product_name:
            return "DD霜"
        elif p_res[0] in type_dandufenlei:
            return p_res[0]
        elif p_res[0] in type_ranmeigao:
            return "染眉膏"

    return "不分"

def get_SPF(texts_list):
    pattern = "(SPF\w+PA)$"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    pattern = "SPF\w+"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_effect(product_name,texts_list):
    #妆效
    if "睫毛膏" in product_name:
        key_jiachang = ["长","延","纤远","神纤","纤维","纤绒","纤长"]
        key_nongmi = ["密","丰","丰盈","浓色"]
        key_fenming = ["精密","分明"]
        key_juanqiao = ["卷","曲","翘","立体","高感"]
        key_ziyang = ["养","滋养"]

        result_zhuangxiao = []

        pattern = "长|延|纤[远维绒长]|神纤|密|丰?盈|浓色|精密|分明|卷|曲|翘|立体|高感|滋?养"
        for texts in texts_list:
            for text in texts:
                p_res = get_info_by_pattern(text, pattern)
                if p_res[0] in key_jiachang:
                    result_zhuangxiao.append(p_res[0])
                if p_res[0] in key_nongmi:
                    result_zhuangxiao.append(p_res[0])
                if p_res[0] in key_fenming:
                    result_zhuangxiao.append(p_res[0])
                if p_res[0] in key_juanqiao:
                    result_zhuangxiao.append(p_res[0])
                if p_res[0] in key_ziyang:
                    result_zhuangxiao.append(p_res[0])
                if len(result_zhuangxiao) > 2:
                    return "多用途"
                elif p_res[0] in key_jiachang:
                    return "加长"
                elif p_res[0] in key_nongmi:
                    return "浓密"
                elif p_res[0] in key_fenming:
                    return "分明"
                elif p_res[0] in key_juanqiao:
                    return "卷翘"
                elif p_res[0] in key_ziyang:
                    return "滋养"
                else:
                    return "普通"

        else:
            key_ziran = ["透","自然","纯[粹净]","清纯","裸[肌妆]?","素颜"]
            key_shanliang = ["闪","璀璨","亮[彩采]","晶[莹亮透钻晶]?","莹[彩肌亮]","[炫提明闪]?亮","光[影感亮]","[感高柔水鎏珠]光","柔晶","丝缎"]
            key_yaguang = ["[哑亚]光?","雾[感面]","[柔迷]?雾"]
            key_chijiu = ["防脱","[脱褪]色","抗汗","防御","长[效久]","持久","恒[妆采]?"]

            pattern = "透|自然|纯[粹净]|清纯|裸[肌妆]?|素颜|璀璨|亮[彩采]|晶[莹亮透钻晶]?|莹[彩肌亮]|[炫提明闪]?亮|光[影感亮]|[感高柔水鎏珠]光|柔晶|丝缎|闪|[哑亚]光?|雾[感面]|[柔迷]?雾|" \
                      "防脱|[脱褪]色|抗汗|防御|长[效久]|持久|恒[妆采]?"
            for texts in texts_list:
                for text in texts:
                    p_res = get_info_by_pattern(text, pattern)
                    if p_res[0] in key_ziran:
                        return "自然"
                    elif p_res[0] in key_shanliang:
                        return "闪亮"
                    elif p_res[0] in key_yaguang:
                        return "哑光"
                    elif p_res[0] in key_chijiu:
                        return "持久"
                    else:
                        return "其它"

    return "其它"

def get_state(texts_list,product_name):
    key_gaozhuang = ["口红","唇泥","粉霜"]
    key_luruye = ["露","液","汁","唇彩","粉底液","眼线液","眼线液笔","眼线水笔","液体眼线笔","唇釉","唇露","果冻唇泥","雪糕唇泥","唇蜜"]
    key_zheli = ["凝露","水晶","嗜喱","冰露","晶露","凝","胶","去死皮","去角质","凝脂","凝膜","冻膜","眼线胶","眼线膏"]
    key_mosi = ["摩丝","慕丝","慕司","泡沫","慕斯粉底"]
    key_fenzhuang = ["粉饼","粉末","蜜粉","散粉","眉粉","眼颊彩盘","腮红","眼影盘","眼影","腮红"]
    key_bi = ["笔芯","眼线"]
    key_other = ["睫毛膏","睫毛液"]

    pattern = "("
    for i in state_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res)>0:
        if "油" in product_name  or "水甲彩" in product_name or "指甲修护产品" in product_name:
            return '油状'
        elif p_res[0] in key_other:
            return "其它"
        elif p_res[0] in key_bi or "笔" in product_name:
            return "笔"
        elif "条" in product_name or "棒" in product_name or "皂" in product_name:
            return "条、棒状"
        elif p_res[0] in key_gaozhuang or "膏" in product_name or "霜" in product_name or "脂" in product_name:
            return "膏状"
        elif p_res[0] in key_zheli:
            return "啫喱"
        elif p_res[0] in key_mosi or "慕斯" in product_name:
            return "摩丝"
        elif p_res[0] in key_luruye or "乳" in product_name or "蜜" in product_name or "液" in product_name or "露" in product_name or "奶" in product_name or "汁" in product_name:
            return "露、乳、液"
        elif p_res[0] in key_fenzhuang or "粉" in product_name:
            return "粉状"
        elif "喷雾" in product_name or "水" in product_name:
            return "水"

    return "其它"

def get_NA_1(texts_list):

    return "不分"

def get_NA_2(texts_list):

    return "不分"

def get_waterproof(texts_list,product_name):
    '''
    1.防水：包装上出现“防水”无“气垫”
    2.不防水：包装上无“防水”无“气垫”
    3.防水，气垫：包装上出现“防水”和“气垫”以及“网格粉凝霜”的产品
    4.不防水，气垫：包装上无“防水”和出现“气垫”以及“网格粉凝霜”的产品
    5.防水，BB：包装上出现“防水”无“气垫”，全称有“BB”字样，并且子品类Sub-category不是“BB霜”、“CC霜”、“DD霜”、“其他BB霜”
    6.不防水，BB：包装上无“防水”无“气垫”，全称有“BB”字样，并且子品类Sub-category不是“BB霜”、“CC霜”、“DD霜”、“其他BB霜”
    7.防水，气垫，BB：包装上出现“防水”和“气垫”以及“网格粉凝霜”的产品，全称有“BB”字样，并且子品类Sub-category不是“BB霜”、“CC霜”、“DD霜”、“其他BB霜”
    8.不防水，气垫，BB：包装上无“防水”和出现“气垫”以及“网格粉凝霜”的产品，全称有“BB”字样，并且子品类Sub-category不是“BB霜”、“CC霜”、“DD霜”、“其他BB霜”
    :param texts_list:
    :return:
    '''

    pattern = "防水|气垫|BB"
    p_res = get_info_by_pattern(product_name, pattern)
    if len(p_res) > 0 and "防水" not in p_res:
        delim = ','
        content = delim.join(p_res)
        return str("不防水,")+ content
    elif len(p_res) > 0 and "防水" in p_res:
        delim = ','
        content = delim.join(p_res)
        return content

    return "不防水"

def get_crowd(texts_list):
    pattern0 = '(儿童|男士|婴幼?儿|幼儿|婴童|宝宝|baby|BABY|MAN)'
    pattern = '适用人群' + pattern0
    pattern1 = '适合\w*' + pattern0
    pattern2 = r'专为' + pattern0 + '研制配方'
    pattern3 = "男士"
    for texts in texts_list:
        text_origi = ''.join(texts)
        p_res = get_info_by_pattern(text_origi, pattern)
        if len(p_res) > 0:
            result = p_res[0]
            if result == '婴儿' or result == '宝宝' or result == '婴童' or result == 'BABY' or result == 'baby' or result == '儿童':
                return '儿童'
            return result
        else:
            p_res = get_info_by_pattern(text_origi, pattern1)
            if len(p_res) > 0:
                result = p_res[0]
                if result == '婴儿' or result == '宝宝' or result == '婴童' or result == 'BABY' or result == 'baby' or result == '儿童':
                    return '儿童'
                return result
            else:
                p_res = get_info_by_pattern(text_origi, pattern2)
                if len(p_res) > 0:
                    result = p_res[0]
                    if result == '婴儿' or result == '婴童' or result == 'BABY' or result == 'baby' or result == '宝宝' or result == '儿童':
                        return '儿童'
                    return result
                else:
                    p_res = get_info_by_pattern(text_origi, pattern3)
                    if len(p_res) > 0:
                        return "男性"
    return '不分'

# 提取英文全称
def get_English_Name(texts_list):
    '''
    英文全称
    提取思路：
    :param texts_list: 有序文本列表
    '''

    pattern = "([A-Z-\s]+)"
    #眉笔、睫毛膏、润唇膏、唇釉、BB霜、粉底液、散粉、隔离乳、眼线笔、指甲油、定妆喷雾、眼影、粉底霜、腮红、唇膏、妆前乳、遮瑕膏、CC霜、唇彩（蜜）、唇泥、无暇膏、眉膏、妆前膏、EE霜、气垫霜、指甲油
    list_key = ['EYEBROWPENCIL','MASCARA', 'mascara', 'WATERTINT','LIPBALM', 'LipBalm','LIPGLAZE', 'BBCREAM', 'FOUNDATION', 'POWDER', 'RADIANCEPRIMER','EYELINER' ,'LIUQIDEYELINER', 'NAILPOLISH', 'MAKEUPSETTINGSPRAY', 'EYESHADOW',
                'CREAMFOUNDATION', 'BLUSH','LIPSTICK', 'PRIMER', 'CONCEALER',' cccream','LIPGLOSS','LIPMUD','FLAWLESSCREAM','BROWPOMADE','PRIMERCREAM','EECREAM','CUSHION',"NAILPOLSH","BETTERTHANCHEEK","LipMirror","LipLacquer"]
    result_list =[]
    for text_list in texts_list:
        txt_orig = ' '.join(text_list).upper().strip()
        if len(txt_orig)>10:
            # 1、首先把英文字符串分离出来
            p_res = get_info_by_pattern(txt_orig, pattern)
            if len(p_res) > 0:
                for title in p_res:
                    # 2、排除长度小于10英文串
                    if len(title) > 10:
                        words_list = []
                        words = title
                        flag = False
                        for it in list_key:
                            if it in words:
                                flag = True
                                break
                        if flag:
                            # 3、把在英文字符串中出现的单词按照先后顺序存储在列表中，最后用空格链接起来就是英文全称
                            if len(English_list)>0:
                                for it in English_list:
                                    if it in words :
                                        words = words.replace(it, '*')
                                        if len(words_list) ==0 :
                                            words_list.append(it)
                                        else:
                                            flag = True
                                            # 根据单词的先后顺序存在列表中
                                            for index, tt in enumerate(words_list):
                                                if title.find(it) < title.find(tt):
                                                    words_list.insert(index, it)
                                                    flag = False
                                                    break
                                            if flag:
                                                words_list.append(it)
                                        temp = words.replace('*', '')
                                        # 如果都找到并且替换完了，结束循环
                                        if len(temp) == 0:
                                            break
                            else:
                                words_list.append(title)
                            if len(words_list)>0:
                                result = ' '.join(words_list)
                                result_list.append(result)
    if len(result_list)>0:
        result_list.sort(key=len, reverse=True)
        return result_list[0]
    return '不分'

def get_productName(kvs_list,texts_list):
    result_list = []
    result_list_tmp = []

    pattern_absort = "^[Q活正管华三不体]|豆沙色|流瑕|滋润"
    pattern_text = "[、，,]|公司"
    pattern_1 = "(\w+眉笔|\w+散粉|\w+高光粉|\w+睫?毛打?底?膏|\w+遮瑕[膏液]|\w+隔离[乳霜露]|\w+气垫霜|\w+素颜霜|\w+粉[霜膏饼]|\w+妆前[乳霜]|\w+调色霜|\w+[A-Z]{2,2}霜|\w+粉底液|\w+修容粉|\w+眼线[液胶]?笔|\w+眼影[笔盘]?|\w+指甲油" \
                "|\w+唇[露膏釉液泥蜜育]笔?|\w+水甲彩|\w+定妆喷雾|\w+定妆散粉|\w+眼颊彩盘|\w+修颜棒|\w+蜜粉饼|\w+精华蜜|\w+[腮口]红)$"
    pattern_2 = "(\w+眉笔|\w+散粉|\w+高光粉|\w+睫毛打?底?膏|\w+遮瑕[膏液]|\w+隔离[乳霜露]|\w+气垫霜|\w+素颜霜|\w+粉[霜膏]|\w+妆前[乳霜]|\w+调色霜|\w+[A-Z]{2,2}霜|\w+粉底液|\w+修容粉|\w+眼线[液胶]?笔|\w+眼影[笔盘]?|\w+指甲油" \
                "|\w+唇[露膏釉液泥蜜]笔?|\w+水甲彩|\w+定妆喷雾|\w+定妆散粉|\w+眼颊彩盘|\w+修颜棒|\w+蜜粉饼|\w+精华蜜|\w*腮红|\w+[腮口]红)"
    pattern_3 = "(\w*[A-Z]{2,2}霜)"

    pattern_tmp = "[笔粉膏液乳霜影油彩盘棒饼蜜]|唇[膏釉液泥蜜]笔?|[腮口]红"
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                if ("品名" in k or k in ["名称", "名"]):
                    if len(kv[k]) > 1 and len(re.compile(pattern_tmp).findall(kv[k])) > 0:
                        result_list.append(kv[k])
                    else:
                        result_list_tmp.append(kv[k])

    if len(result_list_tmp) == 0:
        product_name_tmp = "不分"
    else:
        count = Counter(result_list_tmp).most_common(2)
        product_name_tmp = count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_2)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        count = Counter(result_list).most_common(2)
        return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                if len(re.compile(pattern_text).findall(text)) == 0 and len(re.compile(pattern_absort).findall(p_res[0])) == 0:
                    result_list.append(p_res[0])

    if len(result_list) > 0:
        return product_name_tmp
        count = Counter(result_list).most_common(2)
        return count[0][0]

    return "不分"

def get_suitPosition(texts_list,product_name):
    pattern = "身体|隔离露"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(product_name, pattern)
            if len(p_res) > 0:
                return "身体"

    pattern = "眉[笔膏]|[睫糖]毛打?底?膏|眼线液?笔|眼颊彩盘|眼线胶笔|眼影盘?"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(product_name, pattern)
            if len(p_res) > 0:
                return "眼部"

    pattern = "[散蜜]粉|高光粉|调色霜|隔离[乳霜]|粉底[液霜量]|定妆喷雾|[A-Z]{2,2}霜|修颜棒|腮红|遮瑕[膏液]|妆前[乳霜]|气垫霜|精华[粉蜜]|修容粉|素颜霜|粉[饼霜膏]|妆前霜"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(product_name, pattern)
            if len(p_res) > 0:
                return "面部"

    pattern = "指甲油|水甲彩|油笔|甲油"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(product_name, pattern)
            if len(p_res) > 0:
                return "手部"

    pattern = "唇[露膏釉膏泥蜜]笔?|口红"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(product_name, pattern)
            if len(p_res) > 0:
                return "唇部"

    return "不分"

def get_cover(texts_list):
    key_wuxia = ["无[瑕痕]","遮[瑕盖]","修颜"]
    key_qingtou = ["透","轻","薄","透[明薄光气薄氧肌妆]","[莹轻盈清]透","呼吸","轻[盈柔]""薄纱","丝薄"]

    result_wuxia = []
    result_qingtou = []

    pattern = "无[瑕痕]|遮[瑕盖]|修颜|透|轻|薄|透[明薄光气薄氧肌妆]|[莹轻盈清]透|呼吸|轻[盈柔]|薄纱|丝薄"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text,pattern)
            if len(p_res) > 0:
                if p_res[0] in key_wuxia:
                    result_wuxia.append("无暇")
                if p_res[0] in key_qingtou:
                    result_qingtou.append("轻透")

        if len(result_wuxia) > 0 and len(result_qingtou) > 0:
            count_wuxia = Counter(result_wuxia).most_common(2)
            count_qingtou = Counter(result_qingtou).most_common(2)
            return count_wuxia[0][0] + "," + count_qingtou[0][0]
        elif len(result_wuxia) > 0:
            count_wuxia = Counter(result_wuxia).most_common(2)
            return count_wuxia[0][0]
        elif len(result_qingtou) > 0:
            count_qingtou = Counter(result_qingtou).most_common(2)
            return count_qingtou[0][0]

    return "其它"

def get_effect_result(texts_list):

    key_baoshi = ["水","润","湿","补[保湿水]","水[润嫩凝分亮感活份养库滢漾纯透焕弹盈缘能衡]","水动力","水呼吸","[凝锁饱保]水","水循环","水活能","[深极沁莹恒丰湿滢盈滋清柔丝营特倍]润",
                  "[清润]泽","[防抗]干","透明质酸","玻尿酸","WATER","水动能","滋养","柔[滑和]","[柔润]肤","养护","SOD"]
    key_meibai = ["白","雪","皙","亮","[去祛褪消抗]黑","黑色素","去黄","VC","维他命C","维C","维生素C","玉肤","冰肌","牛奶"]
    key_kongyou = ["疮","痘","[控抑去吸净抗防水无]油","[去吸清净油皮]脂","清透","净化","油光","净透","毛孔","细孔","黑头","细肤","粉刺","痤疮"]
    key_kangshuailao = ["[复馥赋]活","更新","还原","回[复春]","[幻逆凝焕]时","时[空光]","岁月","[焕唤]肤","焕[肌彩颜采]","唤颜","换颜、活[采力肌效妍化肤]","活粒子","激活","[复卓活恒养塑臻童美紧驻新再]颜",
                        "立体","紧[肤容致实]","抗[衰老氧松]","抗衰老","抗老化","抗重力","抗松驰","抗氧化","拉[皮升提]","提[拉升]","不老","酚","平复","纹","皱","青春","弹力","去眼袋","祛?眼袋","生肌",
                        "衰老","松弛","新[肤活生]","重[造生]","再[造生]","果酸","胶原蛋白","胎[盘素]","胎盘素","骨胶原","维E","VE","VE-C","维他命E","维生素E","DNA","Q10","辅酶","酵[母素]","多效修护",
                        "多元修护","七重修护","[靓凝幼赋浣展]颜","无痕","新肌","弹性","修复","修护","VE－C","VC-E","VC－E","御龄"]

    result_effect_2 = []

    pattern = "("
    for i in effect_list:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                result_effect_2.append(p_res[0])

        if len(result_effect_2) > 0:
            count = Counter(result_effect_2).most_common(2)
            count_effect = count[0][0]
            if count_effect in key_baoshi:
                return "保湿"
            elif count_effect in key_meibai:
                return "美白"
            elif count_effect in key_kongyou:
                return "控油"
            elif count_effect in key_kangshuailao:
                return "抗衰老"

    return "其它"

def get_keyValue(kvs_list,keys):
    result_list = []
    for kvs in kvs_list:
        for kv in kvs:
            for key in keys:
                for k in kv.keys():
                    if len(key) == 1:
                        if key == k:
                            result_list.append(kv[k])
                    else:
                        if key in k and  len(k) < 6 and len(kv[k]) > 1:
                            result_list.append(kv[k])

    if len(result_list) == 0:
        return "不分"
    count = Counter(result_list).most_common(2)
    if len(count) >1 and count[0][1] == count[1][1] and len(count[0][0]) < len(count[1][0]) and len(re.compile("[0-9,，、]").findall(count[1][0])) == 0:
        return count[1][0]
    else:
        return count[0][0]

# 提取包装形式
def get_package_327(product_name,base64strs,type,suitPosition):
    '''
    泵管装、泵瓶装、笔、管装、罐装、连体饼装、瓶装、塑料袋、塑料盒、纸盒
    提取思路：采用OCR识别文本和模型结合，优先使用OCR文本识别，
    :param product_name:商品全称
    :param base64strs:图片列表
    :param type:类型
    :param suitPosition:适用部位
    :return:
    '''

    if '笔' in product_name:
        return '笔'
    if '饼' in product_name:
        return '连体饼装'
    if '喷雾' in product_name or type=='定妆喷雾':
        return '泵瓶装'
    if type=='指甲油':
        return '瓶装'
    if suitPosition =='唇部' or suitPosition =='眼部' and (type=='睫毛膏' or type=='染眉膏'):
        return '管装'
    if suitPosition =='眼部' and type=='眼影' or suitPosition =='面部' and ('BB霜' in type or type=='CC霜' or type=='粉饼' or type=='腮红') :
        return '连体饼装'


    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'
    url_unit3 = url_classify + ':5042/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()

    task_unit3 = MyThread(get_url_result, args=(base64strs, url_unit3,))
    task_unit3.start()
    # 获取执行结果
    # 获取执行结果:    '0': '其他','1': '塑料', '2': '半透明塑料','3': '非透明塑料', '4': '纸','5': '金属','6': '玻璃','7': '塑料底','8': '玻璃底'
    result_material = task_material.get_result()
    # '0': '其他',  '1': '袋',  '2': '真空袋',  '3': '立式袋',  '4': '吸嘴袋',  '5': '盒',  '6': '托盘',  '7': '格',  '8': '瓶',
    # '9': '喷雾瓶',  '10': '滴管瓶',  '11': '挤压瓶',  '12': '杯',  '13': '罐',  '14': '桶',  '15': '把手桶',  '16': '礼包',
    # '17': '筒',  '18': '网兜',  '19': '细长罐',  '20': '碗',  '21': '研磨瓶',  '22': '薄膜',  '23': '筐',  '24': '篮',  '25': '管',  '26': '按压瓶',  '27': '喷嘴瓶'
    result_shape = task_shape.get_result()

    # '0': '其他',    '1': '软塑料',    '2': '卡通特殊造型',    '3': '软包烟',    '4': '连体饼',    '5': '罐装',
    # '6': '陶瓷',    '7': '单支装',    '8': '棒状凝膏',    '9': '气雾式',    '10': '湿雾式',    '11': '纸包裹',    '12': '板装'
    result_unit3 = task_unit3.get_result()

    if len(result_material) == 0 and len(result_shape) == 0 and len(result_unit3) == 0:
        return "管装"


    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]
    unit3 = ''
    if len(result_unit3)>0:
        unit3 = Counter(result_unit3).most_common(1)[0][0]
    # print(material,shape,unit3)

    if shape == '罐':
        return '罐装'

    if unit3=='连体饼':
        return '连体饼装'
    elif unit3=='罐装':
        return '罐装'

    return '管装'


def category_rule_327(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"

    NA_1 = "不分"
    suitPosition = "不分"
    type = "不分"
    SPF = "不分"
    effect = "不分"
    state = "不分"
    NA_2 = "不分"
    waterproof = "不分"
    package = "不分"
    crowd = "不分"
    English_name = "不分"

    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    # 品牌
    if brand_1 == "不分":
        brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["AC","THREE","CR","zv","ZH","JE","AG","VC","RD","UMF","TIV","DO","JO","LAC","KAN","EA","OTY","CAG","AFU","GD","EH","EPI","BC","BK","HD","UU",
                                                                                      "CB","ZA","KS","HD","BS","BF","5度","KM","6789","MQ","NV","明艳","MR","FS","美的","REAM","Pt","M3","ZH","LB","LC","DW","SR","ANGLEE","奥希尼",
                                                                         "ODR","TRYME","eco""EFU","SD","NOME","DBR","LUX","REC","MODI","lac","ALA","TET","欧莱雅","novo","MOR","HOT","OLL","EST","FRESH","AILY","ELLE","DEVA"], [])
    brand_1 = re.sub("L'OREAL","LOREAL",brand_1)
    brand_1 = re.sub("L'OREA!","LOREAL",brand_1)
    brand_1 = re.sub("嫁竹","婉竹",brand_1)
    brand_1 = re.sub("绿绿萝","绿缘萝",brand_1)
    brand_1 = re.sub("卡卡","卞卡",brand_1)
    brand_1 = re.sub("伊玫格琳","伊玟格琳",brand_1)
    brand_1 = re.sub("NISTINE","MISTINE",brand_1)
    brand_1 = re.sub("StyOueen","Sty Queen",brand_1)
    brand_1 = re.sub("DEEIN'S黛妆之迷","DEEINS黛妆之迷",brand_1)

    if product_name == "不分":
        product_name = get_productName(dataprocessed, datasorted)

    product_name = re.sub("糖毛膏","睫毛膏",product_name)
    product_name = re.sub("唇育","唇膏",product_name)
    product_name = re.sub("攻瑰","玫瑰",product_name)
    product_name = re.sub("佩再","佩冉",product_name)
    product_name = re.sub("金弯婴婴","金鸾嘤嘤",product_name)
    product_name = re.sub("态意","恣意",product_name)
    product_name = re.sub("零熊","雾感",product_name)
    product_name = re.sub("粉底量","粉底霜",product_name)
    product_name = re.sub("肥红","腮红",product_name)
    product_name = re.sub("粉底量","粉底霜",product_name)

    product_name = re.sub("\d","",product_name)

    # 重容量
    capcity_1, capcity_2 = get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤|升|毫[开元升]|ML|ml|mL|L", "瓶包袋罐片",2)
    capcity_2 = re.sub("[元开]", "升", capcity_2)
    capcity_1 = re.sub("[元开]", "升", capcity_1)

    #适用部位
    suitPosition = get_suitPosition(datasorted,product_name)

    #类型
    type = get_type(datasorted,product_name)

    #防晒指数SPF值
    SPF = get_SPF(datasorted)

    #妆效
    effect_1 = get_effect(datasorted,product_name)
    #功效
    effect_result = get_effect_result(datasorted)
    #遮盖程度
    if suitPosition == "面部":
        cover = get_cover(datasorted)
    else:
        cover = str("其它")

    # 妆效+功效+遮盖度
    if effect_1 == "其它":
        effect_1 = ""
    if cover == "其它":cover = ""
    if effect_result == "其它" :effect_result = ""
    effect = effect_1 + effect_result + cover
    if effect == "":
        effect = "不分"

    #状态
    state = get_state(datasorted,product_name)

    #NA_1
    NA_1 = get_NA_1(datasorted)

    #NA_2
    NA_2 = get_NA_2(datasorted)

    #防水/不防水
    waterproof = get_waterproof(datasorted,product_name)

    #适用人群
    crowd = get_crowd(datasorted)

    #所对应的英文全称
    English_name = get_English_Name(datasorted)

    #包装
    package = get_package_327(product_name, type, suitPosition, datasorted)

    result_dict['info1'] = NA_1
    result_dict['info2'] = suitPosition
    result_dict['info3'] = type
    result_dict['info4'] = SPF
    result_dict['info5'] = effect
    result_dict['info6'] = state
    result_dict['info7'] = NA_2
    result_dict['info8'] = waterproof
    result_dict['info9'] = package
    result_dict['info10'] = crowd
    result_dict['info11'] = English_name
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name

    result_dict["commodityname"] = re.sub("[、,，：:：·]", "", result_dict["commodityname"])

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_3\327-化妆品'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3056263"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_327(image_list)
        with open(os.path.join(root_path, product) + r'\%s_ppocr.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)