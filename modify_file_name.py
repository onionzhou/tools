# -*- coding: utf-8 -*-
import  os


'''
批量修改文件名，在其文件名前追加数字编号
src= test.txt ,test1.txt  
dst= 1_test.txt,2_test.txt

如何使用
dir_path="G:\downloads/27学习入门篇"
modify_file_name(dir_path)

'''
def modify_file_name(dir_path):
    try:
        for root ,dirs,files in os.walk(dir_path):
            for num ,file in enumerate(files,1):
                #print(num,file)
                new_name=str(num)+"_"+file
                src=os.path.join(root,file)   #get 文件路径
                dst=os.path.join(root,new_name)
                os.rename(src,dst)
                #print(src,dst)
    except Exception as e:
        raise e
    print ("modify sucess")


def bantch_file(dir_list):

    if  dir_list == [] :
        return
    tmp =[]
    for num ,filepath in enumerate(dir_list,1):
        for filename in os.listdir(filepath):
            print(filename)
            path=os.path.join(filepath,filename)
            if os.path.isfile(path):
                new_name = str(num) + "_" + filename
                dst= os.path.join(filepath,new_name)
                # print(num, filename)
                os.rename(path,dst)

            if os.path.isdir(path):
                tmp.append(path)
    # print(tmp)
    bantch_file(tmp)

'''
dir_path = "G:\FFOutput/test"
modify_filename_through_folder(dir_path)
执行前
test --dir1--file1,file2,file3 
    |--dir2--file1,file2,file3
    |--dir3--file1,file2,file3
    
执行后 
test --dir1--1_file1,1_file2,1_file3 
    |--dir2--2_file1,2_file2,2_file3
    |--dir3--3_file1,3_file2,3_file3
'''


def modify_filename_through_folder(dir_path):
    dir_list=[]
    for filename in os.listdir(dir_path):
        path =os.path.join(dir_path,filename)
        if os.path.isdir(path):
            dir_list.append(path)

    bantch_file(dir_list)

    print("修改完成")


if __name__ == '__main__':
    dir_path = "G:\downloads/27 机器学习入门篇2"
    modify_filename_through_folder(dir_path)
    # print(os.listdir(dir_path))