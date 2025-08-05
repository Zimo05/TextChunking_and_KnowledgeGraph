from Config.Settings import setting
from openai import OpenAI
import requests

class Transform:
    def __init__(self, file):
        self.file_path = setting.USER['file_path']
        
    def implement_MinerU(self): 
        url='https://mineru.net/api/v4/extract/task'
        header = {
            'Content-Type':'application/json',
            'Authorization':'Bearer eyJ0eXBlIjoiSl...please insert your token！'
        }
        data = {
            'url': self.file_path,
            'is_ocr':True,
            'enable_formula': False,
        }

        res = requests.post(url,headers=header,json=data)
        res = res.json()
        output = res.json()["data"]
        
        return output
    
transform = Transform()
MD_File = transform.implement_MinerU()

# 转换后，# 的标题分类，教科书比较难处理，试卷的可以用re结合神经网络判断是否应该加上该 #
