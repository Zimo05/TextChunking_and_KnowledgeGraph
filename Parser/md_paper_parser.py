import tqdm
import re
import pandas as pd
import requests
import json
from Config.Settings import setting
from EntityLinking.Entity_Linking import Linking
from PDF_to_MD.Check_File_Type import file_name
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
# Input a question collection file

class PaperParser:
    def __init__(self):
        self.paper_path = setting.Designer['Storage']['PDF_to_MD']['MD_file']
        self.api_url = setting.Designer['DIFY']['DIFY_URL']
        self.api_key = setting.Designer['DIFY']['DIFY_ENG_Paper_Parser_API']
        self.subject = setting.USER['subject']
        self.output_path_base = setting.Designer['Storage']['Parser']['Chunked_paper']
        self.file_name = file_name
        self.client = OpenAI(api_key=setting.Designer['DEEPSEEK']['API'], base_url="https://api.deepseek.com")
        self.question_knowledge = {
            '阅读理解':['细节理解题', '主旨大意题', '推理判断题', '词义猜测题'],
            '语法及词法':["名词", "代词", "实义动词", "助动词", "情态动词", "形容词", "副词", "介词", "连词", "感叹词", "冠词", 
                        "数词", "现在分词", "过去分词", "主语", "谓语", "动词", "直接宾语", "间接宾语", "表语", "主语补足语", "宾语补足语", 
                        "定语", "形容词修饰语", "状语", "副词修饰语", "同位语", "独立成分", "呼语", "插入语", "陈述句", "疑问句", "表语从句",
                        "一般疑问句", "特殊疑问句", "选择疑问句", "反义疑问句", "祈使句", "感叹句", "简单句", "并列句", "复合句", "宾语从句", 
                        "定语从句", "状语从句", "主动语态", "被动语态", "一般现在时", "一般过去时", "一般将来时", "现在进行时", "过去进行时", 
                        "将来进行时", "现在完成时", "过去完成时", "将来完成时", "现在完成进行时", "过去完成进行时", "将来完成进行时", "过去将来时", 
                        "过去将来进行时", "过去将来完成时", "过去将来完成进行时", "语态", "主动", "被动", "陈述语气", "祈使语气", "虚拟语气", 
                        "非谓语动词", "不定式", "动名词", "分词", "主谓一致", "倒装句", "省略句", "强调句", '动词时态', '固定搭配', '短语']
        }
        
    def ENG_parser(self):
        with open(self.paper_path, 'r', encoding='utf-8') as f:
            md_paper = f.read()
        question_judge = self._question_type_judge(self.file_name)

        questions_collection = re.split(r'(?=\n#)', md_paper.strip())
        def process_question(question):
            chunnking_signal = self._dify_structuring(question)
            parsed_question = self._split_questions(chunnking_signal, question)
            return {
                'text': parsed_question['文章主体内容'],
                'questions': parsed_question['问题及选项部分'],
                'analysis': parsed_question['解析部分'],
                'answer': parsed_question['答案内容']
            }
        def process_newlines(text):
            text = re.sub(r'([a-zA-Z])\n([a-zA-Z])', r'\1 \2', text)
            text = re.sub(r'([\u4e00-\u9fff])\n([\u4e00-\u9fff])', r'\1\2', text)
            text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
            text.replace('（', '(')
            text.replace('）', ')')

            return text
                
        question_chunking = []
        for question in questions_collection:
            source_pattern = r'【([^】]*\d{4}[^】]*)】'
            source = re.findall(source_pattern, question[:100])[0] if re.findall(source_pattern, question[:100]) else ""
            q = process_newlines(question)
            processed_q = process_question(q)
            question_dict = {
                                "source": source,
                                "content": processed_q
                            }
            question_chunking.append(question_dict) 
        
