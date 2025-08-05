import os
import pandas as pd
import requests
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from Config.Settings import setting


class EntityLinking:
    def __init__(self):
        self.edukg_instance = setting.Designer['Entity_linking']['Edukg_instance_info']
        self.KD_index = setting.Designer['Entity_linking']['Entity_level_index']
        self.subject = setting.USER['subject']
        self.SUBJECT_MAPPING = {
                                    'CHI': '语文',
                                    'ENG': '英语',
                                    'PHY': '物理',
                                    'CHM': '化学',
                                    'HIS': '历史',
                                    'BIO': '生物',
                                    'GEO': '地理',
                                    'POL': '政治'
                                }
        self.api_url = setting.Designer['DIFY']['DIFY_URL']
        self.api_key = setting.Designer['DIFY']['DIFY_Entity_Linking_API']
        self.book_api_key = setting.Designer['DIFY']['DIFY_Entity_Book_Linking_API']
        self.user = setting.Designer['DIFY']['DIFY_USER']

    def _import_entity(self):
        self.SUBJECT_TABLE = pd.DataFrame(self.SUBJECT_MAPPING, index=[0]).T.reset_index()
        self.SUBJECT_MAPPING.columns = ['科目代码', '科目名称']

        THU_entity = pd.read_csv('./neo4j/import/edukg_instance_info.csv', encoding='utf-8')
        THU_dict = {}
        for code, name in self.SUBJECT_MAPPING.items():
            THU_dict[f"{code}_THU"] = THU_entity[THU_entity['subject_type'] == f'{name}实体']

        KG_index = {} 
        for code, name in self.SUBJECT_MAPPING.items():
            file_path = f'./neo4j/import/{code}/{name}_知识图谱目录.xlsx'
            KG_index[f"{code}_KG_index"] = pd.read_excel(file_path)

    def _unique_entity_and_tree(self, df: pd.DataFrame, title):
        all_entities = []
        records = []
        for ind, row in df.iterrows():
            filtered_row = [item for item in row if pd.notna(item)] 
            for i in range(1, len(filtered_row)):
                subject = filtered_row[i - 1]
                object = filtered_row[i]
                if object not in all_entities:
                    all_entities.append(object)
                if subject not in all_entities:
                    all_entities.append(subject)

                record = {
                        'subject': subject,
                        'subject_type': f'{title}实体',
                        'subject_level':i,
                        'object': object,
                        'object_type': f'{title}实体',
                        'object_level':i+1,
                        'relation_type': '下位',
                    }
                if record not in records:
                    records.append(record)
        df_knowledgeTree = pd.DataFrame(records)
        df_all_entities = pd.DataFrame(all_entities, columns=['entity'])
        df_knowledgeTree.to_csv(f'./neo4j/import/{title}/{title}_知识图谱目录_all.csv', index=False)
        df_all_entities.to_csv(f'./neo4j/import/{title}/{title}_all_entities.csv', index=False)
        
        return df_knowledgeTree, df_all_entities

    def link_book_with_entity(self, chunk):
        headers = {
            "Authorization": f"Bearer {self.book_api_key}",
            "Content-Type": 'application/json'
        }
        request_data = {
            "inputs": {
                "title": chunk, 
            },
            "user": self.user
        }
        response = requests.post(self.api_url, headers=headers, json=request_data, timeout=30)
        response_text = response.text
        response_json = json.loads(response_text)
        response_text = response.text
        response_json = json.loads(response_text)
        responses = response_json['data']['outputs']['entity']
        entity_list = [item['content'] for item in responses]
        candidate = {}
        distance_list = []
        for entry in entity_list:
            distance = self._tfidf_cosine_distance(chunk, entry)
            candidate[distance] = entry
            distance_list.append(distance)

        best_dist = min(distance_list)
        best = candidate[best_dist]
        
        return best
    
    def _tfidf_cosine_distance(self, str1, str2):
        documents = [str1, str2]
        vectorizer = TfidfVectorizer(analyzer='char').fit(documents)
        tfidf_matrix = vectorizer.transform(documents)
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        cosine_dist = 1 - cosine_sim
        return cosine_dist

    def link_question_with_entity(self, question_chunk):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": 'application/json'
        }
        request_data = {
            "inputs": {
                "Quesion": question_chunk, 
            },
            "user": self.user
        }
        response = requests.post(self.api_url, headers=headers, json=request_data, timeout=30)
        response_text = response.text
        response_json = json.loads(response_text)
        output = response_json['data']['outputs']['knowledge']
        output_dict = json.loads(output.replace("'", '"'))
        knowledge = output_dict['知识点']
        return knowledge
    
Linking = EntityLinking()