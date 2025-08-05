import re
from openai import OpenAI
from Config.Settings import settings
from PDF_to_MD.Check_File_Type import file_name, file_judge
from PDF_to_MD.MinerU_Transform import mineru_zip_path
from Config.Settings import setting
import zipfile

class correction:
    def __init__(self):
        self.api = setting.Designer['DIFY']['DIFY_Correction_API']
        self.user = setting.Designer['DIFY']['DIFY_USER']
        self.url = setting.Designer['DIFY']['DIFY_URL']
        self.file_judge = file_judge
        self.file_name = file_name
        self.mineru_zip_path = mineru_zip_path
        self.extract_dir_base = setting.Designer['Storage']['PDF_to_MD']['MD_file']
        self.subject = setting.USER['subject']

    def pre_processing(self):
        file_type = self.file_judge['file_type']
        file_name_base = self.file_name
        file_name_base = file_name_base.replace('.pdf', '')
        extract_dir = f'{self.extract_dir_base}/{file_type}/{self.subject}/{file_name_base}/'
        with zipfile.ZipFile(self.mineru_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        mineru_folder = self.pre_processing()
        md_content_path = f'{mineru_folder}/full.md'
        with open(md_content_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('．', '.')
        content = content.replace('（', '(')
        content = content.replace('）', ')')
        
        processed_text = re.sub(r'(\d+\.)(\S)', r'\1 \2', content)
        processed_text = re.sub(r'^(\d+\.)', r'## \1', processed_text, flags=re.MULTILINE)

        return processed_text, md_content_path
    
    def correct_markdown_files(self, content, md_content_path):
        
        prompt = "对于我给你的markdown文本块，请把这个文本的markdown错误语法进行修正，不要对原内容做任何的删改"           
        response = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {"role": "system", "content": "你是个聪明的markdown专家"},
                {"role": "user", "content": prompt + '\n' + '以下是markdown文本：' +  '\n' + content}
            ],
            stream=False
        )
        modified_md_chunk = response.choices[0].message.content

        return modified_md_chunk
    
    def main(self):
        # 
        corrected_md_file = ''
        if self.file_judge[0] == 'Book':
            return

        else:
            content, md_content_path = self.pre_processing()
            sections = re.split(r'(# [一二三四五六七八九十]+、)', content)

            result = []
            for i in range(0, len(sections), 2):
                if i + 1 < len(sections):
                    result.append(sections[i] + sections[i+1])
                else:
                    result.append(sections[i])
            for idx, sec in enumerate(result, 1):
                modified_md = self.correct_markdown_files(sec.strip(), md_content_path)
                corrected_md_file = corrected_md_file + '\n' + modified_md

        with open(md_content_path, 'w', encoding='utf-8') as file:
            file.write(corrected_md_file)

        return corrected_md_file

# 做出可以识别出
correction = correction()
results = correction.main()
