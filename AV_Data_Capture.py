#!/usr/bin/env python3
import argparse
from core import *
import os
from number_parser import get_number
import zipfile

def check_update(local_version):
    data = json.loads(get_html("https://api.github.com/repos/yoshiko2/AV_Data_Capture/releases/latest"))

    remote = data["tag_name"]
    local = local_version

    if not local == remote:
        line1 = "* New update " + str(remote) + " *"
        print("[*]" + line1.center(54))
        print("[*]" + "↓ Download ↓".center(54))
        print("[*] https://github.com/yoshiko2/AV_Data_Capture/releases")
        print("[*]======================================================")


def argparse_function() -> [str, str, bool]:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", default='', nargs='?', help="Single Movie file path.")
    parser.add_argument("-c", "--config", default='config.ini', nargs='?', help="The config file Path.")
    parser.add_argument("-n", "--number", default='', nargs='?',help="Custom file number")
    args = parser.parse_args()

    return args.file, args.config, args.number

def movie_lists(root, escape_folder):
    for folder in escape_folder:
        if folder in root:
            return []
    total = []
    file_type = ['.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.MP4', '.AVI', '.RMVB', '.WMV','.MOV', '.MKV', '.FLV', '.TS', '.WEBM', '.iso','.ISO']
    dirs = os.listdir(root)
    for entry in dirs:
        f = os.path.join(root, entry)
        if os.path.isdir(f):
            total += movie_lists(f, escape_folder)
        elif os.path.splitext(f)[1] in file_type:
            total.append(f)
    return total


def create_failed_folder(failed_folder):
    if not os.path.exists(failed_folder + '/'):  # 新建failed文件夹
        try:
            os.makedirs(failed_folder + '/')
        except:
            print("[-]failed!can not be make folder 'failed'\n[-](Please run as Administrator)")
            os._exit(0)


def CEF(path):
    try:
        files = os.listdir(path)  # 获取路径下的子文件(夹)列表
        for file in files:
            os.removedirs(path + '/' + file)  # 删除这个空文件夹
            print('[+]Deleting empty folder', path + '/' + file)
    except:
        a = ''

