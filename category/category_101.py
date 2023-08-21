import os
import re

from util import *
from glob import glob
from utilCapacity import get_capacity

'''
通用字段: 品牌1,品牌2,重容量,重容量*数量,商品全称
非通用字段: 口味,包装形式,类型,包装类型,配料
'''
FRUIT_LIST = [
    "平安果","雪莲果","苹果","沙果","海棠","野樱莓","枇杷","欧楂","山楂","温柏","黑加仑","蔷薇果","花楸","香梨","雪梨","杏","樱桃","水蜜桃","蜜桃","黄桃","油桃","蟠桃等","李子","梅子","青梅","西梅","白玉樱桃",
    "黑莓","沃柑","覆盆子","云莓","甘蔗","罗甘莓","白里叶莓","草莓","菠萝莓","橘子","砂糖桔","橙子","柠檬","青柠","柚子","金桔","青桔","葡萄柚","香橼","佛手","指橙","黄皮果","哈密瓜","香瓜","白兰瓜","刺角瓜",
    "金铃子","香蕉","木瓜","枣","葡萄","提子","蓝莓","蔓越莓","越橘","芒果","猕猴桃","奇异果","金果","菠萝蜜","菠萝","凤梨","杨梅","柿子","桑葚","无花果","牛油果","火龙果","荔枝","龙眼","桂圆","莲雾","蜜释迦",
    "榴莲","石榴","椰子","椰蓉","槟榔","蛇皮果","山竹","圣女果","小番茄","沙棘","西瓜","脐橙","香橙","车厘子","网纹瓜","百香果","西柚","石榴柚","石柚","树莓","橙","桃","橘","蜜瓜","梨","柑","酸梅","刺梨","桑椹","脆柿","玲珑柚",
    "珠宝李","沙田柚","芭乐"
]
TASTE_RULE = ['口味', '味']
EXP_RULE = ['保质期']
#没有用
#TYPE_RULE = ['混合','混合装','米制雪饼（米饼）','米制','面制','薯条','土豆非薯片、非薯条','土豆薯片','豆类','玉米','粟米','山药']
PACKAGE_RULE = ['单包装','多包装']
INGREDIENT_RULE = ['配料']
Capacity_Rule = ["净含量"]
Brand_list_1 = [i.strip() for i in set(open("Labels/101_brand_list_1",encoding="utf-8").readlines())]
Brand_replace_dict_1 = {i.strip().split(':')[0]:i.strip().split(':')[1] for i in set(open("Labels/101_brand_list_3", encoding="utf-8").readlines())}
# 通常来看需要20个非通用属性
LIMIT_NUM = 20
# 中国台湾，泰国，越南，美国，新西兰，日本，澳大利亚，智利，秘鲁，菲律宾
# 原产地
# origin_area_list = ['中国台湾','TAIWAN','台湾','泰国','THAILAND','越南','VIETNAM','美国','U.S.A','新西兰','NEW ZEALAND','纽西兰','日本','JAPAN','澳大利亚','AUSTRALIA',
#                     '智利','CHILE','秘鲁','PERU','菲律宾','THE PHILIPPINES','PHILIPPINES']
# 原产地
origin_area_list = [i.strip() for i in set(open("Labels/101_originarea_list_1",encoding="utf-8").readlines())]
origin_area_dict = {i.strip().split(':')[0]:i.strip().split(':')[1] for i in set(open("Labels/101_originarea_dict_1", encoding="utf-8").readlines())}

def get_type(texts_list):
    pattern = "("
    for i in FRUIT_LIST:
        pattern += i + "|"
    pattern = pattern[:-1] + ")"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

#从字符串获取中文
def getChinese(txt):
    uncn = re.compile(r'[\u4e00-\u9fa5]')
    ls = uncn.findall(txt)
    cn = "".join(ls)
    return cn

