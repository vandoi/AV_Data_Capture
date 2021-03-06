import json
import os.path
import re
import shutil
import platform

from PIL import Image
from ADC_function import *

# =========website========
from WebCrawler import airav
from WebCrawler import avsox
from WebCrawler import fanza
from WebCrawler import fc2
from WebCrawler import jav321
from WebCrawler import javbus
from WebCrawler import javdb
from WebCrawler import mgstage
from WebCrawler import xcity
from WebCrawler import javlib
from WebCrawler import dlsite

# ========porn========
from WebCrawler import badoinkvr

def escape_path(path, escape_literals: str):  # Remove escape literals
    backslash = '\\'
    for literal in escape_literals:
        path = path.replace(backslash + literal, '')
    return path


def moveFailedFolder(filepath, failed_folder):
    print('[-]Move to Failed output folder')
    shutil.move(filepath, str(os.getcwd()) + '/' + failed_folder + '/')
    return 


def CreatFailedFolder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make Failed output folder\n[-](Please run as Administrator)")
            return 


def get_data_from_json(file_number, liuchu, leakcode, filepath, conf: config.Config):  # 从JSON返回元数据
    """
    iterate through all services and fetch the data 
    """

    func_mapping = {
        "airav": airav.main,
        "avsox": avsox.main,
        "fc2": fc2.main,
        "fanza": fanza.main,
        "javdb": javdb.main,
        "javbus": javbus.main,
        "mgstage": mgstage.main,
        "jav321": jav321.main,
        "xcity": xcity.main,
        "javlib": javlib.main,
        "dlsite": dlsite.main,
    }

    # default fetch order list, from the beginning to the end
    sources = conf.sources().split(',')

    # if the input file name matches certain rules,
    # move some web service to the beginning of the list
    if "avsox" in sources and (re.match(r"^\d{5,}", file_number) or
        "HEYZO" in file_number or "heyzo" in file_number or "Heyzo" in file_number
    ):
        sources.insert(0, sources.pop(sources.index("avsox")))
    elif "mgstage" in sources and (re.match(r"\d+\D+", file_number) or
        "siro" in file_number or "SIRO" in file_number or "Siro" in file_number
    ):
        sources.insert(0, sources.pop(sources.index("mgstage")))
    elif "fc2" in sources and ("fc2" in file_number or "FC2" in file_number
    ):
        sources.insert(0, sources.pop(sources.index("fc2")))
    elif "dlsite" in sources and (
        "RJ" in file_number or "rj" in file_number or "VJ" in file_number or "vj" in file_number
    ):
        sources.insert(0, sources.pop(sources.index("dlsite")))

    print("[!]Sources order: {}".format(sources))
    json_data = {}
    for source in sources:
        try:
            if conf.debug() == True:
                print('[+]select',source)
            json_data = json.loads(func_mapping[source](file_number))
            # if any service return a valid return, break
            if get_data_state(json_data):
                break
        except Exception as e:
            print('[-]Error occured when getting data from {}: {}'.format(source, str(e)))
            # break

    # Return if data not found in all sources
    if not get_data_state(json_data):
        print('[-]Movie Data not found!')
        if conf.failed_move():
            moveFailedFolder(filepath, conf.failed_folder())
        return

    # ================================================网站规则添加结束================================================

    title = json_data.get('title')
    actor_list = str(json_data.get('actor')).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    release = json_data.get('release')
    number = json_data.get('number')
    studio = json_data.get('studio')
    source = json_data.get('source')
    runtime = json_data.get('runtime')
    outline = json_data.get('outline')
    label = json_data.get('label')
    series = json_data.get('series')
    year = json_data.get('year')

    if json_data.get('cover_small') == None:
        cover_small = ''
    else:
        cover_small = json_data.get('cover_small')
        
    imagecut = json_data.get('imagecut')
    tag = str(json_data.get('tag')).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    if title == '' or number == '':
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
    title = title.replace('\\', '')
    title = title.replace('/', '')
    title = title.replace(':', '')
    title = title.replace('*', '')
    title = title.replace('?', '')
    title = title.replace('"', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('|', '')
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')

    # ====================处理异常字符 END================== #\/:*?"<>|

    # ===  替换Studio片假名
    studio = studio.replace('アイエナジー','Energy')
    studio = studio.replace('アイデアポケット','Idea Pocket')
    studio = studio.replace('アキノリ','AKNR')
    studio = studio.replace('アタッカーズ','Attackers')
    studio = re.sub('アパッチ.*','Apache',studio)
    studio = studio.replace('アマチュアインディーズ','SOD')
    studio = studio.replace('アリスJAPAN','Alice Japan')
    studio = studio.replace('オーロラプロジェクト・アネックス','Aurora Project Annex')
    studio = studio.replace('クリスタル映像','Crystal 映像')
    studio = studio.replace('グローリークエスト','Glory Quest')
    studio = studio.replace('ダスッ！','DAS！')
    studio = studio.replace('ディープス','DEEP’s')
    studio = studio.replace('ドグマ','Dogma')
    studio = studio.replace('プレステージ','PRESTIGE')
    studio = studio.replace('ムーディーズ','MOODYZ')
    studio = studio.replace('メディアステーション','宇宙企画')
    studio = studio.replace('ワンズファクトリー','WANZ FACTORY')
    studio = studio.replace('エスワン ナンバーワンスタイル','S1')
    studio = studio.replace('エスワンナンバーワンスタイル','S1')
    studio = studio.replace('SODクリエイト','SOD')
    studio = studio.replace('サディスティックヴィレッジ','SOD')
    studio = studio.replace('V＆Rプロダクツ','V＆R PRODUCE')
    studio = studio.replace('V＆RPRODUCE','V＆R PRODUCE')
    studio = studio.replace('レアルワークス','Real Works')
    studio = studio.replace('マックスエー','MAX-A')
    studio = studio.replace('ピーターズMAX','PETERS MAX')
    studio = studio.replace('プレミアム','PREMIUM')
    studio = studio.replace('ナチュラルハイ','NATURAL HIGH')
    studio = studio.replace('マキシング','MAXING')
    studio = studio.replace('エムズビデオグループ','M’s Video Group')
    studio = studio.replace('ミニマム','Minimum')
    studio = studio.replace('ワープエンタテインメント','WAAP Entertainment')
    # added studio name translation for uncensor studio
    studio = studio.replace('カリビアンコム','Caribbean')
    studio = re.sub('.*/妄想族','妄想族',studio)
    studio = studio.replace('/',' ')
    # ===  替换Studio片假名 END
    
    # patch file name with publisher (if necessary)
    if conf.add_studio_to_number():
        number = patch_studio_name_to_filename(studio, number)
        json_data['number'] = number

    location_rule = eval(conf.location_rule())

    if 'actor' in conf.location_rule() and len(actor) > 100:
        print(conf.location_rule())
        location_rule = eval(conf.location_rule().replace("actor","'多人作品'"))
    maxlen = conf.max_title_len()
    if 'title' in conf.location_rule() and len(title) > maxlen:
        shorttitle = title[0:maxlen]
        location_rule = location_rule.replace(title, shorttitle)

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['filename'] = number # this tag is for porn, for jav, we simply use number as filename
    json_data['location_rule'] = location_rule
    json_data['year'] = year
    json_data['actor_list'] = actor_list
    if liuchu == '流出':
        json_data['leak_code'] = leakcode
    if conf.is_translate():
        translate_values = conf.translate_values().split(",")
        for translate_value in translate_values:
            json_data[translate_value] = translate(json_data[translate_value], target_language=conf.translate_language())
    naming_rule=""

    if liuchu == '流出' and len(leakcode) > 0:
        naming_rule_to_use = conf.leak_naming_rule()
    else:
        naming_rule_to_use = conf.naming_rule()

    for i in naming_rule_to_use.split("+"):
        if i not in json_data:
            naming_rule += i.strip("'").strip('"')
        else:
            naming_rule += json_data.get(i)
    json_data['naming_rule'] = naming_rule
    return json_data

def get_data_from_json_porn(file_number, filepath, conf: config.Config):  # 从JSON返回元数据
    """
    iterate through all services and fetch the data 
    """

    func_mapping = {
        "badoinkvr": badoinkvr.main,
    }

    # default fetch order list, from the beginning to the end
    sources = conf.porn_sources().split(',')

    print("[!]Sources order: {}".format(sources))
    json_data = {}
    for source in sources:
        try:
            if conf.debug() == True:
                print('[+]select',source)
            json_data = json.loads(func_mapping[source](file_number))
            # if any service return a valid return, break
            if get_data_state(json_data):
                break
        except Exception as e:
            print('[-]Error occured when getting data from {}: {}'.format(source, str(e)))
            # break

    # Return if data not found in all sources
    if not get_data_state(json_data):
        print('[-]Movie Data not found!')
        if conf.failed_move():
            moveFailedFolder(filepath, conf.failed_folder())
        return

    # ================================================网站规则添加结束================================================
    print("json_data: {}".format(json_data))
    title = json_data['title']
    # if 'actor' in json_data.keys():
    actor_list = str(json_data['actor']).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    release = json_data['release']
    number = json_data['number']
    studio = json_data['studio']
    source = json_data['source']
    runtime = json_data['runtime']
    outline = json_data['outline']
    label = json_data['label']
    series = json_data['series']
    year = json_data['year']
    try:
        cover_small = json_data['cover_small']
    except:
        cover_small = ''
    imagecut = json_data['imagecut']
    tag = str(json_data['tag']).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    actor = ','.join(actor_list)

    if title == '' or number == '':
        print('[-]Movie Data not found!')
        moveFailedFolder(filepath, conf.failed_folder())
        return

    # if imagecut == '3':
    #     DownloadFileWithFilename()

    # ====================处理异常字符====================== #\/:*?"<>|
    title = title.replace('\\', '')
    title = title.replace('/', '')
    title = title.replace(':', '')
    title = title.replace('*', '')
    title = title.replace('?', '')
    title = title.replace('"', '')
    title = title.replace('<', '')
    title = title.replace('>', '')
    title = title.replace('|', '')
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')
    # ====================处理异常字符 END================== #\/:*?"<>|
    
    # patch file name with publisher (if necessary)
    if conf.add_studio_to_number():
        number = patch_studio_name_to_filename(studio, number)
        json_data['number'] = number

    location_rule = eval(conf.porn_location_rule())

    # Process only Windows.
    if platform.system() == "Windows":
        if 'actor' in conf.location_rule() and len(actor) > 100:
            print(conf.location_rule())
            location_rule = eval(conf.location_rule().replace("actor","'多人作品'"))
        maxlen = conf.max_title_len()
        if 'title' in conf.location_rule() and len(title) > maxlen:
            shorttitle = title[0:maxlen]
            location_rule = location_rule.replace(title, shorttitle)

    # keep filename original
    if conf.porn_is_keep_name_original():
        filename, ext = os.path.splitext(os.path.basename(filepath))
    else:
        filename = eval(conf.porn_naming_rule())

    # 返回处理后的json_data
    json_data['title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['filename'] = filename
    json_data['naming_rule'] = eval(conf.porn_naming_rule())
    json_data['location_rule'] = location_rule
    json_data['year'] = year
    json_data['actor_list'] = actor_list
    return json_data

def get_info(json_data):  # 返回json里的数据
    title = json_data.get('title')
    studio = json_data.get('studio')
    year = json_data.get('year')
    outline = json_data.get('outline')
    runtime = json_data.get('runtime')
    director = json_data.get('director')
    actor_photo = json_data.get('actor_photo')
    release = json_data.get('release')
    number = json_data.get('number')
    cover = json_data.get('cover')
    website = json_data.get('website')
    series = json_data.get('series')
    label = json_data.get('label', "")
    return title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label


def small_cover_check(path, number, cover_small, conf: config.Config, filepath, failed_folder):
    download_file_with_filename(cover_small, number + '-poster.jpg', path, conf, filepath, failed_folder)
    print('[+]Image Downloaded! ' + path + '/' + number + '-poster.jpg')


def create_folder(success_folder, location_rule, json_data, conf: config.Config):  # 创建文件夹
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label = get_info(json_data)
    if len(location_rule) > 240:  # 新建成功输出文件夹
        path = success_folder + '/' + location_rule.replace("'actor'", "'manypeople'", 3).replace("actor","'manypeople'",3)  # path为影片+元数据所在目录
    else:
        path = success_folder + '/' + location_rule
    path = trimblank(path)
    if not os.path.exists(path):
        path = escape_path(path, conf.escape_literals())
        try:
            os.makedirs(path)
        except:
            path = success_folder + '/' + location_rule.replace('/[' + number + ')-' + title, "/number")
            path = escape_path(path, conf.escape_literals())

            os.makedirs(path)
    return path


def trimblank(s: str):
    """
    Clear the blank on the right side of the folder name
    """
    if s[-1] == " ":
        return trimblank(s[:-1])
    else:
        return s

# =====================资源下载部分===========================

# path = examle:photo , video.in the Project Folder!
def download_file_with_filename(url, filename, path, conf: config.Config, filepath, failed_folder):
    switch, proxy, timeout, retry_count, proxytype = config.Config().proxy()

    for i in range(retry_count):
        try:
            if switch == 1 or switch == '1':
                if not os.path.exists(path):
                    os.makedirs(path)
                proxies = get_proxy(proxy, proxytype)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                r = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
                if r == '':
                    print('[-]Movie Data not found!')
                    return 
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
            else:
                if not os.path.exists(path):
                    os.makedirs(path)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
                r = requests.get(url, timeout=timeout, headers=headers)
                if r == '':
                    print('[-]Movie Data not found!')
                    return 
                with open(str(path) + "/" + filename, "wb") as code:
                    code.write(r.content)
                return
        except requests.exceptions.RequestException:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ConnectionError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ProxyError:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
        except requests.exceptions.ConnectTimeout:
            i += 1
            print('[-]Image Download :  Connect retry ' + str(i) + '/' + str(retry_count))
    print('[-]Connect Failed! Please check your Proxy or Network!')
    moveFailedFolder(filepath, failed_folder)
    return


# 封面是否下载成功，否则移动到failed
def image_download(cover, number, path, conf: config.Config, filepath, failed_folder):
    if download_file_with_filename(cover, number + '-fanart.jpg', path, conf, filepath, failed_folder) == 'failed':
        moveFailedFolder(filepath, failed_folder)
        return

    switch, _proxy, _timeout, retry, _proxytype = conf.proxy()
    for i in range(retry):
        if os.path.getsize(path + '/' + number + '-fanart.jpg') == 0:
            print('[!]Image Download Failed! Trying again. [{}/3]', i + 1)
            download_file_with_filename(cover, number + '-fanart.jpg', path, conf, filepath, failed_folder)
            continue
        else:
            break
    if os.path.getsize(path + '/' + number + '-fanart.jpg') == 0:
        return
    print('[+]Image Downloaded!', path + '/' + number + '-fanart.jpg')
    shutil.copyfile(path + '/' + number + '-fanart.jpg',path + '/' + number + '-thumb.jpg')


def print_files(path, filename, naming_rule, cn_sub, json_data, filepath, failed_folder, tag, actor_list, liuchu, leakcode):
    title, studio, year, outline, runtime, director, actor_photo, release, number, cover, website, series, label = get_info(json_data)
    output_path = path + "/" + filename + ".nfo"

    try:
        if not os.path.exists(path):
            os.makedirs(path)
        with open(output_path, "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            print(" <title>" + naming_rule + "</title>", file=code)
            print("  <set>", file=code)
            print("  </set>", file=code)
            print("  <studio>" + studio + "+</studio>", file=code)
            print("  <year>" + year + "</year>", file=code)
            print("  <outline>" + outline + "</outline>", file=code)
            print("  <plot>" + outline + "</plot>", file=code)
            print("  <runtime>" + str(runtime).replace(" ", "") + "</runtime>", file=code)
            print("  <director>" + director + "</director>", file=code)
            print("  <poster>" + filename + "-poster.jpg</poster>", file=code)
            print("  <thumb>" + filename + "-thumb.jpg</thumb>", file=code)
            print("  <fanart>" + filename + '-fanart.jpg' + "</fanart>", file=code)
            try:
                for key in actor_list:
                    print("  <actor>", file=code)
                    print("   <name>" + key + "</name>", file=code)
                    print("  </actor>", file=code)
            except:
                aaaa = ''
            print("  <maker>" + studio + "</maker>", file=code)
            print("  <label>" + label + "</label>", file=code)
            if cn_sub == '1':
                print("  <tag>中文字幕</tag>", file=code)
            if liuchu == '流出':
                print("  <tag>流出</tag>", file=code)
            try:
                for i in tag:
                    print("  <tag>" + i + "</tag>", file=code)
                print("  <tag>" + series + "</tag>", file=code)
            except:
                aaaaa = ''
            try:
                for i in tag:
                    print("  <genre>" + i + "</genre>", file=code)
            except:
                aaaaaaaa = ''
            if cn_sub == '1':
                print("  <genre>中文字幕</genre>", file=code)
            print("  <num>" + number + "</num>", file=code)
            if len(leakcode) > 0:
                print("  <leakcode>" + leakcode + "</leakcode>", file=code)
            print("  <premiered>" + release + "</premiered>", file=code)
            print("  <cover>" + cover + "</cover>", file=code)
            print("  <website>" + website + "</website>", file=code)
            print("</movie>", file=code)
            print("[+]Wrote!            " + output_path)
    except IOError as e:
        print("[-]Write Failed!")
        print(e)
        moveFailedFolder(filepath, failed_folder)
        return
    except Exception as e1:
        print(e1)
        print("[-]Write Failed!")
        moveFailedFolder(filepath, failed_folder)
        return


def cutImage(imagecut, path, number):
    if imagecut == 1: # 剪裁大封面
        try:
            img = Image.open(path + '/' + number  + '-fanart.jpg')
            imgSize = img.size
            w = img.width
            h = img.height
            img2 = img.crop((w - h / 1.5, 0, w, h))
            img2.save(path + '/' + number  + '-poster.jpg')
            print('[+]Image Cutted!     ' + path + '/' + number  + '-poster.jpg')
        except:
            print('[-]Cover cut failed!')
    elif imagecut == 0: # 复制封面
        shutil.copyfile(path + '/' + number  + '-fanart.jpg',path + '/' + number  + '-poster.jpg')
        print('[+]Image Copyed!     ' + path + '/' + number + '-poster.jpg')

def _safe_move(src, target):
    if os.path.exists(target):
        raise FileExistsError()
    else:
        shutil.move(src, target)

def paste_file_to_folder(filepath, path, new_filename, conf: config.Config):  # 文件路径，番号，后缀，要移动至的位置
    houzhui = str(re.search('[.](iso|ISO|AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|WEBM|avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm)$', filepath).group())

    filename = os.path.basename(filepath)
    filename_no_ext, file_ext = os.path.splitext(filename)
    target_path = path + '/' + new_filename + houzhui

    if conf.debug() == True:
        print("[!]Debug: move {} to {}".format(filepath, target_path))
        return

    try:
        # 如果soft_link=1 使用软链接
        if conf.soft_link():
            os.symlink(filepath, target_path)
        else:
            _safe_move(filepath, target_path)
        if os.path.exists(os.getcwd() + '/' + filename + '.srt'):  # 字幕移动
            _safe_move(os.getcwd() + '/' + filename + '.srt', path + '/' + new_filename + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + filename + '.ssa'):
            _safe_move(os.getcwd() + '/' + filename + '.ssa', path + '/' + new_filename + '.ssa')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + filename + '.sub'):
            _safe_move(os.getcwd() + '/' + filename + '.sub', path + '/' + new_filename + '.sub')
            print('[+]Sub moved!')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        return 
    except shutil.Error as err:
        print("[-]Unable to move file '{}', reason: {}".format(filepath, err))
        return

def paste_file_to_folder_keep_name_original(filepath, path, conf: config.Config):  # 文件路径，番号，后缀，要移动至的位置
    # houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|WEBM|avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm)$', filepath).group())

    filename = os.path.basename(filepath)
    filename_no_ext, file_ext = os.path.splitext(filename)
    target_path = path + '/' + filename
    if conf.debug() == True:
        print("[!]Debug: move {} to {}".format(filepath, target_path))
        return

    try:
        # 如果soft_link=1 使用软链接
        if conf.soft_link():
            os.symlink(filepath, target_path)
        else:
            _safe_move(filepath, target_path)
        
        if os.path.exists(os.getcwd() + '/' + filename + '.srt'):  # 字幕移动
            _safe_move(os.getcwd() + '/' + filename + '.srt', path + '/' + filename + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + filename + '.ssa'):
            _safe_move(os.getcwd() + '/' + filename + '.ssa', path + '/' + filename + '.ssa')
            print('[+]Sub moved!')
        elif os.path.exists(os.getcwd() + '/' + filename + '.sub'):
            _safe_move(os.getcwd() + '/' + filename + '.sub', path + '/' + filename + '.sub')
            print('[+]Sub moved!')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        return 
    except shutil.Error as err:
        print("[-]Unable to move file '{}', reason: {}".format(filepath, err))
        return

def paste_file_to_folder_mode2(filepath, path, multi_part, filename, conf):  # 文件路径，番号，后缀，要移动至的位置
    # if multi_part == 1:
    #     number += part  # 这时number会被附加上CD1后缀
    houzhui = str(re.search('[.](AVI|RMVB|WMV|MOV|MP4|MKV|FLV|TS|WEBM|avi|rmvb|wmv|mov|mp4|mkv|flv|ts|webm)$', filepath).group())

    if conf.debug() == True:
        print("[!]Debug: move {} to {}".format(filepath, path + '/' + number + c_word + houzhui))
        return

    try:
        if conf.soft_link():
            os.symlink(filepath, path + '/' + number + part + c_word + houzhui)
        else:
            os.rename(filepath, path + '/' + number + part + c_word + houzhui)
        if os.path.exists(number + '.srt'):  # 字幕移动
            os.rename(number + part + c_word + '.srt', path + '/' + number + part + c_word + '.srt')
            print('[+]Sub moved!')
        elif os.path.exists(number + part + c_word + '.ass'):
            os.rename(number + part + c_word + '.ass', path + '/' + number + part + c_word + '.ass')
            print('[+]Sub moved!')
        elif os.path.exists(number + part + c_word + '.sub'):
            os.rename(number + part + c_word + '.sub', path + '/' + number + part + c_word + '.sub')
            print('[+]Sub moved!')
        print('[!]Success')
    except FileExistsError:
        print('[-]File Exists! Please check your movie!')
        print('[-]move to the root folder of the program.')
        return 
    except PermissionError:
        print('[-]Error! Please run as administrator!')
        return

def get_part(filepath, failed_folder):
    try:
        if re.search('-CD\d+', filepath):
            return re.findall('-CD\d+', filepath)[0]
        if re.search('-cd\d+', filepath):
            return re.findall('-cd\d+', filepath)[0]
    except:
        print("[-]failed!Please rename the filename again!")
        moveFailedFolder(filepath, failed_folder)
        return

def debug_print(data: json):
    try:
        print("[+] ---Debug info---")
        for i, v in data.items():
            if i == 'outline':
                print('[+]  -', i, '    :', len(v), 'characters')
                continue
            if i == 'actor_photo' or i == 'year':
                continue
            print('[+]  -', "%-11s" % i, ':', v)

        print("[+] ---Debug info---")
    except:
        pass

# for uncensored video, patch studio name to file name
def patch_studio_name_to_filename(studio, filename):
    unsensor_publisher = {
        'Caribbean': 'Caribbean',
        '一本道': '1Pondo',
        '一本道 ( 1pondo )': '1Pondo',
        '東京熱': 'Tokyo-Hot'
    }
    results = list(filter(lambda x: (x in studio), unsensor_publisher.keys()))
    print("[+]Found matched prefix for studio: {}".format(results))
    if len(results) >= 1:
        publisher = unsensor_publisher[results[0]]
        print("[+]Patch filename to {}".format(publisher + '-' + filename))
        return publisher + '-' + filename
    else:
        return filename

##
# core_main
# mode (str): mode of search, e.g. jav, porn, etc.
# @return: str, the path that movies moved to
def core_main(file_path, number_th, conf: config.Config, mode: 'jav'):
    # =======================================================================初始化所需变量
    multi_part = 0
    part = ''
    c_word = ''
    cn_sub = ''
    liuchu = ''

    filepath = file_path  # 影片的路径
    number = number_th

    # Add liuchu tag and store the leak code after leak / 流出
    # file name format: EBOD-203_leak_FC2PPV-1224191
    filename = os.path.splitext(filepath)[0]
    leakcode = ''
    if '流出' in filename:
        liuchu = '流出'
        leakcode = filename.partition("_流出_")[2].partition("-CD")[0] # remove CD multi-part in leakcode
    if 'leak' in filename:
        liuchu = '流出'
        leakcode = filename.partition("_leak_")[2].partition("-CD")[0] # remove CD multi-part in leakcode

    json_data = {}
    if mode == 'jav':
        json_data = get_data_from_json(number, liuchu, leakcode, filepath, conf)  # 定义番号
    elif mode == 'porn':
        json_data = get_data_from_json_porn(number, filepath, conf) # the number is keyword actually
    else:
        print("[-]Unknown core search mode: {}".format(mode))
        return

    # Return if blank dict returned (data not found)
    if not json_data:
        return

    if json_data["number"] != number:
        # fix issue #119
        # the root cause is we normalize the search id
        # print_files() will use the normalized id from website,
        # but paste_file_to_folder() still use the input raw search id
        # so the solution is: use the normalized search id
        number = json_data["number"]

    imagecut =  json_data.get('imagecut')
    tag =  json_data.get('tag')

    given_filename = json_data.get('filename')
    # =======================================================================判断-C,-CD后缀
    if '-CD' in filepath or '-cd' in filepath:
        multi_part = 1
        part = get_part(filepath, conf.failed_folder())

    # Combine and generate filename here
    # instead of passing number + c_word + part to other functions again and again
    filename = os.path.basename(filepath)
    multi_part_num_re = re.compile(".*(-|_)([0-9])\.")
    results_num = multi_part_num_re.findall(filename)
    print(results_num)
    if len(results_num) > 0:
        multi_part = 1
        results_num = results_num[0]
        num = results_num[1] # the second capture group is multi-part letter
        part = '-CD' + num
    elif conf.multi_part_abc(): # add support to _A, _B, _C multi_part filename
        # sometimes directory name may contain '-A', we use filename instead
        multi_part_abc_re = re.compile(".*(-|_)([A-Za-z])\.")
        results_abc = multi_part_abc_re.findall(filename)
        if len(results_abc) > 0:
            multi_part = 1
            results_abc = results_abc[0]
            abc = results_abc[1].lower() # the second capture group is multi-part letter
            part = '-CD' + str(ord(abc) - 96)
    
    if not conf.multi_part_abc() and ('-c.' in filepath or '-C.' in filepath or '中文' in filepath or '字幕' in filepath):
        print("[+]Chinese subtitle video found, filepath: {}".format(filepath))
        cn_sub = '1'
        c_word = '-C'  # 中文字幕影片后缀

    # actual filename
    if liuchu == '流出':
        actual_filename = given_filename + "_leak_" + leakcode + c_word + part
    else:
        actual_filename = given_filename + c_word + part

    # 创建输出失败目录
    CreatFailedFolder(conf.failed_folder())

    # 调试模式检测
    if conf.debug():
        debug_print(json_data)

    # 创建文件夹
    path = create_folder(conf.success_folder(),  json_data.get('location_rule'), json_data, conf)

    # main_mode
    #  1: 刮削模式 / Scraping mode
    #  2: 整理模式 / Organizing mode
    if conf.main_mode() == 1:
        if multi_part == 1:
            number += part  # 这时number会被附加上CD1后缀

        # 检查小封面, 如果image cut为3，则下载小封面
        if imagecut == 3:
            small_cover_check(path, actual_filename, json_data['cover_small'], conf, filepath, conf.failed_folder())

        # creatFolder会返回番号路径
        image_download(json_data['cover'], actual_filename, path, conf, filepath, conf.failed_folder())

        # 裁剪图
        cutImage(imagecut, path, actual_filename)

        # 打印文件
        print_files(path, actual_filename, json_data['naming_rule'], cn_sub, json_data, filepath, conf.failed_folder(), tag, json_data['actor_list'], liuchu, leakcode)

        # 移动文件
        if mode == 'porn' and conf.porn_is_keep_name_original():
            paste_file_to_folder_keep_name_original(filepath, path, conf)
        else:
            paste_file_to_folder(filepath, path, actual_filename, conf)
    elif conf.main_mode() == 2:
        # 移动文件
        if mode == 'porn' and conf.porn_is_keep_name_original():
            paste_file_to_folder_keep_name_original(filepath, path, conf)
        else:
            paste_file_to_folder_mode2(filepath, path, multi_part, actual_filename, conf)

    return path