# @return: str, the path that movies moved to
def create_data_and_move(file_path: str, c: config.Config,debug):
    # Normalized number, eg: 111xxx-222.mp4 -> xxx-222.mp4
    n_number = get_number(debug,file_path,c)

    if debug == True:
        print("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
        return core_main(file_path, n_number, c)
        print("[*]======================================================")
    else:
        try:
            print("[!]Making Data for [{}], the number is [{}]".format(file_path, n_number))
            return core_main(file_path, n_number, c)
            print("[*]======================================================")
        except Exception as err:
            print("[-] [{}] ERROR:".format(file_path))
            print('[-]', err)
            return ""

            # TODO:
            # If we got leftover in the directory, and we simply move the movie file outside of it,
            # , it would be problematic. The better way is to move the whole directory to failed folder.

            # 3.7.2 New: Move or not move to failed folder.
            # if c.failed_move() == False:
            #     if c.soft_link():
            #         print("[-]Link {} to failed folder".format(file_path))
            #         os.symlink(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
            # elif c.failed_move() == True:
            #     if c.soft_link():
            #         print("[-]Link {} to failed folder".format(file_path))
            #         os.symlink(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
            #     else:
            #         try:
            #             print("[-]Move [{}] to failed folder".format(file_path))
            #             shutil.move(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
            #         except Exception as err:
            #             print('[!]', err)

def create_data_and_move_with_custom_number(file_path: str, c: config.Config, custom_number=None):
    try:
        print("[!]Making Data for [{}], the number is [{}]".format(file_path, custom_number))
        core_main(file_path, custom_number, c)
        print("[*]======================================================")
    except Exception as err:
        print("[-] [{}] ERROR:".format(file_path))
        print('[-]', err)

        if c.soft_link():
            print("[-]Link {} to failed folder".format(file_path))
            os.symlink(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
        else:
            try:
                print("[-]Move [{}] to failed folder".format(file_path))
                shutil.move(file_path, str(os.getcwd()) + "/" + conf.failed_folder() + "/")
            except Exception as err:
                print('[!]', err)

# @return list of paths of decompressed files, 
# the list is empty if decompress failed
def decompress_leftover(leftover: str, extract_to: str, type: str):
    if type == '.zip':
        with zipfile.ZipFile(leftover, "r") as zip_ref:
            file_list = zip_ref.namelist()
            path_list = list()
            try:
                for i, f in enumerate(file_list):
                    o_path = os.path.join(extract_to, f)
                    print("[+]Decompressing file '{}' to path '{}'".format(f, o_path))
                    zip_ref.extract(f, extract_to)
                    path_list.append(o_path)
            except Exception as err:
                print("[-]Error orrured when decompressing '{}': {}".format(leftover, err))
                return []
            print("[+]Unzip leftover '{}' to '{}' successfully".format(leftover, extract_to))
            return path_list
    else:
        print("[-]Unsupported compress format: {}".format(type))
        return []

# Check the directory of provided movie path
# to see if there is any leftover we would like to keep
def check_and_move_leftover(root, movie_path: str, dir_path_move_to: str, c: config.Config):
    parent_path = os.path.dirname(movie_path)
    if parent_path == root:
        print("[!]Directory of movie {} is the root, skip checking leftover".format(movie_path))
        return

    # define file_types to unzip
    zip_type = ['.zip']

    dirs = os.listdir(parent_path)
    for entry in dirs:
        if entry in c.leftover():
            print("[+]Find leftover '{}' to preserve".format(entry))
            entry_path = os.path.join(parent_path, entry)
            entry_ext = os.path.splitext(entry_path)[1]
            if entry_ext in zip_type:
                print("[!]Leftover '{}' is a compressed file".format(entry))
                # remember to update entry_path to the output directory
                leftovers = decompress_leftover(entry_path, parent_path, entry_ext)
                for l in leftovers:
                    shutil.move(l, dir_path_move_to)
            else:
                shutil.move(entry_path, dir_path_move_to)

if __name__ == '__main__':
    version = '3.9.1'

    # Parse command line args
    single_file_path, config_file, custom_number = argparse_function()

    # Read config.ini
    conf = config.Config(path=config_file)

    version_print = 'Version ' + version
    print('[*]================== AV Data Capture ===================')
    print('[*]' + version_print.center(54))
    print('[*]======================================================')

    if conf.update_check():
        check_update(version)

    create_failed_folder(conf.failed_folder())
    os.chdir(os.getcwd())

    # ========== Single File ==========
    if not single_file_path == '':
        print('[+]==================== Single File =====================')
        create_data_and_move_with_custom_number(single_file_path, conf,custom_number)
        CEF(conf.success_folder())
        CEF(conf.failed_folder())
        print("[+]All finished!!!")
        input("[+][+]Press enter key exit, you can check the error messge before you exit.")
        exit()
    # ========== Single File ==========

    movie_list = movie_lists(".", re.split("[,，]", conf.escape_folder()))

    count = 0
    count_all = str(len(movie_list))
    print('[+]Find', count_all, 'movies')
    if conf.debug() == True:
        print('[+]'+' DEBUG MODE ON '.center(54, '-'))
    if conf.soft_link():
        print('[!] --- Soft link mode is ENABLE! ----')
    for movie_path in movie_list:  # 遍历电影列表 交给core处理
        count = count + 1
        percentage = str(count / int(count_all) * 100)[:4] + '%'
        print('[!] - ' + percentage + ' [' + str(count) + '/' + count_all + '] -')
        dir_path_to_move = create_data_and_move(movie_path, conf, conf.debug())
        if dir_path_to_move:
            # check leftover to preserve for each movie
            check_and_move_leftover(".", movie_path, dir_path_to_move, conf)

    CEF(conf.success_folder())
    CEF(conf.failed_folder())
    print("[+]All finished!!!")
    if conf.auto_exit():
        os._exit(0)
    input("[+][+]Press enter key exit, you can check the error message before you exit.")
