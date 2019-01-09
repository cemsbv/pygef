from pygef.robertson.robertson import Robertson
import os


def scan_folder(parent):
    # iterate over all the files and directories in the directory 'parent'
    for folder in os.listdir(parent):
        for file_name in os.listdir(parent + folder + '/'):
            if file_name.endswith((".GEF", ".gef")):
                path = parent + folder + '/' + file_name
                print(file_name)
                ciao_rob = Robertson(path)
                df = ciao_rob.df_complete
                print(df)




scan_folder("/home/martina/Documents/gef_files/2013/")
#rob = Robertson("/home/martina/Documents/gef_files/2018/18337/18337_AA17425_42.GEF")
#df = rob.df_complete
#print(df)