def get_brand_bak(texts_list):
    brand_1_txt_list=[]
    for texts in texts_list:
        for text in texts:
            for b1 in Brand_list_1:
                if b1.upper() in text.upper() or b1 in text:
                    brand_1_txt_list.append(b1)
    if len(brand_1_txt_list) > 0:
        brand_1_txt_list.sort(key=len, reverse=True)
        count = Counter(brand_1_txt_list).most_common(1)
        brand_1 = count[0][0]
        return brand_1
    return '不分'


def get_productName_voting(texts_list):
    result_list = []
    abort_list = ['放','市','飞安']

    pattern_1 = "(\w+榴莲果肉|\w+榴蓬果肉|\w+榴莲肉肉|\w+金枕榴莲肉|\w+冻榴莲肉|\w+老树榴莲|\w*金枕榴莲|\w*烤榴莲|\w+榴莲肉|\w+熟榴莲|\w+榴莲|\w*猕猴桃|\w*蓝莓|\w*玲珑柚|\w*草莓|\w*蜜柚|\w*脐橙|\w*苹果|\w*树莓|" \
                "\w*西梅|\w*青提|\w*黑提|\w*香梨|\w*车厘子|\w*珠宝李|哈密瓜块|\w*蜜瓜|\w*黑莓|\w*奇异果|\w*人参果|\w*荔枝|\w*火柑|\w*百香果|\w*蜜释迦|\w*金菠萝|\w*脆柿|\w*金椰果肉|\w*脆蜜金柑|" \
                "\w*粑粑柑|\w*葡萄柚|\w*耙耙柑|\w*石榴柚|\w*油桃|\w*小菠萝果切|美国蛇果|\w*小菠萝|\w*香蕉|\w*木瓜|\w*芒果|\w*山竹|\w*莲雾|\w+甘蔗|\w*沃柑|\w*火龙果|\w*柠檬|\w*胡柚|\w*糖果柑|\w*葡萄柚|" \
                "\w*沙田柚|\w*香瓜|\w*稀柚|\w*红肉橙|\w*美国橙|\w*鲜椰肉|\w*埃及橙|\w*青啤梨|\w*桔子|Blueberries|Strawberry)"

    pattern_3 = "([\w\.]+榴莲果肉|[\w\.]+菠萝蜜肉|"
    for i in FRUIT_LIST:
        pattern_3 += "[\w\.]+" + i + "|"

    pattern_3 = pattern_3[:-1] + ")$"
    pattern_4 = pattern_3[:-1].replace("+", "*")
    pre_result_list=[]
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_1)
            if len(p_res) > 0:
                flag = True
                for it in abort_list:
                    if it in p_res[0]:
                        flag = False
                        break
                if flag and "的" not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text:
                        pre_result_list.append(p_res[0])
                continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        if len(count) == 1:
            return count[0][0]
        else:
            if count[0][1] < count[1][1]:
                return count[1][0]
            else:
                return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_3)
            if len(p_res) > 0:
                flag = True
                for it in abort_list:
                    if it in p_res[0]:
                        flag = False
                        break
                if flag and "的" not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text:
                        pre_result_list.append(p_res[0])
                continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        if len(count) == 1:
            return count[0][0]
        else:
            if count[0][1] < count[1][1]:
                return count[1][0]
            else:
                return count[0][0]

    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern_4)
            if len(p_res) > 0:
                flag = True
                for it in abort_list:
                    if it in p_res[0]:
                        flag = False
                        break
                if flag and "的" not in p_res[0]:
                    result_list.append(p_res[0])
                    if '品名' in text:
                        pre_result_list.append(p_res[0])
                continue

    if len(result_list) > 0:
        if len(pre_result_list) > 0:
            return pre_result_list[0]
        result_list.sort(key=len, reverse=True)
        count = Counter(result_list).most_common(2)
        if len(count) == 1:
            return count[0][0]
        else:
            if count[0][1] < count[1][1]:
                return count[1][0]
            else:
                return count[0][0]
    return '不分'

