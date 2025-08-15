from Config.Settings import setting
from collections import deque
import re
import requests
import json
import pandas as pd
from EntityLinking.Entity_Linking import Linking
import os

class TextBookQuestion:
    def __init__(self, BookTree, file_name):
        self.BookTree = BookTree
        self.file_name = file_name.replace('.pdf', '')
        self.file_path_base = setting.Designer['Storage']['Parser']['Chunked_book']
        self.Dify_API = setting.Designer['DIFY']['DIFY_TextBook_Question_Answer']
        self.user = setting.Designer['DIFY']['DIFY_USER']
        self.url = setting.Designer['DIFY']['DIFY_URL']
        self.subject = setting.USER['subject']

    def Question_Chunking(self):

        chapter_questions = {}
        keywords = {'练习', '复习题', '复习与提高'}

        for chapter in self.BookTree:
            chapter_name = chapter.title
            chapter_questions[chapter_name] = []
        
            queue = deque([chapter])
            while queue:
                node = queue.popleft()
                if any(k in node.title for k in keywords):
                    chapter_questions[chapter_name].append(node)  # 添加到当前章节的问题列表
                queue.extend(node.children)

        df_list = []
        for chapter, node_list in chapter_questions.items():
            for node in node_list:
                content = node.content

                translation_table = str.maketrans({
                    '．': '.',
                    '（': '(',
                    '）': ')',
                })
                content = content.translate(translation_table)
                replacements = {
                    '.': '. ', 
                    '\n\n': '\n'
                }
                for old, new in replacements.items():
                    content = content.replace(old, new)
                    sections = re.split(r'\d+\.\s*', content)

                Question = []
                Answers = []
                Analyses = []
                Knowledge = []

                for section in sections:
                    answer, analysis = self.Dify_structuring(section)
                    try:
                        knowledge = Linking.link_question_with_entity(section)
                    except Exception as e:
                        try:
                            knowledge = Linking.link_question_with_entity(section)
                        except Exception as e:
                            knowledge = 'None'
                            continue
                    Answers.append(answer)
                    Analyses.append(analysis)
                    Knowledge.append(knowledge)
                    Question.append(section)
                
                df = pd.DataFrame()
                df['question'] = Question
                df['answer'] = Answers
                df['analysis'] = Analyses
                df['knowledge'] = Knowledge

            df_list.append(df)

        combined_df = pd.concat(df_list, ignore_index=True)

        output_path = f'{self.file_path_base}/{self.subject}/{self.file_name}/chunked_{self.file_name}_question_df.csv'
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        combined_df.to_csv(output_path, index=False)
        
        return combined_df

    def Dify_structuring(self, section):
        headers = {
                "Authorization": f"Bearer {self.Dify_API}",
                "Content-Type": 'application/json'
            }
        request_data = {
            "inputs": {
                "Question": section, 
            },
            "user": self.user
        }
        response = requests.post(self.url, headers=headers, json=request_data)
        response_text = response.text
        response_json = json.loads(response_text)
        output = response_json["data"]["outputs"]['Answer']
        cleaned_str = re.sub(r'`json|\`', '', output)
        cleaned_str = cleaned_str.strip()
        data = json.loads(cleaned_str)

        answer = data['答案']
        analysis = data['解析']

        return answer, analysis
