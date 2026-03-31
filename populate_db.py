#!/usr/bin/env python3
"""
Database Population Script for Chinese Self Learning System
This script populates the words table with sample HSK 1-6 vocabulary data.
"""

import mysql.connector
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'joshua6775',
    'database': 'cls'
}

def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise e

# Sample HSK vocabulary data (HSK 1-3 for demonstration)
# Format: (level, hanzi, pinyin, pinyin_tone, pinyin_num, english, pos, tts_url)
HSK_WORDS = [
    # HSK 1 - Basic words
    (1, "你好", "nǐ hǎo", "ni3 hao3", "ni3 hao3", "hello", "interjection", "https://dict.youdao.com/dictvoice?audio=你好&type=1"),
    (1, "谢谢", "xiè xie", "xie4 xie", "xie4 xie", "thank you", "verb", "https://dict.youdao.com/dictvoice?audio=谢谢&type=1"),
    (1, "再见", "zài jiàn", "zai4 jian4", "zai4 jian4", "goodbye", "interjection", "https://dict.youdao.com/dictvoice?audio=再见&type=1"),
    (1, "是", "shì", "shi4", "shi4", "to be; yes", "verb", "https://dict.youdao.com/dictvoice?audio=是&type=1"),
    (1, "不", "bù", "bu4", "bu4", "no; not", "adverb", "https://dict.youdao.com/dictvoice?audio=不&type=1"),
    (1, "好", "hǎo", "hao3", "hao3", "good; well", "adjective", "https://dict.youdao.com/dictvoice?audio=好&type=1"),
    (1, "我", "wǒ", "wo3", "wo3", "I; me", "pronoun", "https://dict.youdao.com/dictvoice?audio=我&type=1"),
    (1, "你", "nǐ", "ni3", "ni3", "you", "pronoun", "https://dict.youdao.com/dictvoice?audio=你&type=1"),
    (1, "他", "tā", "ta1", "ta1", "he; him", "pronoun", "https://dict.youdao.com/dictvoice?audio=他&type=1"),
    (1, "她", "tā", "ta1", "ta1", "she; her", "pronoun", "https://dict.youdao.com/dictvoice?audio=她&type=1"),
    (1, "我们", "wǒ men", "wo3 men", "wo3 men", "we; us", "pronoun", "https://dict.youdao.com/dictvoice?audio=我们&type=1"),
    (1, "他们", "tā men", "ta1 men", "ta1 men", "they; them", "pronoun", "https://dict.youdao.com/dictvoice?audio=他们&type=1"),
    (1, "什么", "shén me", "shen2 me", "shen2 me", "what", "pronoun", "https://dict.youdao.com/dictvoice?audio=什么&type=1"),
    (1, "这", "zhè", "zhe4", "zhe4", "this", "pronoun", "https://dict.youdao.com/dictvoice?audio=这&type=1"),
    (1, "那", "nà", "na4", "na4", "that", "pronoun", "https://dict.youdao.com/dictvoice?audio=那&type=1"),
    (1, "谁", "shéi", "shei2", "shei2", "who", "pronoun", "https://dict.youdao.com/dictvoice?audio=谁&type=1"),
    (1, "哪", "nǎ", "na3", "na3", "which", "pronoun", "https://dict.youdao.com/dictvoice?audio=哪&type=1"),
    (1, "多少", "duō shao", "duo1 shao", "duo1 shao", "how many; how much", "pronoun", "https://dict.youdao.com/dictvoice?audio=多少&type=1"),
    (1, "几", "jǐ", "ji3", "ji3", "how many; a few", "pronoun", "https://dict.youdao.com/dictvoice?audio=几&type=1"),
    (1, "有", "yǒu", "you3", "you3", "to have; there is", "verb", "https://dict.youdao.com/dictvoice?audio=有&type=1"),
    (1, "没有", "méi you", "mei2 you", "mei2 you", "to not have; there is not", "verb", "https://dict.youdao.com/dictvoice?audio=没有&type=1"),
    (1, "在", "zài", "zai4", "zai4", "to be at; in; on", "preposition", "https://dict.youdao.com/dictvoice?audio=在&type=1"),
    (1, "和", "hé", "he2", "he2", "and; with", "conjunction", "https://dict.youdao.com/dictvoice?audio=和&type=1"),
    (1, "也", "yě", "ye3", "ye3", "also; too", "adverb", "https://dict.youdao.com/dictvoice?audio=也&type=1"),
    (1, "很", "hěn", "hen3", "hen3", "very; quite", "adverb", "https://dict.youdao.com/dictvoice?audio=很&type=1"),
    (1, "吗", "ma", "ma", "ma", "(question particle)", "particle", "https://dict.youdao.com/dictvoice?audio=吗&type=1"),
    (1, "了", "le", "le", "le", "(completed action particle)", "particle", "https://dict.youdao.com/dictvoice?audio=了&type=1"),
    (1, "的", "de", "de", "de", "(possessive particle)", "particle", "https://dict.youdao.com/dictvoice?audio=的&type=1"),
    (1, "人", "rén", "ren2", "ren2", "person; people", "noun", "https://dict.youdao.com/dictvoice?audio=人&type=1"),
    (1, "大", "dà", "da4", "da4", "big; large", "adjective", "https://dict.youdao.com/dictvoice?audio=大&type=1"),
    (1, "小", "xiǎo", "xiao3", "xiao3", "small; little", "adjective", "https://dict.youdao.com/dictvoice?audio=小&type=1"),
    (1, "多", "duō", "duo1", "duo1", "many; much", "adjective", "https://dict.youdao.com/dictvoice?audio=多&type=1"),
    (1, "少", "shǎo", "shao3", "shao3", "few; little", "adjective", "https://dict.youdao.com/dictvoice?audio=少&type=1"),
    (1, "个", "gè", "ge4", "ge4", "(general measure word)", "measure word", "https://dict.youdao.com/dictvoice?audio=个&type=1"),
    (1, "天", "tiān", "tian1", "tian1", "day; sky", "noun", "https://dict.youdao.com/dictvoice?audio=天&type=1"),
    (1, "今天", "jīn tiān", "jin1 tian1", "jin1 tian1", "today", "noun", "https://dict.youdao.com/dictvoice?audio=今天&type=1"),
    (1, "明天", "míng tiān", "ming2 tian1", "ming2 tian1", "tomorrow", "noun", "https://dict.youdao.com/dictvoice?audio=明天&type=1"),
    (1, "昨天", "zuó tiān", "zuo2 tian1", "zuo2 tian1", "yesterday", "noun", "https://dict.youdao.com/dictvoice?audio=昨天&type=1"),
    (1, "年", "nián", "nian2", "nian2", "year", "noun", "https://dict.youdao.com/dictvoice?audio=年&type=1"),
    (1, "月", "yuè", "yue4", "yue4", "month; moon", "noun", "https://dict.youdao.com/dictvoice?audio=月&type=1"),
    (1, "日", "rì", "ri4", "ri4", "day; sun", "noun", "https://dict.youdao.com/dictvoice?audio=日&type=1"),
    (1, "号", "hào", "hao4", "hao4", "number; day (of month)", "noun", "https://dict.youdao.com/dictvoice?audio=号&type=1"),
    (1, "点", "diǎn", "dian3", "dian3", "o'clock; point", "noun", "https://dict.youdao.com/dictvoice?audio=点&type=1"),
    (1, "分", "fēn", "fen1", "fen1", "minute; to divide", "noun", "https://dict.youdao.com/dictvoice?audio=分&type=1"),
    (1, "现在", "xiàn zài", "xian4 zai4", "xian4 zai4", "now", "noun", "https://dict.youdao.com/dictvoice?audio=现在&type=1"),
    (1, "时候", "shí hou", "shi2 hou", "shi2 hou", "time; when", "noun", "https://dict.youdao.com/dictvoice?audio=时候&type=1"),
    (1, "上", "shàng", "shang4", "shang4", "up; above; to go up", "verb", "https://dict.youdao.com/dictvoice?audio=上&type=1"),
    (1, "下", "xià", "xia4", "xia4", "down; below; to go down", "verb", "https://dict.youdao.com/dictvoice?audio=下&type=1"),
    (1, "来", "lái", "lai2", "lai2", "to come", "verb", "https://dict.youdao.com/dictvoice?audio=来&type=1"),
    (1, "去", "qù", "qu4", "qu4", "to go", "verb", "https://dict.youdao.com/dictvoice?audio=去&type=1"),
    (1, "吃", "chī", "chi1", "chi1", "to eat", "verb", "https://dict.youdao.com/dictvoice?audio=吃&type=1"),
    (1, "喝", "hē", "he1", "he1", "to drink", "verb", "https://dict.youdao.com/dictvoice?audio=喝&type=1"),
    (1, "水", "shuǐ", "shui3", "shui3", "water", "noun", "https://dict.youdao.com/dictvoice?audio=水&type=1"),
    (1, "饭", "fàn", "fan4", "fan4", "rice; meal", "noun", "https://dict.youdao.com/dictvoice?audio=饭&type=1"),
    (1, "书", "shū", "shu1", "shu1", "book", "noun", "https://dict.youdao.com/dictvoice?audio=书&type=1"),
    (1, "看", "kàn", "kan4", "kan4", "to look; to read; to watch", "verb", "https://dict.youdao.com/dictvoice?audio=看&type=1"),
    (1, "听", "tīng", "ting1", "ting1", "to listen; to hear", "verb", "https://dict.youdao.com/dictvoice?audio=听&type=1"),
    (1, "说", "shuō", "shuo1", "shuo1", "to speak; to say", "verb", "https://dict.youdao.com/dictvoice?audio=说&type=1"),
    (1, "话", "huà", "hua4", "hua4", "words; speech", "noun", "https://dict.youdao.com/dictvoice?audio=话&type=1"),
    (1, "中文", "zhōng wén", "zhong1 wen2", "zhong1 wen2", "Chinese (language)", "noun", "https://dict.youdao.com/dictvoice?audio=中文&type=1"),
    (1, "英语", "yīng yǔ", "ying1 yu3", "ying1 yu3", "English (language)", "noun", "https://dict.youdao.com/dictvoice?audio=英语&type=1"),
    (1, "学习", "xué xí", "xue2 xi2", "xue2 xi2", "to study; to learn", "verb", "https://dict.youdao.com/dictvoice?audio=学习&type=1"),
    (1, "工作", "gōng zuò", "gong1 zuo4", "gong1 zuo4", "work; job", "noun", "https://dict.youdao.com/dictvoice?audio=工作&type=1"),
    (1, "学生", "xué sheng", "xue2 sheng", "xue2 sheng", "student", "noun", "https://dict.youdao.com/dictvoice?audio=学生&type=1"),
    (1, "老师", "lǎo shī", "lao3 shi1", "lao3 shi1", "teacher", "noun", "https://dict.youdao.com/dictvoice?audio=老师&type=1"),
    (1, "学校", "xué xiào", "xue2 xiao4", "xue2 xiao4", "school", "noun", "https://dict.youdao.com/dictvoice?audio=学校&type=1"),
    (1, "家", "jiā", "jia1", "jia1", "home; family", "noun", "https://dict.youdao.com/dictvoice?audio=家&type=1"),
    (1, "中国", "zhōng guó", "zhong1 guo2", "zhong1 guo2", "China", "noun", "https://dict.youdao.com/dictvoice?audio=中国&type=1"),
    (1, "钱", "qián", "qian2", "qian2", "money", "noun", "https://dict.youdao.com/dictvoice?audio=钱&type=1"),
    (1, "买", "mǎi", "mai3", "mai3", "to buy", "verb", "https://dict.youdao.com/dictvoice?audio=买&type=1"),
    (1, "卖", "mài", "mai4", "mai4", "to sell", "verb", "https://dict.youdao.com/dictvoice?audio=卖&type=1"),
    (1, "电话", "diàn huà", "dian4 hua4", "dian4 hua4", "telephone; phone call", "noun", "https://dict.youdao.com/dictvoice?audio=电话&type=1"),
    (1, "名字", "míng zi", "ming2 zi", "ming2 zi", "name", "noun", "https://dict.youdao.com/dictvoice?audio=名字&type=1"),
    (1, "叫", "jiào", "jiao4", "jiao4", "to be called; to call", "verb", "https://dict.youdao.com/dictvoice?audio=叫&type=1"),
    (1, "岁", "suì", "sui4", "sui4", "years old; age", "noun", "https://dict.youdao.com/dictvoice?audio=岁&type=1"),
    (1, "做", "zuò", "zuo4", "zuo4", "to do; to make", "verb", "https://dict.youdao.com/dictvoice?audio=做&type=1"),
    (1, "写", "xiě", "xie3", "xie3", "to write", "verb", "https://dict.youdao.com/dictvoice?audio=写&type=1"),
    (1, "字", "zì", "zi4", "zi4", "character (written); word", "noun", "https://dict.youdao.com/dictvoice?audio=字&type=1"),
    (1, "爸爸", "bà ba", "ba4 ba", "ba4 ba", "father; dad", "noun", "https://dict.youdao.com/dictvoice?audio=爸爸&type=1"),
    (1, "妈妈", "mā ma", "ma1 ma", "ma1 ma", "mother; mom", "noun", "https://dict.youdao.com/dictvoice?audio=妈妈&type=1"),
    (1, "朋友", "péng you", "peng2 you", "peng2 you", "friend", "noun", "https://dict.youdao.com/dictvoice?audio=朋友&type=1"),
    (1, "喜欢", "xǐ huan", "xi3 huan", "xi3 huan", "to like", "verb", "https://dict.youdao.com/dictvoice?audio=喜欢&type=1"),
    (1, "爱", "ài", "ai4", "ai4", "to love", "verb", "https://dict.youdao.com/dictvoice?audio=爱&type=1"),
    (1, "想", "xiǎng", "xiang3", "xiang3", "to think; to want; to miss", "verb", "https://dict.youdao.com/dictvoice?audio=想&type=1"),
    (1, "知道", "zhī dào", "zhi1 dao4", "zhi1 dao4", "to know", "verb", "https://dict.youdao.com/dictvoice?audio=知道&type=1"),
    (1, "要", "yào", "yao4", "yao4", "to want; to need; will (future)", "verb", "https://dict.youdao.com/dictvoice?audio=要&type=1"),
    (1, "可以", "kě yǐ", "ke3 yi3", "ke3 yi3", "can; may; okay", "verb", "https://dict.youdao.com/dictvoice?audio=可以&type=1"),
    (1, "能", "néng", "neng2", "neng2", "can; to be able to", "verb", "https://dict.youdao.com/dictvoice?audio=能&type=1"),
    (1, "会", "huì", "hui4", "hui4", "can; to know how to; will", "verb", "https://dict.youdao.com/dictvoice?audio=会&type=1"),
    (1, "地方", "dì fang", "di4 fang", "di4 fang", "place", "noun", "https://dict.youdao.com/dictvoice?audio=地方&type=1"),
    (1, "东西", "dōng xi", "dong1 xi", "dong1 xi", "thing; stuff", "noun", "https://dict.youdao.com/dictvoice?audio=东西&type=1"),
    (1, "时间", "shí jiān", "shi2 jian1", "shi2 jian1", "time", "noun", "https://dict.youdao.com/dictvoice?audio=时间&type=1"),
    (1, "问题", "wèn tí", "wen4 ti2", "wen4 ti2", "question; problem", "noun", "https://dict.youdao.com/dictvoice?audio=问题&type=1"),
    (1, "回答", "huí dá", "hui2 da2", "hui2 da2", "to answer; answer", "verb", "https://dict.youdao.com/dictvoice?audio=回答&type=1"),
    (1, "开", "kāi", "kai1", "kai1", "to open; to drive", "verb", "https://dict.youdao.com/dictvoice?audio=开&type=1"),
    (1, "关", "guān", "guan1", "guan1", "to close; to turn off", "verb", "https://dict.youdao.com/dictvoice?audio=关&type=1"),
    (1, "门", "mén", "men2", "men2", "door", "noun", "https://dict.youdao.com/dictvoice?audio=门&type=1"),
    (1, "口", "kǒu", "kou3", "kou3", "mouth", "noun", "https://dict.youdao.com/dictvoice?audio=口&type=1"),
    (1, "手", "shǒu", "shou3", "shou3", "hand", "noun", "https://dict.youdao.com/dictvoice?audio=手&type=1"),
    (1, "头", "tóu", "tou2", "tou2", "head", "noun", "https://dict.youdao.com/dictvoice?audio=头&type=1"),
    (1, "身体", "shēn tǐ", "shen1 ti3", "shen1 ti3", "body; health", "noun", "https://dict.youdao.com/dictvoice?audio=身体&type=1"),
    (1, "高", "gāo", "gao1", "gao1", "tall; high", "adjective", "https://dict.youdao.com/dictvoice?audio=高&type=1"),
    (1, "长", "cháng", "chang2", "chang2", "long; length", "adjective", "https://dict.youdao.com/dictvoice?audio=长&type=1"),
    (1, "新", "xīn", "xin1", "xin1", "new", "adjective", "https://dict.youdao.com/dictvoice?audio=新&type=1"),
    (1, "老", "lǎo", "lao3", "lao3", "old; experienced", "adjective", "https://dict.youdao.com/dictvoice?audio=老&type=1"),
    (1, "对", "duì", "dui4", "dui4", "correct; right; to", "adjective", "https://dict.youdao.com/dictvoice?audio=对&type=1"),
    (1, "错", "cuò", "cuo4", "cuo4", "wrong; mistake", "adjective", "https://dict.youdao.com/dictvoice?audio=错&type=1"),
    (1, "漂亮", "piào liang", "piao4 liang", "piao4 liang", "beautiful; pretty", "adjective", "https://dict.youdao.com/dictvoice?audio=漂亮&type=1"),
    (1, "高兴", "gāo xìng", "gao1 xing4", "gao1 xing4", "happy; glad", "adjective", "https://dict.youdao.com/dictvoice?audio=高兴&type=1"),
    (1, "累", "lèi", "lei4", "lei4", "tired", "adjective", "https://dict.youdao.com/dictvoice?audio=累&type=1"),
    (1, "忙", "máng", "mang2", "mang2", "busy", "adjective", "https://dict.youdao.com/dictvoice?audio=忙&type=1"),
    (1, "冷", "lěng", "leng3", "leng3", "cold", "adjective", "https://dict.youdao.com/dictvoice?audio=冷&type=1"),
    (1, "热", "rè", "re4", "re4", "hot", "adjective", "https://dict.youdao.com/dictvoice?audio=热&type=1"),
    (1, "快", "kuài", "kuai4", "kuai4", "fast; quick", "adjective", "https://dict.youdao.com/dictvoice?audio=快&type=1"),
    (1, "慢", "màn", "man4", "man4", "slow", "adjective", "https://dict.youdao.com/dictvoice?audio=慢&type=1"),
    (1, "贵", "guì", "gui4", "gui4", "expensive", "adjective", "https://dict.youdao.com/dictvoice?audio=贵&type=1"),
    (1, "便宜", "pián yi", "pian2 yi", "pian2 yi", "cheap", "adjective", "https://dict.youdao.com/dictvoice?audio=便宜&type=1"),
    (1, "好吃", "hǎo chī", "hao3 chi1", "hao3 chi1", "delicious; tasty", "adjective", "https://dict.youdao.com/dictvoice?audio=好吃&type=1"),
    (1, "一", "yī", "yi1", "yi1", "one", "number", "https://dict.youdao.com/dictvoice?audio=一&type=1"),
    (1, "二", "èr", "er4", "er4", "two", "number", "https://dict.youdao.com/dictvoice?audio=二&type=1"),
    (1, "三", "sān", "san1", "san1", "three", "number", "https://dict.youdao.com/dictvoice?audio=三&type=1"),
    (1, "四", "sì", "si4", "si4", "four", "number", "https://dict.youdao.com/dictvoice?audio=四&type=1"),
    (1, "五", "wǔ", "wu3", "wu3", "five", "number", "https://dict.youdao.com/dictvoice?audio=五&type=1"),
    (1, "六", "liù", "liu4", "liu4", "six", "number", "https://dict.youdao.com/dictvoice?audio=六&type=1"),
    (1, "七", "qī", "qi1", "qi1", "seven", "number", "https://dict.youdao.com/dictvoice?audio=七&type=1"),
    (1, "八", "bā", "ba1", "ba1", "eight", "number", "https://dict.youdao.com/dictvoice?audio=八&type=1"),
    (1, "九", "jiǔ", "jiu3", "jiu3", "nine", "number", "https://dict.youdao.com/dictvoice?audio=九&type=1"),
    (1, "十", "shí", "shi2", "shi2", "ten", "number", "https://dict.youdao.com/dictvoice?audio=十&type=1"),
    (1, "百", "bǎi", "bai3", "bai3", "hundred", "number", "https://dict.youdao.com/dictvoice?audio=百&type=1"),
    (1, "千", "qiān", "qian1", "qian1", "thousand", "number", "https://dict.youdao.com/dictvoice?audio=千&type=1"),
    (1, "万", "wàn", "wan4", "wan4", "ten thousand", "number", "https://dict.youdao.com/dictvoice?audio=万&type=1"),
    (1, "第一", "dì yī", "di4 yi1", "di4 yi1", "first", "number", "https://dict.youdao.com/dictvoice?audio=第一&type=1"),
    (1, "开始", "kāi shǐ", "kai1 shi3", "kai1 shi3", "to begin; start", "verb", "https://dict.youdao.com/dictvoice?audio=开始&type=1"),
    (1, "结束", "jié shù", "jie2 shu4", "jie2 shu4", "to end; finish", "verb", "https://dict.youdao.com/dictvoice?audio=结束&type=1"),
    (1, "等", "děng", "deng3", "deng3", "to wait; etc.", "verb", "https://dict.youdao.com/dictvoice?audio=等&type=1"),
    (1, "找", "zhǎo", "zhao3", "zhao3", "to look for; to find", "verb", "https://dict.youdao.com/dictvoice?audio=找&type=1"),
    (1, "给", "gěi", "gei3", "gei3", "to give", "verb", "https://dict.youdao.com/dictvoice?audio=给&type=1"),
    (1, "让", "ràng", "rang4", "rang4", "to let; to allow", "verb", "https://dict.youdao.com/dictvoice?audio=让&type=1"),
    (1, "请", "qǐng", "qing3", "qing3", "please; to invite", "verb", "https://dict.youdao.com/dictvoice?audio=请&type=1"),
    (1, "帮", "bāng", "bang1", "bang1", "to help", "verb", "https://dict.youdao.com/dictvoice?audio=帮&type=1"),
    (1, "告诉", "gào su", "gao4 su", "gao4 su", "to tell; to inform", "verb", "https://dict.youdao.com/dictvoice?audio=告诉&type=1"),
    (1, "问", "wèn", "wen4", "wen4", "to ask", "verb", "https://dict.youdao.com/dictvoice?audio=问&type=1"),
    (1, "认识", "rèn shi", "ren4 shi", "ren4 shi", "to know (a person); to recognize", "verb", "https://dict.youdao.com/dictvoice?audio=认识&type=1"),
    (1, "觉得", "jué de", "jue2 de", "jue2 de", "to feel; to think", "verb", "https://dict.youdao.com/dictvoice?audio=觉得&type=1"),
    (1, "希望", "xī wàng", "xi1 wang4", "xi1 wang4", "to hope; hope", "verb", "https://dict.youdao.com/dictvoice?audio=希望&type=1"),
    (1, "欢迎", "huān yíng", "huan1 ying2", "huan1 ying2", "to welcome", "verb", "https://dict.youdao.com/dictvoice?audio=欢迎&type=1"),
    (1, "对不起", "duì bu qǐ", "dui4 bu qi3", "dui4 bu qi3", "sorry; excuse me", "phrase", "https://dict.youdao.com/dictvoice?audio=对不起&type=1"),
    (1, "没关系", "méi guān xi", "mei2 guan1 xi", "mei2 guan1 xi", "it doesn't matter; never mind", "phrase", "https://dict.youdao.com/dictvoice?audio=没关系&type=1"),
    (1, "不用", "bú yòng", "bu2 yong4", "bu2 yong4", "no need; don't have to", "verb", "https://dict.youdao.com/dictvoice?audio=不用&type=1"),
    (1, "欢迎", "huān ying", "huan1 ying2", "huan1 ying2", "welcome", "interjection", "https://dict.youdao.com/dictvoice?audio=欢迎&type=1"),
    (1, "欢迎", "huān ying", "huan1 ying2", "huan1 ying2", "welcome", "interjection", "https://dict.youdao.com/dictvoice?audio=欢迎&type=1"),
]


def populate_database():
    """Populate the database with sample vocabulary"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if words table exists
        cursor.execute("SHOW TABLES LIKE 'words'")
        if not cursor.fetchone():
            logger.error("Words table does not exist. Please run the main application first to create tables.")
            return False
        
        # Check if words already exist
        cursor.execute("SELECT COUNT(*) FROM words")
        count = cursor.fetchone()[0]
        
        if count > 0:
            logger.info(f"Database already contains {count} words. Skipping population.")
            return True
        
        # Insert sample words
        insert_query = """
            INSERT INTO words (level, hanzi, pinyin, pinyin_tone, pinyin_num, english, pos, tts_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_query, HSK_WORDS)
        conn.commit()
        
        logger.info(f"Successfully inserted {len(HSK_WORDS)} words into the database.")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM words")
        new_count = cursor.fetchone()[0]
        logger.info(f"Total words in database: {new_count}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error populating database: {e}")
        return False


if __name__ == "__main__":
    print("Chinese Self Learning System - Database Population Script")
    print("=" * 60)
    
    success = populate_database()
    
    if success:
        print("\n✓ Database population completed successfully!")
        print("You can now use the search and flashcard features.")
    else:
        print("\n✗ Database population failed. Please check the errors above.")
    
    print("=" * 60)