# 1. 阅读题：题干-原文-文章类型-考察题型-答案解析
# 2. 完形：题目-解析-考点
# 3. 填词：挖空-解析-考察题型
# 4. 七选五：挖空-逻辑相关上下文-答案
        
        df_config = {
            '阅读理解': {
                'columns': ['text', 'text_type', 'questions', 'analysis', 'answer', 'question_type'],
                'processor': lambda q: {
                    'text': q['text'],
                    'text_type': question_judge[1], 
                    'questions': q['questions'],
                    'analysis': q['analysis'],
                    'answer': q['answer'],
                    'question_type': self._knowledge_extraction_1(
                        q['analysis'], 
                        self.question_knowledge['阅读理解']
                    )
                }
            },

            '完形填空': {
                'columns': ['text', 'text_type', 'questions', 'analysis', 'answer', 'question_type'],
                'processor': lambda q: {
                    'text': q['text'],
                    'text_type': question_judge[1], 
                    'questions': q['questions'],
                    'analysis': q['analysis'],
                    'answer': q['answer'],
                    'question_type': self._knowledge_extraction_2(
                        q['analysis'], 
                        self.question_knowledge['语法及词法']
                    )
                }
            },

            '语法填空': {
                'columns': ['text', 'text_type', 'questions', 'analysis', 'answer', 'question_type'],
                'processor': lambda q: {
                    'text': q['text'],
                    'text_type': question_judge[1],  # 同上
                    'questions': q['questions'],
                    'analysis': q['analysis'],
                    'answer': q['answer'],
                    'question_type': self._knowledge_extraction_2(
                        q['analysis'], 
                        self.question_knowledge['语法及词法']
                    )
                }
            },

            '阅读理解七选五': {
                'columns': ['text', 'questions', 'analysis', 'answer'],
                'processor': lambda q: {
                    'text': q['text'],
                    'questions': q['questions'],
                    'analysis': q['analysis'],
                    'answer': q['answer'],
                }
            }
        }
        config = df_config.get(question_judge[0])
        df = pd.DataFrame(columns=config['columns'])
        rows = []
        for q in question_chunking:
            for source, chunks in q.items():
                question_data = config['processor'](chunks)
                question_data['source'] = source
                rows.append(question_data)

        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

        if question_judge[0] in ['阅读理解', '完形填空', '语法填空']:
            all_entities = []
            question_chunk = df['question_type']
            for row in question_chunk:
                knowledge_list = [item.strip() for item in row.split(",")]
                entity_list = []
                for item in knowledge_list:
                    entity = Linking.link_question_with_entity(item)
                    entity_list.append(entity)

                all_entities.append(', '.join(entity_list))
            

            df['entity'] = all_entities
        
        output_path = f'{self.output_path_base}/{self.subject}/{self.file_name}/'
        df.to_csv(output_path, index=False)
        return df   

    def GENERAL_parser(self):

        with open(self.paper_path, 'r', encoding='utf-8') as f:
            content = f.read()

        #题干
        stems = []
        #解析和答案
        answerAnalysis = []
        #试题来源
        references=[]
        #知识点
        knowledges=[]
        names=self.paper_path.split('/')
        names='/'.join(names[-3:-1])
        zhentis=content.split('###')[1:]

        for item in tqdm(zhentis):
            if "【答案】" in item:
                # print(f"答案:{item}")
                tmp = item.split("【答案】")
                stems.append(tmp[0])
                answerAnalysis.append(tmp[1])
            elif "【解答】" in item:
                # print(f"解析:{item}")
                tmp = item.split("【解答】")
                # print(f"tmp:{tmp}")
                stems.append(tmp[0])
                answerAnalysis.append(tmp[1])
            elif "【解析】" in item:
                # print(f"解析:{item}")
                tmp = item.split("【解析】")
                # print(f"tmp:{tmp}")
                stems.append(tmp[0])
                answerAnalysis.append(tmp[1])
            else: 
                print(f"没有答案和解析:{item}")
            references.append(names)
            knowledges.append(Linking.link_question_with_entity(item))

        df=pd.DataFrame()
        df["questions"]=stems
        df["analysis"]=answerAnalysis
        df["references"]=references
        df["knowledges"]=knowledges

        output_path = f'{self.output_path_base}/{self.subject}/{self.file_name}/'
        df.to_csv(output_path, index=False)

        return df
    
    def _dify_structuring(self, question_chunk):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": 'application/json'
        }
        request_data = {
            "inputs": {
                "Paper": question_chunk, 
            },
            "user": "Zimo"
        }
        response = requests.post(self.api_url, headers=headers, json=request_data, timeout=30)
        response_text = response.text
        response_json = json.loads(response_text)
        output = response_json["data"]["outputs"]
        raw_str = output['Structure']
        cleaned_str = re.sub(r'`json|\`', '', raw_str)
        cleaned_str = cleaned_str.strip()
        data = json.loads(cleaned_str)
        print(data) 
        return data
    
    def _split_questions(self, signals, text:str):
        parts = {}
        for signal_info in signals[:2]:
            part_name = re.escape(signal_info['part_name'])
            start_pattern = re.escape(signal_info['start_index'])
            end_pattern = re.escape(signal_info['end_index'])
            
            pattern = f"{start_pattern}.*?{end_pattern}"
            match = re.search(pattern, text.replace('\n', ' '), re.DOTALL)
            if not match:
                raise ValueError(f"Could not find pattern for {part_name}.")
            
            parts[part_name] = match.group(0).strip()

        answer_signal = signals[-2]
        answer = answer_signal['答案内容']
        parts['答案内容'] = answer
        
        signal_info = signals[-1]
        part_name = re.escape(signal_info['part_name'])
        start_pattern = re.escape(signal_info['start_index'])
        end_pattern = re.escape(signal_info['end_index'])
        pattern = f"{start_pattern}.*"
        match = re.search(pattern, text.replace('\n', ' '), re.DOTALL)
        parts[part_name] = match.group(0).strip()
        return parts
    
    def _question_type_judge(self, file_name):
        # 阅读以外的返回question_type str,阅读题返回[阅读理解，(文章类型)]
        text_type = ['完形填空', '阅读理解七选五', '阅读理解', '语法填空']
        all_texts = text_type + [file_name]
        vectorizer = TfidfVectorizer(analyzer='char')
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        cos_sim = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:len(text_type)])
        best_match_idx = cos_sim.argmax()
        judge = text_type[best_match_idx]

        judgement = []
        judgement.append(judge)
        if judge in ['阅读理解', '完形填空', '语法填空']:
            text_type = ['记叙文','说明文', '新闻类', '议论文']
            all_texts = text_type + [file_name]
            vectorizer = TfidfVectorizer(analyzer='char')
            tfidf_matrix = vectorizer.fit_transform(all_texts)

            cos_sim = cosine_similarity(tfidf_matrix[-1:], tfidf_matrix[:len(text_type)])
            best_match_idx = cos_sim.argmax()
            type = text_type[best_match_idx]
            judgement.append(type)
        else:
            judgement.append(None)

        return judgement
    
    def _knowledge_extraction_1(self, analyses, knowledge):
        pattern = '|'.join(map(re.escape, knowledge))
        matches = re.findall(pattern, analyses)

        result = ", ".join(matches)

        return result
        
    def _knowledge_extraction_2(self, analyses, knowledge):
        def preprocess_chinese(analysis):
            return " ".join(jieba.cut(analysis))
        
        knowledge_list = ''
        if re.search(r'[^。！？；]*考查[^。！？；]*[。！？；]', analyses):
            analyses_list = re.findall(r'[^。！？；]*考查[^。！？；]*[。！？；]', analyses)
        else:
            split_result = re.split(r'\d+\.', analyses)
            split_result = [item.strip() for item in split_result if item.strip()]

        for analysis in analyses_list:
            first_20_chars = analysis[:20]
            processed_first_20 = preprocess_chinese(first_20_chars)
            token_list = processed_first_20.split()
            candidates = set()
            for cat in knowledge:
                for tok in token_list:
                    if tok in cat:
                        candidates.add(cat)
            best_score = -1
            best_category = None
            for candidate in candidates:
                texts = [processed_first_20, candidate]
                vectorizer = TfidfVectorizer(analyzer='char')
                tfidf_matrix = vectorizer.fit_transform(texts)

                cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                if cos_sim > best_score:
                    best_score = cos_sim
                    best_category = candidate

            knowledge_list += str(best_category) + ', '

        knowledge_list = knowledge_list.strip(', ')

        return knowledge_list
    
    
paper_parser = PaperParser()
ENG_parser = paper_parser.ENG_parser()
Othertype_parser = paper_parser.GENERAL_parser()

