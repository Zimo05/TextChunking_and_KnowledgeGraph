from PDF_to_MD.MinerU_Transform import MD_File
from PDF_to_MD.LLM_correction import results
from Parser.Invoke_Parser import invoking_Parser
from Config.Settings import setting

import json

from openai import OpenAI

# 知识图谱助手：
# 出题助手： 单个科目，直接问什么知识点的什么题型，多科目问什么学科的什么知识点的什么题型
class Implement:

    def Question_Generate():
        # 出题助手：Input subject(s)
        knowledge_options = ['语文(CHI)', '数学(MAT)', '英语(ENG)', '物理(PHY)', 
                            '化学(CHM)', '生物(BIO)', '政治(POL)', '历史(HIS)', '地理(GEO)']
        
        for i, subject in enumerate(knowledge_options, 1):
            print(f"{i}. {subject}")

        print("Please choose subjects(Input the number and Separate by commas):")
        choice = input("你的选择(如:1,3,5): ").strip()
        selected_indices = [int(idx.strip())-1 for idx in choice.split(',')]
        selected_subjects = [knowledge_options[idx] for idx in selected_indices]
        setting.USER['knowledge'] = selected_subjects
        
        
        # Dealing with muktiple subjects(出题助手, 对接章哥)

    def Corpus_Search():
        # Search for corpus(ES Importer)
        return



    def Knowlwdge_Graph():
        # Input subject
        knowledge_options = ['语文(CHI)', '数学(MAT)', '英语(ENG)', '物理(PHY)', 
                            '化学(CHM)', '生物(BIO)', '政治(POL)', '历史(HIS)', '地理(GEO)']
        
        for i, subject in enumerate(knowledge_options, 1):
            print(f"{i}. {subject}")

        print("Please choose subject(Input the number):")
        choice = input("Please choose: ").strip()
        selected_subject = knowledge_options[int(choice)-1]
        subject_code = selected_subject.split('(')[1].split(')')[0]
        setting.USER['subject'] = subject_code

        # Storage path
        setting.USER['file_path'] =  input('Please enter your file path: ') #'./Data/Original/教材/高中数学必修第一册A版/高中数学必修第一册A版.md'
        TransformedMD = MD_File
        chunk, df = invoking_Parser.invoke_parser()
        return


knowledge_options = ['语文(CHI)', '数学(MAT)', '英语(ENG)', '物理(PHY)', 
                    '化学(CHM)', '生物(BIO)', '政治(POL)', '历史(HIS)', '地理(GEO)']

for i, subject in enumerate(knowledge_options, 1):
    print(f"{i}. {subject}")

print("Please choose subject(Input the number):")
choice = input("Please choose: ").strip()
selected_subject = knowledge_options[int(choice)-1]
subject_code = selected_subject.split('(')[1].split(')')[0]
setting.USER['subject'] = subject_code

# Storage path
setting.USER['file_path'] =  input('Please enter your file path: ') #'./Data/Original/教材/高中数学必修第一册A版/高中数学必修第一册A版.md'
TransformedMD = MD_File
chunk, df = invoking_Parser.invoke_parser()