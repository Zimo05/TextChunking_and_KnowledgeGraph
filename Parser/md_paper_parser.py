import re
import pandas as pd
import requests
import json
import os
from Config.Settings import setting
from EntityLinking.Entity_Linking import Linking
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jieba
# Input a question collection file

class PaperParser:
    def __init__(self, md_content_path, file_name):
        self.paper_path = md_content_path
        self.dify_user = setting.Designer['DIFY']['DIFY_USER']
        self.api_url = setting.Designer['DIFY']['DIFY_URL']
        self.api_key = setting.Designer['DIFY']['DIFY_ENG_Paper_Parser_API']
        self.geo_api_key = setting.Designer['DIFY']['DIFY_GEO_Paper_Parser_API']
        self.subject = setting.USER['subject']
        self.output_path_base = setting.Designer['Storage']['Parser']['Chunked_paper']
        self.file_name = file_name.replace('.pdf', '')
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
                'columns': ['text', 'questions', 'analysis', 'answer', 'question_type'],
                'processor': lambda q: {
                    'text': q['text'],
                    'questions': q['questions'],
                    'answer and analysis': {'answer': q['answer'], 'analysis': q['analysis']},
                    'question_type': self._knowledge_extraction_1(
                        q['analysis'], 
                        self.question_knowledge['阅读理解']
                    )
                }
            },

            '完形填空': {
                'columns': ['text', 'questions', 'analysis', 'answer', 'question_type'],
                'processor': lambda q: {
                    'text': q['text'],
                    'questions': q['questions'],
                    'answer and analysis': {'answer': q['answer'], 'analysis': q['analysis']},
                    'question_type': self._knowledge_extraction_2(
                        q['analysis'], 
                        self.question_knowledge['语法及词法']
                    )
                }
            },

            '语法填空': {
                'columns': ['text', 'questions', 'analysis', 'answer', 'question_type'],
                'processor': lambda q: {
                    'text': q['text'],
                    'questions': q['questions'],
                    'answer and analysis': {'answer': q['answer'], 'analysis': q['analysis']},
                    'question_type': self._knowledge_extraction_2(
                        q['analysis'], 
                        self.question_knowledge['语法及词法']
                    )
                }
            },

            '阅读理解七选五': {
                'columns': ['text', 'questions', 'analysis', 'answer', 'question_type'],
                'processor': lambda q: {
                    'text': q['text'],
                    'questions': q['questions'],
                    'answer and analysis': {'answer': q['answer'], 'analysis': q['analysis']},
                    'question_type': '上下文逻辑推断'
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
                    try:
                        entity = Linking.link_question_with_entity(item)
                        entity_list.append(entity)
                    except Exception as e:
                        entity_list.append(None)
                        continue


                all_entities.append(', '.join(entity_list))

            df['entity'] = all_entities
        
        output_path = f'{self.output_path_base}/{self.subject}/{self.file_name}/chunked_df_{self.file_name}.csv'
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        df.to_csv(output_path, index=False)

        return df 

    def GEO_parser(self):
        def dify_structuring(question_chunk):
            headers = {
                "Authorization": f"Bearer {self.geo_api_key}",
                "Content-Type": 'application/json'
            }
            request_data = {
                "inputs": {
                    "Question": question_chunk, 
                },
                "user": self.dify_user
            }
            response = requests.post(self.api_url, headers=headers, json=request_data)
            response_text = response.text
            response_json = json.loads(response_text)
            output = response_json["data"]["outputs"]
            raw_str = output['Structure']
            cleaned_str = re.sub(r'`json|\`', '', raw_str)
            cleaned_str = cleaned_str.strip()
            data = json.loads(cleaned_str)
            return data
        
        with open(self.paper_path, 'r', encoding='utf-8') as f:
            text = f.read()
        text = text.replace('.', '. ')
        text = text.replace('.  ', '. ')
        translation_table = str.maketrans({
                    '．': '.',
                    '（': '(',
                    '）': ')',
                    '，': ','
                })
        text = text.translate(translation_table)

        sections = re.split(r'^#\s+[一二三四五六七八九十、]+.*$', text, flags=re.MULTILINE)

        question_text_collection = []
        question_collection = []
        answer_collection = []
        knowledge_collection = []

        choice_question = []
        index_set = []
        choice_questions = []
        for sec in sections[1:]:
            if '#' not in sec[:20]:
                choice_question.append(sec)
        for question in choice_question:
            structure = dify_structuring(question)
        structure = structure['text']
        for question in choice_question:
            pattern = re.escape(question[10:]) 
            match = re.search(pattern, text)
            if match:
                end_index = match.end() - 1
            for set in structure:
                pattern = re.escape(set[:10]) 
                match = re.search(pattern, text)
                if match:
                    start_index = match.start()
                    index_set.append(start_index)
            for i in range(len(index_set)):
                start = index_set[i]
                try:
                    end = index_set[i + 1]
                    que = text[start:end]
                    choice_questions.append(que)
                except Exception as e:
                    que = text[start:end_index]
                    choice_questions.append(que)
        for quest in choice_questions:
            before, sep, after = quest.partition("【答案】")
            question = before
            answer = sep + after
            
            answer_collection.append(answer)
            knowledge_list = []
            small_questions = question.split('## ')

            question_text_collection.append(small_questions[0])
            question_collection.extend(small_questions[1:])
            for char in small_questions[1:]:
                try:
                    knowledge = Linking.link_question_with_entity(char)
                    knowledge_list.append(knowledge)
                except Exception as e:
                    knowledge_list.append('None')
                    continue
            knowledge_str = ', '.join(knowledge_list)
            knowledge_collection.append(knowledge_str)

        written_questions = []
        for sec in sections[1:]:
            if '#' in sec[:25]:
                written_questions.append(sec)
        for question in written_questions:
            pattern = re.compile(r'## (.*?)【答案】', re.S)
            pattern_ans = re.compile(r'【答案】(.*?)(?=##|$)', re.S)
            questions = pattern.findall(question)
            answers = pattern_ans.findall(question)

            for question in questions:
                knowledge_list = []
                if '###' in question:
                    quests = question.split('### ')
                    question_collection.extend(quests[1:])
                    question_text_collection.extend(quests[0])
                    for quest in quests[1:]:

                        try:
                            knowledge = Linking.link_question_with_entity(quest)
                            knowledge_list.append(knowledge)
                        except Exception as e:
                            knowledge_list.append('None')
                            continue
                else:
                    try:
                            knowledge = Linking.link_question_with_entity(quest)
                            knowledge_list.append(knowledge)
                    except Exception as e:
                        knowledge_list.append('None')
                        continue
                knowledge_str = ', '.join(knowledge_list)
                knowledge_collection.append(knowledge_str)

            answer_collection.extend(answers)

        df = pd.DataFrame()
        max_len = max(len(question_text_collection), len(answer_collection), len(knowledge_collection))

        if len(question_text_collection) < max_len:
            question_text_collection.extend([None] * (max_len - len(question_text_collection)))
        if len(answer_collection) < max_len:
            answer_collection.extend([None] * (max_len - len(answer_collection)))
        if len(knowledge_collection) < max_len:
            knowledge_collection.extend([None] * (max_len - len(knowledge_collection)))

        assert len(question_text_collection) == len(answer_collection) == len(knowledge_collection), \
            "列表长度仍不一致，请在输出文件夹内检查数据！"
        
        df['question_text'] = question_text_collection
        df['question'] = question_collection
        df['answer and analysis'] = answer_collection
        df['entity'] = knowledge_collection

        output_path = f'{self.output_path_base}/{self.subject}/{self.file_name}/chunked_df_{self.file_name}.csv'
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        df.to_csv(output_path, index=False)

        return df
        
    def GENERAL_parser(self):
        with open(self.paper_path, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('.', '. ')
        content = content.replace('.  ', '. ')
        translation_table = str.maketrans({
                    '．': '.',
                    '（': '(',
                    '）': ')',
                })
        content = content.translate(translation_table)
        
        knowledges=[]
        question_text_collection = []
        question_collection = []

        pattern = re.compile(r'## (.*?)【答案】', re.S)
        pattern_ans = re.compile(r'【答案】(.*?)(?=##|$)', re.S)
        questions = pattern.findall(content)
        answers = pattern_ans.findall(content)
        
        for question in questions:

            if any(x in question for x in ['A. ', 'B. ', 'C. ', 'D ']):
                # 选择题
                lines = question.split('\n')
                split_index = -1
                for i, line in enumerate(lines):
                    if any(opt in line for opt in ['A. ', 'B. ', 'C. ', 'D. ']):
                        split_index = i
                        break
                if split_index != -1:
                    part1 = '\n'.join(lines[:split_index]) 
                    part2 = '\n'.join(lines[split_index:]) 
                else:
                    part1 = question 
                    part2 = ""   

                question_text_collection.append(part1)
                question_collection.append(part2)
            elif '###' in question:
                # 主观题
                lines = question.split('\n')
                split_index = -1
                for i, line in enumerate(lines):
                    if '###' in line:
                        split_index = i
                        break

                if split_index != -1:
                    part1 = '\n'.join(lines[:split_index]) 
                    part2 = '\n'.join(lines[split_index:]) 
                else:
                    part1 = question 
                    part2 = ""   
                question_text_collection.append(part1)
                question_collection.append(part2)
            else:
                # 填空题
                question_str = question.split('则')
                question_text_collection.append(question_str[0])
                question_collection.append(question_str[1])

            try:
                knowledge = Linking.link_question_with_entity(question)
                knowledges.append(knowledge)
            except Exception as e:
                knowledges.append(None)
                continue
        df=pd.DataFrame()
        df["question_text"]=question_text_collection
        df['questions'] = question_collection
        df["analysis"]=answers
        df["entity"]=knowledges

        for ind, row in df.iterrows():
            if row['knowledges'] == None:
                question = row['questions']
                chinese_chars = re.findall(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', question)
                question = ''.join(chinese_chars)
                try:
                    knowledge = Linking.link_question_with_entity(question)
                    row['knowledges'] = knowledge
                except Exception as e:
                    continue
            else:
                continue 
        output_path = f'{self.output_path_base}/{self.subject}/{self.file_name}/chunked_df_{self.file_name}.csv'
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
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
            "user": self.dify_user
        }
        response = requests.post(self.api_url, headers=headers, json=request_data, timeout=150)
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