def get_EXP_store(kvs_list,texts_list):
    pattern = r'(储存|贮藏|贮存|保存|贴存|购存|存|冷藏)'
    p = re.compile(pattern)
    degree=''
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                p_res1 = p.findall(kv[k])
                if len(p_res) > 0 or len(p_res1):
                    p_res = re.compile("-?\d{1,2}[-至]\d{1,2}[度C]?以?下?|零下\d+以?下?").findall(kv[k])
                    if len(p_res) > 0:
                        if len(re.compile("\d$").findall(p_res[0])) > 0:
                            if '-' in p_res[0]:
                                ts = p_res[0].split('-')
                                if int(ts[1])>30:
                                    return ts[0]+'-'+ts[1][0]+'度'
                                else:
                                    return p_res[0] + "度"
                            else:
                                return p_res[0] + "度"
                        else:
                            return p_res[0]

    pattern = r'(-?\d{1,2}[-至]\d{1,2}[度C]|零下\d{1,2}[度C]?以?下?|-18以?下?|0-4|2-8)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and '日期' not in text:
                if len(re.compile("\d$").findall(p_res[0])) > 0 :
                    return p_res[0] + "度"
                else:
                    return p_res[0]


    pattern = r'(冷藏|冷冻)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if '常温' in text:
                    return '常温'
                else:
                    return p_res[0]

    pattern = r'常温|阴凉|带温|冷藏'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]

    return "不分"

def get_EXP(kvs_list,texts_list):

    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    p_1 = re.compile(r'[0-9一-十]+个?[年天月]')
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    p_res_1 = p_1.findall(kv[k])
                    if len(p_res_1) > 0:
                        if len(re.compile(r'20[12]\d年[01]?\d月[0123]?\d日?').findall(kv[k])) > 0:
                            continue
                        return kv[k]

    pattern = r'(质期|保期)'
    p = re.compile(pattern)
    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    if kv[k] in ["12","18"]:
                        return kv[k] + "个月"

    pattern = "-?\d{0,2}[-至]\d+[度C]?以?下?\d+个月|零下\d+以?下?\d+个月|-\d+以?下?\d+个月"
    for texts in texts_list:
        tmp_list = []
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                tmp_list.append(p_res[0])
        if len(tmp_list) > 0:
            return ",".join(tmp_list)


    pattern = r'(\D+[12]年|^[12]年|\d+个月|[一-十]+个月|\d+天)'
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0 and "无理由" not in text and "退" not in text and '挂果期' not in text:
                return p_res[0]

    pattern = r'20[12]\d[-\\/\s\.]?[01]\d[-\\/\s\.]?[0123][\d]'
    date_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                date_list.append(re.sub("\D","",p_res[0]))

    date_list = list(set(date_list))
    for ddate in date_list:
        try:
            d0 = datetime.datetime.strptime(ddate, "%Y%m%d")
        except:
            date_list.remove(ddate)

    date_list.sort(reverse=True)
    if len(date_list) >=2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y%m%d")
        df = datetime.datetime.strptime(date_list[-1], "%Y%m%d")
        d_res = (d0 - df).days
        if d_res > 1:
            if d_res>800:
                return '不分'
            return str(d_res) + "天"

    pattern = r'20[12]\d年[01]?\d月[0123]?\d日?'
    date_list = []
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                if "日" not in p_res[0]:
                    date_list.append(p_res[0] + "日")
                else:
                    date_list.append(p_res[0])

    date_list = list(set(date_list))
    for ddate in date_list:
        try:
            d0 = datetime.datetime.strptime(ddate, "%Y年%m月%d日")
        except:
            date_list.remove(ddate)

    date_list.sort(reverse=True)
    if len(date_list) >= 2:
        d0 = datetime.datetime.strptime(date_list[0], "%Y年%m月%d日")
        df = datetime.datetime.strptime(date_list[-1], "%Y年%m月%d日")
        d_res = (d0 - df).days
        if d_res > 1:
            if d_res>800:
                return '不分'
            return str(d_res) + "天"

    return "不分"

