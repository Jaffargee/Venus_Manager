import shutil
import os
import zipfile

def zip_directory(direc, output):
    shutil.make_archive(output, "zip", direc)

