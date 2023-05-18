import os
import stat
import shutil
import pygit2
import uvicorn


def del_dir(file_path):
    """删除文件夹"""
    while 1:
        if not os.path.exists(file_path):
            break
        try:
            shutil.rmtree(file_path)
        except PermissionError as err:
            err_file_path = str(err).split("\'", 2)[1]
            if os.path.exists(err_file_path):
                os.chmod(err_file_path, stat.S_IWUSR)
    print(file_path,'已删除')

def update_file(src,dest,ignore):
    """更新文件"""
    ignore.append(src)
    ignore.append('.git')
    ignore_list = [os.path.join(src,i).strip('/') for i in ignore]
    for root, dirs, files in os.walk(src, topdown=True):
        if any(root.startswith(i) for i in ignore_list):
            print(root,'过滤文件夹')
        else:
            print(root,len(files))
            for name in files:
                src_file = os.path.join(root, name)
                if src_file in ignore_list:
                    print(src_file,'过滤文件')
                    continue
                dest_file = os.path.join(root.replace(src,dest),name)
                os.makedirs(os.path.dirname(dest_file),exist_ok=True)
                if os.path.exists(dest_file):
                    print(f'覆盖：{dest_file}')
                else:
                    print(f'新建：{dest_file}')
                shutil.copy(src_file,dest_file)

def updates(src,dest,ignore):
    """更新程序"""
    remote_url = "https://github.com/seo888/SeoApi.git"
    if os.path.exists(src):
        del_dir(src)
    print(f'{remote_url} 下载中...')
    repo = pygit2.clone_repository(remote_url, src)
    print(f'{remote_url} 已下载')
    # 比对文件进行覆盖
    update_file(src,dest,ignore)

def run():
    ignore_list = [
        'config/config.yml',
    ]
    src = "./repo"
    dest = './'
    updates(src,dest,ignore_list)

    for i in ignore_list:
        print(i,f'跳过更新，如需更新则手动更新 {os.path.join(src,i)}')
    print('本次更新完成')

if __name__ == '__main__':
    run()