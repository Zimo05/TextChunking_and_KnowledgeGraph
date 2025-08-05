from Parser.Invoke_Parser import Chunker
from Parser.MD_section_parser import BookTree # 教科书的先检查现有的
from Config.Settings import setting
import pandas as pd
import os

class updateContent:
    def __init__(self):
        self.edukg = setting.Designer['Entity_linking']['Edukg_instance_info']
        self.knowledge_index = setting.Designer['Entity_linking']['Knowledge_index']
        self.Entity_Table = setting.Designer['Entity_linking']['Entity_Table_Path']
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
        self.output_path = setting.Designer['Entity_linking']['Output']

    def update_entity_tree():
        for key, value in BookTree.items():
            title = key.title
        return
    
    def unique_entity_and_tree(df: pd.DataFrame, title):
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