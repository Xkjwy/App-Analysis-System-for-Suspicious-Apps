import os
import zipfile
import hashlib
from androguard.core.bytecodes import apk as androguard_apk

def extract_apk_info(apk_path):
    def hash_file(apk_path):
        # 计算文件的SHA1和SHA256哈希值
        blocksize = 65536
        hashes = {'sha1': hashlib.sha1(), 'sha256': hashlib.sha256()}

        # 以二进制读模式打开APK文件
        with open(apk_path, 'rb') as afile:
	    # 读取文件块，并更新哈希对象
            buf = afile.read(blocksize)
            while len(buf) > 0:
                hashes['sha1'].update(buf)
                hashes['sha256'].update(buf)
                buf = afile.read(blocksize)

        return hashes['sha1'].hexdigest(), hashes['sha256'].hexdigest()  # 返回计算得到的SHA1和SHA256哈希值的十六进制字符串

    # 调用内部函数计算APK文件的SHA1和SHA256哈希值
    sha1_hash, sha256_hash = hash_file(apk_path)

    #  计算APK文件的大小
    apk_size = os.path.getsize(apk_path)
    # 再次以二进制读模式打开APK文件，计算MD5哈希值
    with open(apk_path, 'rb') as f:  
        apk_data = f.read()   
        md5 = hashlib.md5(apk_data).hexdigest()

    #  使用androguard库加载APK文件
    apk = androguard_apk.APK(apk_path)

    # 提取APK信息
    package_name = apk.get_package()  # 获取包名
    application_name = apk.get_app_name()  # 获取应用名（如果有的话）
    # 尝试获取版本名称，如果版本信息中没有'Name'，则设置为'Unknown'
    version_name = apk.get_androidversion_name() if 'Name' in apk.androidversion else 'Unknown'
    # 尝试获取版本代码，如果版本信息中没有'code'，则设置为'Unknown' 
    version_code = apk.get_androidversion_code() if 'code' in apk.androidversion else 'Unknown'
    target_sdk_version = apk.get_target_sdk_version()

    # 构建架构信息字典
    architecture = {arch: False for arch in ['armeabi', 'armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64']}
    for file in apk.get_files():
        for arch in architecture.keys():
            if file.startswith(f'lib/{arch}/'):
                architecture[arch] = True

    # 将所有信息包装成一个字典并返回
    info = {
        'APK Size': apk_size,
        'MD5': md5,
        'Application Name': application_name,
        'Package Name': package_name,
        'Version Code': version_code,
        'Version Name': version_name,
        'Target SDK Version': target_sdk_version,
        'Architecture': architecture,
        'SHA256': sha256_hash,
        'SHA1': sha1_hash
    }

    return info