def get_EXP_all(texts_list):
    pattern = "-18[度C][\u4e00-\u9fa5]*\d+个?[天月]|零下18[度C][\u4e00-\u9fa5]*\d+个?[天月]"
    for texts in texts_list:
        for text in texts:
            p_res = get_info_by_pattern(text, pattern)
            if len(p_res) > 0:
                return p_res[0]
    return "不分"

def get_EXP_last(store,EXP):
    store = re.sub("^-", "零下", store)
    store = re.sub("[度C]?以下", "度以下", store)
    store = re.sub("带温", "常温", store)
    store = re.sub("C", "度", store)
    EXP = re.sub("^-", "零下", EXP)
    EXP = re.sub("[度C]?以下", "度以下", EXP)
    EXP = re.sub("0[-至]4[度C]?", "0至4度", EXP)
    EXP = re.sub("0[-至]5[度C]?", "0至5度", EXP)
    EXP = re.sub("C度", "度", EXP)

    if len(re.compile("\d$").findall(store)) > 0:
        store += "度"

    # store = "零下18度以下冷冻保存" if store == "冷冻" or store == "不分" else store
    store = "零下18度以下冷冻保存" if store == "冷冻" else store
    if store != "不分":
        if EXP != "不分" and len(re.compile(r'(-?\d+[-至]\d+[度C]|零下\d+以?下?|-\d+[度C]?以?下?|冷藏|冷冻|常温)').findall(EXP)) == 0:
            EXP = store + EXP
    if EXP == '不分':
        EXP = store
    return EXP

#提取礼品装
def get_giftpacket(product_name,texts_list):
    '''
    提取子类
    提取依据：101水果定义文档及人为标注Excel测试数据
    提取思路：101水果定义文档只明确定义 包括礼品装/非礼品装，
    礼品装定义：根据产品全称中带有“礼”字的产品，结合产品图片判断是否为礼盒装。
    按包装大字或贴签上是否有礼盒判定，果礼纳福也算，其它小字、广告词不看
    :param product_name:商品名称全称
    :param texts_list:文本列表
    :return:
    '''
    result = '非礼品装'
    if '礼' in product_name:
        for texts in texts_list:
            for text in texts:
                if '礼盒' in text:
                    result = '礼品装'
                    return result
    else:
        for texts in texts_list:
            for text in texts:
                if '礼盒' in text:
                    result = '礼品装'
                    return result
    return result

#提取加工程度
def get_process_degree(product_name,texts_list,type):
    '''
    提取加工程度
    提取依据：101水果定义文档及人为标注Excel测试数据
    提取思路：101水果定义文档只明确定义 包含整果、果切、去皮、拆瓣、未知
    整果：非加工过的鲜果，只要是完整、没有经过去皮、拆分、切割等加工工序的，即使是从成串上拆下来的，仍为完整鲜果。特殊规则：椰子、去皮椰青、有易开宝吸嘴可直饮的椰子，归类为整果
    果切：1、通过全称判断：鲜果经切割后分成一小块一小块“片”或“块”的形状，全称含有“切”、“块”等，具体需看图片判定。
          2、全称没有“果切”等字样，但实际产品形态属于果切
          3、果切与整果混合，优先给果切（如图，蓝莓为整果，草莓、菠萝为果切）
          4、特殊规则：椰子蛋也归类为果切
    去皮：经过加工处理，仅去掉外壳或削皮的鲜果。
    拆瓣：整个鲜果经去皮、拆分，将内部的果肉独立分装出售的。 根据数据判断，凡是子类为榴莲或枕榴基本都是拆瓣
    :param product_name:商品名称全称
    :param texts_list:文本列表
    :return:
    '''
    result = '不分'
    list_cut = ['果切','切','片','块','椰肉','椰果肉']
    for it in list_cut:
        if it in product_name:
            result = '果切'
            break

    if result=='不分':
        for texts in texts_list:
            for text in texts:
                if '切片' in text or '切碎' in text or "果切" in text:
                    result = '果切'
                    break
            if result != '不分':
                break
    if result == '不分':
        if '去皮' in product_name:
            result = '去皮'

    if result == '不分':
        if type=='榴莲' or type=='枕榴':
            result = '拆瓣'
        else:
            result = '整果'
    return result

