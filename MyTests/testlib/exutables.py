import os


def python38_lang(file: str) -> list:
    data = "python3.8 %s" % file
    return data.split()


def gpp_lang(file: str) -> list:
    os.system("g++ %s -o main" % file)
    return "./main".split()
