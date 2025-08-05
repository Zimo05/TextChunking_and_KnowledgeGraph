from Config.Settings import setting
from openai import OpenAI
import os

class CheckFileType:
    # 检查是书籍还是paper，检查试卷是不是英语的
    def __init__(self):
        self.client = OpenAI(api_key=setting.Designer['DEEPSEEK']['API'], base_url="https://api.deepseek.com")
        self.path = setting.Designer['Storage']['PDF_to_MD']['MD_file']

    def get_filename_from_path(self):
        file_name = os.path.basename(self.path)
        return file_name
    
    def File_type(self): 
        # return {file_type: (paper or textbook), is ENG: }
        file_judge = {'file_type': None, 'is ENG': None} 
        file_name = self.get_filename_from_path()
        prompt_check_type = f'你觉得：“{file_name}，“是关于一个教科书的文件名吗，如果是返回1，不是返回0'
        prompt_check_is_ENG = f'你觉得：“{file_name}，“是关于英语试卷的文件名吗，如果是返回1，不是返回0'

        if self._AI_helper(prompt_check_type) == '1':
            file_judge['file_type'] = 'Book'
        else:
            file_judge['file_type'] = 'Paper'

        if self._AI_helper(prompt_check_is_ENG) == '1':
            file_judge['is ENG'] = True
        else:
            file_judge['is ENG'] = False

        return file_judge
    
    def _AI_helper(self, prompt):
        response = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {"role": "system", "content": "你是个聪明的老师"},
                {"role": "user", "content": prompt}
            ], 
            stream=False
        )
        judge = response.choices[0].message.content
        return judge

check = CheckFileType()
file_name = check.get_filename_from_path()
file_judge = check.File_type()