#提取原产地
def get_origin_area(kvs_list,texts_list,product_name):
    '''
    提取加工程度
    提取依据：101水果定义文档及人为标注Excel测试数据
    提取思路：101水果定义文档只明确定义
              1、包括：中国台湾，泰国，越南，美国，新西兰，日本，澳大利亚，智利，秘鲁，菲律宾，进口，不分其它(具体中国或外国国家和城市名称)
              2、按包装原料产地或产地抄录，不按厂家地址或加工地址抄，按包装原始状态抄录，例如云南丽江，贵州修文，江苏徐州徐香，新疆阿克苏，中国云南等
              3、进口：外包装标注外国名字，且不在以上国家或地区的；或外包装出现日文、泰文、俄文等非英语文字，无法区分具体产地和产国的，分类为“进口”
              4、不分：排出以上情况，外包装没有明确标注产地的。
    :param kvs_list:文本键值对
    :param texts_list:文本列表
    :return:
    '''
    pattern = '(原产地|原料产地|产地|原产国|产国|产址|原产园)'
    split_list = ['上市日期']
    p = re.compile(pattern)
    pattern1 = ""
    for it in origin_area_list:
        pattern1 += it+'|'
    # pattern1 = '(' + pattern1[:-1] + ')$'
    pattern1 = '(' + pattern1[:-1] + ')'
    p1 = re.compile(pattern1)

    list_result = []
    result='不分'

    for kvs in kvs_list:
        for kv in kvs:
            for k in kv.keys():
                p_res = p.findall(k)
                if len(p_res) > 0:
                    kvp = kv[k]
                    list_result.append(kvp)
                    for area in origin_area_list:
                        if area in kvp:
                            result = area
                            break
                    if result != '不分':
                        break
            if result != '不分':
                break
        if result != '不分':
            break

    if result=='不分' :
        for texts in texts_list:
            for text in texts:
                p_res = p1.findall(text)
                if len(p_res) > 0 and p_res[0] in origin_area_list:
                    result = p_res[0]
                    break

            if result!='不分':
                break
    if result == '不分' :
        if len(list_result)>0:
            result = list_result[0]

    for sp in split_list:
        if sp in result:
            result=result.split(sp)[0]

    if result!='不分':
        # result = re.sub("玉溪", "玉虞", result)
        # result = re.sub("青马市", "青岛市", result)
        # result = re.sub("山东果阳", "山东莱阳", result)
        # result = re.sub("街南三亚", "海南三亚", result)
        # result = re.sub("江西鲶州", "江西赣州", result)
        # result = re.sub("广西武腾", "广西武鸣", result)
        # result = re.sub("新疆库尔勤", "新疆库尔勒", result)
        # result = re.sub("甘弟庆阳", "甘肃庆阳", result)
        # result = re.sub("惠大利", "意大利", result)
        # result = re.sub("秘兽", "秘鲁", result)
        # result = re.sub("湖北陕旧", "湖北秭归", result)
        # result = re.sub("与气候", "", result)
        result = re.sub("\W", "", result)
        if result in origin_area_dict.keys():
            result = origin_area_dict[result]
        if len(result)==0:
            result='不分'
    return result

