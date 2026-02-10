
from re import S


def checkFileData(srv, filepath):
    response = False

    try:
        with open(filepath, 'r') as f:
            file_lines= f.read().split("\n")
            
            for line in file_lines:
                if srv == line:
                    response = True
                    break
            
                     
    except Exception as e:
        print(e)
    

    return response