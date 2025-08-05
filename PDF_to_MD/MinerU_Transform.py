from Config.Settings import setting
from openai import OpenAI
import requests
import os
import time

class Transform:
    def __init__(self):
        self.file_path = setting.USER['file_path']
        self.subject = setting.USER['subject']
        self.TOKEN = setting.Designer['MinerU']['API']
        
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