def get_brand_list_local(texts_list,Brand_list_1,Brand_list_2,keyWords,abortWords,num = 2):
    brand_1_tmp_list = []
    brand_1_txt_list = []
    brand_1_merge_tmp_list = []
    brand_1_merge_list = []
    brand_1_merge_absort_list = []
    brand_2 = []
    for texts in texts_list:
        # text_str = TextFormatNormal(texts)
        text_str = "".join(texts)
        text_str_ori = ",".join(texts)
        for bb in Brand_list_1:
            if bb in text_str :
                if len(bb) > 2:
                    brand_1_merge_tmp_list.append(bb)
                elif len(re.compile("(,|^)%s($|,)"%(",".join(list(bb)))).findall(text_str_ori)) > 0:
                    brand_1_merge_tmp_list.append(bb)
        for text in texts:
            if text in keyWords:
                brand_1_txt_list.append(text)
            for b1 in Brand_list_1:
                if b1.upper() in text.upper() or b1 in text:
                    if b1 == text and b1 not in abortWords:
                        brand_1_txt_list.append(text)
                    if len(b1) > num or (len(re.compile("[市省镇区村县请勿]|大道|街道").findall(text)) == 0 and "地址" not in text):

                        brand_1_tmp_list.append(b1)
                    else:
                        brand_1_merge_absort_list.append(b1)


        for b2 in Brand_list_2:
            if b2 in texts:
                brand_2.append(b2)

    if len(brand_2) > 0:
        brand_2 = ",".join(list(set(brand_2)))
    else:
        brand_2 = "不分"

    for bm in brand_1_merge_tmp_list:
        if bm not in brand_1_tmp_list:
            brand_1_merge_list.append(bm)

    if len(brand_1_merge_list) > 0:
        count = Counter(brand_1_merge_list).most_common(1)
        brand_1 = count[0][0]
        if brand_1 not in brand_1_merge_absort_list:
            return brand_1,brand_2

    if len(brand_1_txt_list) > 0:
        brand_1_txt_list.sort(key=len, reverse=True)
        count = Counter(brand_1_txt_list).most_common(1)
        brand_1 = count[0][0]
    else:
        brand_1_list = []
        for i in brand_1_tmp_list:
            flag = True
            for j in brand_1_tmp_list:
                if j != i and i in j:
                    flag = False
                    break
            if flag:
                brand_1_list.append(i)

        if len(brand_1_list) == 0:
            brand_1 = "不分"
        else:
            brand_1_list.sort(key=len, reverse=True)
            count = Counter(brand_1_list).most_common(1)
            brand_1 = count[0][0]
    return brand_1,brand_2

def get_package_101(base64strs):
    url_material = url_classify + ':5028/yourget_opn_classify'
    url_shape = url_classify + ':5029/yourget_opn_classify'

    task_material = MyThread(get_url_result, args=(base64strs, url_material,))
    task_material.start()
    task_shape = MyThread(get_url_result, args=(base64strs, url_shape,))
    task_shape.start()
    # 获取执行结果
    result_material = task_material.get_result()
    result_shape = task_shape.get_result()

    if len(result_material) == 0 or len(result_shape) == 0:
        return "不分"

    if "真空袋" in result_shape:
        return "真空塑料袋"

    material = Counter(result_material).most_common(1)[0][0]
    shape = Counter(result_shape).most_common(1)[0][0]

    if shape == "网兜":
        return "网兜"
    elif shape == "薄膜":
        return "塑料薄膜"

    if material == "塑料底" or "塑料" in material:
        material = "塑料"
    elif material == "玻璃底":
        material = "玻璃"

    if "袋" in shape:
        shape = "袋"
    elif "瓶" in shape:
        shape = "瓶"
    elif "桶" in shape or "罐" in shape:
        shape = "桶"
    elif shape == "礼包":
        shape = "盒"

    return material + shape

