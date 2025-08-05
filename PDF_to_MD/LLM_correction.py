import os
from openai import OpenAI
from Config.Settings import settings
from PDF_to_MD.Check_File_Type import file_name, file_judge
from PDF_to_MD.MinerU_Transform import transform, MD_File


class correction:
    def __init__(self, output_path):
        self.MD_File = MD_File
        self.output_path = output_path
        self.client = OpenAI(api_key="sk-16528769d4794f44a01c283443c88bec", base_url="https://api.deepseek.com")
        self.file_judge = file_judge
        self.file_name = file_name

    def correct_markdown_files(self):
        if self.output_path and not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
        
        results = []
        for filename in os.listdir(self.input_path):
            if not filename.endswith('.md'):
                continue
                
            content = MD_File
            prompt = "对于我给你的markdown文本块，请把这个文本的错误语法进行修正，不要对原内容做任何的删改"
            output_path = os.path.join(self.output_path, filename) if self.output_path else None
            
            try:                
                response = self.client.chat.completions.create(
                    model='deepseek-chat',
                    messages=[
                        {"role": "system", "content": "你是个聪明的老师"},
                        {"role": "user", "content": prompt + '\n' + '以下是markdown文本：' +  '\n' + content}
                    ],
                    stream=False
                )
                modified_md = response.choices[0].message.content

                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as file:
                        file.write(modified_md)
                
                results.append(f"Success: {filename}")
                
            except Exception as e:
                results.append(f"Error processing {filename}: {str(e)}")
        
        return results
    
    
    def main(self):
        # 
        if self.file_judge[0] == 'Book':





    
# 做出可以识别出
correction = correction()
results = correction.main()

# 假如是一张试卷的话，就整张卷子传，假如是一本书的话，两个##为单位传递， 然后添加上结构化的#，##，###， ####
# 让用户自己取output的名字

# 假如input一本书，results就是两个##，要做拼接