def category_rule_101(datasorted,dataprocessed,dataoriginal,base64strs,uie_obj = None):
    result_dict = {}
    brand_1 = "不分"
    brand_2 = "不分"
    EXP = "不分"
    type = "不分"
    package = "不分"
    capcity_1 = "不分"
    capcity_2 = "不分"
    product_name = "不分"
    brand_tmp = "不分"

    # 礼品装
    giftpacket='非礼品装'
    # 加工程度
    process_degree = "不分"
    #原产地
    origin_area = '不分'
    dataprocessed.sort(key=len, reverse=True)
    datasorted.sort(key=len)

    brand_1, brand_2 = get_brand_list(datasorted, Brand_list_1, [], ["PLU","Tibos"],[])
    # brand_1, brand_2 = get_brand_list_local(datasorted, Brand_list_1, [], [], [])

    brand_1 = re.sub("歌本", "歌林", brand_1)
    brand_1 = re.sub("冰冻", "冷冻", brand_1)
    brand_1 = re.sub("泰缝", "泰莲", brand_1)
    brand_1 = re.sub("果泥", "果派", brand_1)
    brand_1 = re.sub("福莲", "榴莲", brand_1)
    brand_1 = re.sub("留莲", "榴莲", brand_1)
    brand_1 = re.sub("ALDI", "奥乐奇ALDI", brand_1)

    if brand_1 == "不分":
        # brand_1 = get_brand(dataprocessed)
        brand_1 = get_brand_bak(datasorted)

    # product_name = get_keyValue(dataprocessed, ["品名"])
    if product_name == "不分":
        product_name = get_productName_voting(datasorted)
        if brand_1!='不分':
            if (len(product_name) - len(brand_1)) > 1:
                product_name = re.sub(brand_1, "", product_name)
        product_name = re.sub('泰月', "泰国", product_name)
        product_name = re.sub('榴蓬', "榴莲", product_name)
        product_name = re.sub('Blueberries', "蓝莓", product_name)
        product_name = re.sub('Strawberry', "草莓", product_name)
        product_name = re.sub('冷浦', "冷冻", product_name)

    if product_name != "不分":
        for i in FRUIT_LIST:
            if i in product_name:
                type = i
                break
    if type == "不分":
        type = get_type(datasorted)
    # 加工程度
    process_degree = get_process_degree(product_name, datasorted,type)
    giftpacket = get_giftpacket(product_name, datasorted)
    origin_area = get_origin_area(dataprocessed,datasorted,product_name)
    # if EXP == "不分":
    #     EXP = get_EXP(dataprocessed, datasorted)

    EXP = get_EXP_all(datasorted)
    if EXP != "不分":
        EXP = re.sub("^-", "零下", EXP)
        EXP = re.sub("[度C]", "度", EXP)

    if EXP == "不分":
        store = get_EXP_store(dataprocessed, datasorted)
        EXP = get_EXP(dataprocessed, datasorted)
        EXP = get_EXP_last(store, EXP)

    capcity_1 ,capcity_2= get_capacity(dataprocessed, datasorted, "G|g|克|千克|kg|KG|斤|公斤", "包袋盒罐粒个", 0)

    package = get_package_101(base64strs)

    type = type if type != "平安果" else "苹果"

    result_dict['info1'] = package
    result_dict['info2'] = EXP
    result_dict['info3'] = type
    result_dict['info4'] = giftpacket
    result_dict['info5'] = process_degree
    result_dict['info6'] = origin_area
    result_dict['brand1'] = brand_1
    result_dict['brand2'] = brand_2
    result_dict['capacitysum'] = capcity_1
    result_dict['capacityamount'] = capcity_2
    result_dict['commodityname'] = product_name
    # result_dict['brand_tmp'] = brand_tmp
    real_use_num = 6
    sub_num = LIMIT_NUM - real_use_num
    for i in range(sub_num):
        item_index = i + real_use_num + 1
        key_name = 'info' + str(item_index)
        result_dict[key_name] = ""

    return result_dict

if __name__ == '__main__':
    root_path = r'D:\Data\商品识别\stage_1\101-水果'
    for product in os.listdir(root_path)[:100]:
        image_list = []
        # product = "3132577"
        for image_path in glob(os.path.join(root_path, product) + "\*g"):
            image_list.append(image_path)
        result_dict = category_rule_101(image_list)
        with open(os.path.join(root_path, product) + r'\%s_new.json' % (product), "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=4)