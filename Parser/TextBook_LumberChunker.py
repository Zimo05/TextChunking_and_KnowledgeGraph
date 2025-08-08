from Config.Settings import setting
from openai import OpenAI
import pandas as pd
from EntityLinking.Entity_Linking import Linking
import re
import queue
import spacy
import os

"""
最后要整理成df的形式
"""

class LumberChunker:
    def __init__(self, BookTree, file_name):
        self.client = OpenAI(api_key = setting.Designer['DEEPSEEK']['API'], base_url="https://api.deepseek.com")
        self.nlp_Chi = spacy.load("zh_core_web_sm")
        self.nlp_Eng = spacy.load("en_core_web_sm")
        self.subject = setting.USER['subject']
        self.output_path_base = setting.Designer['Storage']['Parser']['Chunked_book']
        self.file_name = file_name.replace('.pdf', '')
        self.BookTree = BookTree

    def lumberchunker(self):
            chunked_data = []
        # data_separate是不管层级的展开的分类，   NewBookTree是管层级的
            for chapter1 in self.book_tree: # 一集
                Chapter_structure = self._initialize_chapter_structure(chapter1)
                extra_question = queue.Queue()

                for chapter2 in chapter1.children: # 二级
                    chapter2_content_list = []
                    data_separate = self._initialize_data_separate(chapter2)
                    
                    Chapter_structure[chapter1]["sections"][chapter2] = chapter2_content_list   
                    # 后面记得处理二级标题下的内容，用三级标题多出来的extra question，二级一下的多出来的储存好，最后放进大章节的内容里
                    for chapter3 in chapter2.children:
                        # 判断节点是否为知识点，是的话就形成dict加进chapter2的list，不是的话，就加进问题,最后统一处理进chapter2的问题块

                        chapter3_content_dict = self._classify_node(chapter3, data_separate, chapter2_content_list)

                        if chapter3_content_dict is not None:
                            self._process_child_chapters(chapter3, data_separate, chapter3_content_dict[chapter3])
                            # 以上就是把所有的知识节点都存进去了，下面处理content

                    # question content
                    question_content = self._clean_question_content(data_separate['题目'])
                    question_content_queue = self._split_sentences_general(question_content)

                    # 处理知识节点
                    for ch3_dict in chapter2_content_list:
                        for key, list in ch3_dict.items():
                            self._chunk_all_nodes(key, question_content_queue, ch3_dict)

                    # 处理chapter2.content：
                    self._process_chapter_content(chapter3, chapter2_content_list, question_content_queue)

                    if not question_content_queue.empty(): # Remaining question content
                        self._handle_remaining_questions(question_content_queue, chapter2_content_list, extra_question)
                    Chapter_structure[chapter1]['sections'][chapter2] = chapter2_content_list

                self._process_top_level_chapter_content(chapter1, Chapter_structure, extra_question)            

                chunked_data.append(Chapter_structure)
            return chunked_data

    def _process_chapter_content(self, chapter, content_list, question_queue):
        check = self._check_len(chapter.content)
        if check == 'OK':
            content_list.append(chapter.content)
        elif check == 'LARGE':
            content_list.append(chapter.content[:800])
            remaining = chapter.content[800:]
            if remaining:
                question_queue.put(remaining)
        else:  # SMALL
            combined = chapter.content
            while not question_queue.empty() and len(combined) < 600:
                combined += "\n" + question_queue.get()
            
            if len(combined) > 1000:
                content_list.append(combined[:800])
                if len(combined) > 800:
                    question_queue.put(combined[800:])
            else:
                content_list.append(combined)

    def _process_top_level_chapter_content(self, chapter, book_tree, extra_questions):
        def process_large_content(content):
            sentences = self._split_sentences_general(content)
            chunks = []
            current_chunk = ''
            while not sentences.empty():
                sentence = sentences.get()
                if len(current_chunk) + len(sentence) <= 1000:
                    current_chunk += sentence + "\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence + "\n"
                    while len(current_chunk) > 1000:
                        chunks.append(current_chunk[:1000])
                        current_chunk = current_chunk[1000:]
            if current_chunk:
                chunks.append(current_chunk.strip())
            return chunks
        def process_small_content(content, extra_questions):
            while len(content) < 600 and not extra_questions.empty():
                content += "\n" + extra_questions.get()
            
            if len(content) > 1000:
                chunk = content[:1000]
                remaining = content[1000:]
                extra_questions.put(remaining)
                return [chunk]
            else:
                return [content]
        def handle_extra_questions(extra_questions, content_list):
            current_chunk = ''
            while not extra_questions.empty():
                question = extra_questions.get()
                if len(current_chunk) + len(question) + 1 <= 1000:
                    current_chunk += question + "\n"
                    if len(current_chunk) >= 600:
                        content_list.append(current_chunk.strip())
                        current_chunk = ''
                else:
                    if current_chunk:
                        content_list.append(current_chunk.strip())
                    current_chunk = question + "\n"
                    while len(current_chunk) > 1000:
                        content_list.append(current_chunk[:1000])
                        current_chunk = current_chunk[1000:]
            
            if current_chunk:
                content_list.append(current_chunk.strip())  
        
        content_list = book_tree[chapter]['content']
        chapter_content = chapter.content
        check = self._check_len(chapter_content)
        
        if check == 'OK':
            content_list.append(chapter_content)
        elif check == 'LARGE':
            chunks = process_large_content(chapter_content)
            content_list.extend(chunks)
        else: 
            small_chunks = process_small_content(chapter_content, extra_questions)
            content_list.extend(small_chunks)
        handle_extra_questions(extra_questions, content_list)

    def _initialize_chapter_structure(self, chapter):
        return {
                    chapter: {
                        "content": [],
                        "sections": {}
                    }
                }

    def _initialize_data_separate(self, chapter):
        return {
                    '知识': [chapter],
                    '题目': ''
                }

    def _process_child_chapters(self, parent_chapter, data_separate, parent_content_list:list):
        # parent_chapter：relative一级
        if not parent_chapter.children:
            return

        for child in parent_chapter.children:
            child_dict = self._classify_node(child, data_separate, parent_content_list)
            if child_dict is not None:
                child_content = child.content
                if len(child_content) < 600:
                    parent_content_list = parent_content_list[:-1]
                while len(child_content) > 1000:

                    child_dict[child].append(child_content[:1000])
                    child_content = child_content[1000:]
                
                if child_content:
                    if len(child_content) > 600:
                        child_dict[child].append(child_content)
                        break
                    else:
                        break


    def _clean_question_content(self, question_content):
        return "\n".join([line for line in question_content.splitlines() if line.strip()])

    def _chunk_all_nodes(self, chapter, question_content_queue:queue.Queue, chapter_dict):

        check = self._check_len(chapter.content)
        if check == 'OK':
            chapter_dict[chapter].append(chapter.content)
        elif check == 'SMALL':
            self._handle_small_chunk(chapter_dict, chapter, question_content_queue)
        elif check == 'LARGE':
            self._handle_large_chunk(chapter_dict, chapter, question_content_queue)

    def _handle_small_chunk(self, chapter_dict, chapter:dict, question_queue:queue.Queue):
        content = chapter.content
        max_iterations = 100  # Prevent infinite loops
        iteration = 0
        
        while (not question_queue.empty() and 
               len(content) < 600 and 
               iteration < max_iterations):
            content += "\n" + question_queue.get()
            iteration += 1

        if len(content) > 1000:
            chapter_dict[chapter].append(content[:800])
            remaining = content[800:]
            if remaining:
                question_queue.put(remaining)
        else:
            chapter_dict[chapter].append(content)

    def _handle_large_chunk(self, chapter_dict, chapter, question_queue: queue.Queue):
        tmp_queue = self._split_sentences_general(chapter.content)
        tmp_chunk = ''
        max_iterations = 200
        iteration = 0
        
        while (not tmp_queue.empty() and iteration < max_iterations): 
            sentence = tmp_queue.get()
            iteration += 1
            
            if len(tmp_chunk) + len(sentence) > 800:
                if len(tmp_chunk) >= 600:
                    chapter_dict[chapter].append(tmp_chunk)
                    tmp_chunk = sentence + "\n"
                else:
                    tmp_chunk += sentence + "\n"
                    if len(tmp_chunk) > 1200:
                        chapter_dict[chapter].append(tmp_chunk[:len(tmp_chunk)//2])
                        chapter_dict[chapter].append(tmp_chunk[len(tmp_chunk)//2:])
                        tmp_chunk = ''
            else: 
                tmp_chunk += sentence + "\n"
        
        if tmp_chunk:
            if len(tmp_chunk) >= 600:
                chapter_dict[chapter].append(tmp_chunk)
            else:
                if not question_queue.empty() and len(tmp_chunk) < 800:
                    additional = question_queue.get()
                    if len(tmp_chunk) + len(additional) > 800:
                        remaining = 800 - len(tmp_chunk)
                        tmp_chunk += additional[:remaining]
                        chapter_dict[chapter].append(tmp_chunk)
                        question_queue.put(additional[remaining:])
                    else:
                        tmp_chunk += "\n" + additional
                        chapter_dict[chapter].append(tmp_chunk)
                else:
                    question_queue.put(tmp_chunk)

    def _handle_remaining_questions(self, question_queue, chapter_content_list, extra_question:queue.Queue):
        # chapter_content_dict: NewBookTree[chapter1]['sections']
        # Handle remaining questions in the queue
        if question_queue.empty():
            return
            
        tmp_chunk = ''
        node = Node('习题与思考', 2)
        node_dict = {node: []}
        chapter_content_list.append(node_dict)
        max_iterations = 200
        iteration = 0
        
        while not question_queue.empty() and iteration < max_iterations:
            tmp_chunk += question_queue.get() + "\n"
            iteration += 1
            
            if len(tmp_chunk) >= 600:
                if len(tmp_chunk) > 1000:
                    node_dict[node].append(tmp_chunk[:800])
                    remaining = tmp_chunk[800:]
                    question_queue.put(remaining)
                    tmp_chunk = ''
                else:
                    node_dict[node].append(tmp_chunk)
                    tmp_chunk = ''
        
        if tmp_chunk:
            extra_question.put(tmp_chunk.strip())

    def _classify_node(self, ChapterNode: Node, data_separate, parent_content_list:list):
        title = ChapterNode.title
        prompt = f'你觉得“{title}“这是个知识点的标题吗，如果是返回1，不是返回0'
        response = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {"role": "system", "content": "你是个聪明的老师"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        judge = response.choices[0].message.content
        
        if judge == '1':
            data_separate['知识'].append(ChapterNode)
            ChildChapterDict = {ChapterNode: []}
            parent_content_list.append(ChildChapterDict)
            return ChildChapterDict

        else:
            content = ChapterNode.content
            data_separate['题目'] += content
            return None
        
        
    def _check_len(self, chunk):
        length = len(chunk)
        if 600 <= length <= 800:
            return 'OK'
        elif length < 600:
            return 'SMALL'
        elif length > 800:
            return 'LARGE'

    def _split_sentences_general(self, text: str) -> queue.Queue:
        replacements = {
            "tables": [],
            "latex": [],
            "images": []
        }

        def replace_table(match):
            replacements["tables"].append(match.group(0))
            return f"@@TABLE{len(replacements['tables']) - 1}@@"

        def replace_latex(match):
            expr = match.group(0)
            replacements["latex"].append(expr)
            return f"@@LATEX{len(replacements['latex']) - 1}@@"

        def replace_image(match):
            replacements["images"].append(match.group(0))
            return f"@@IMAGE{len(replacements['images']) - 1}@@"

        text = re.sub(r'<table.*?>.*?</table>', replace_table, text, flags=re.DOTALL)

        latex_pattern = r'\$\$.*?\$\$|\$.*?\$|\\\[.*?\\\]|\\\(.*?\\\)'
        text = re.sub(latex_pattern, replace_latex, text, flags=re.DOTALL)

        text = re.sub(r'!\[.*?\]\((.*?)\)', replace_image, text)
        protected_text = (
            text.replace('@@LATEX', 'LATEXPROTECTED')
                .replace('@@IMAGE', 'IMAGEPROTECTED')
                .replace('@@TABLE', 'TABLEPROTECTED')
        )
        if self.subject == 'English':
            doc = self.nlp_Eng(protected_text)
        else:
            doc = self.nlp_Chi(protected_text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        restored_sentences = queue.Queue()
        for sent in sentences:
            sent = (
                sent.replace('LATEXPROTECTED', '@@LATEX')
                    .replace('IMAGEPROTECTED', '@@IMAGE')
                    .replace('TABLEPROTECTED', '@@TABLE')
            )
            for i, table in enumerate(replacements["tables"]):
                sent = sent.replace(f"@@TABLE{i}@@", table)
            for j, latex in enumerate(replacements["latex"]):
                sent = sent.replace(f"@@LATEX{j}@@", latex)
            for k, img in enumerate(replacements["images"]):
                sent = sent.replace(f"@@IMAGE{k}@@", img)
            restored_sentences.put(sent)

        return restored_sentences


    def text_to_table(self, Chunked_book):
        data = []

        for parent1, value in Chunked_book.items():  # 章节: 第一章
            parent1_title = parent1.title
            subcha = Chunked_book.get(parent1)

            parent1_content = subcha['content']
            for entry in parent1_content:
                if entry and str(entry).strip():
                    data.append({
                        'parent': parent1_title,
                        'relation1': '同位',
                        'chapter_title': parent1_title,
                        'relation2': '文本块',
                        'content': entry
                    })

            parent1_sections = subcha['sections']
            for parent2, value in parent1_sections.items():  # 课: 1.1: []
                parent2_title = parent2.title
                subsubcha = parent1_sections.get(parent2)

                for entry in subsubcha:  # 课的 content
                    if isinstance(entry, str):
                        if entry and str(entry).strip(): 
                            data.append({
                                'parent': parent1_title,
                                'relation1': '上位',
                                'chapter_title': parent2_title,
                                'relation2': '文本块',
                                'content': entry
                            })
                    elif isinstance(entry, dict):
                        for parent3, value in entry.items():  # 课的小节
                            parent3_title = parent3.title
                            for entry in value:
                                if isinstance(entry, dict):
                                    for parent4, value in entry.items():
                                        parent4_title = parent4.title
                                        for entry in value:
                                            if entry and str(entry).strip(): 
                                                data.append({
                                                    'parent': parent3_title,
                                                    'relation1': '上位',
                                                    'chapter_title': parent4_title,
                                                    'relation2': '文本块',
                                                    'content': entry
                                                })
                                elif isinstance(entry, str):
                                    if entry and str(entry).strip():
                                        data.append({
                                            'parent': parent2_title,
                                            'relation1': '上位',
                                            'chapter_title': parent3_title,
                                            'relation2': '文本块',
                                            'content': entry
                                        })

        df = pd.DataFrame(data, columns=['parent', 'relation1', 'chapter_title', 'relation2', 'content'])

        Entity_list_self = []
        Entity_list_father = []
        for ind, row in df.iterrows():
            parent = row['parent']
            itself = row['chapter_title']

            Entity_list_father.append(Linking.link_book_with_entity(parent))
            Entity_list_self.append(Linking.link_book_with_entity(itself))
            
        df['Entity_father'] = Entity_list_father
        df['Entity_self'] = Entity_list_self

        return df

    def main1(self):
        Book = self.lumberchunker()
        return Book
    
    def mian2(self, Books):
        df_list = []
        for book in Books:
            key = book.keys()
            if key.title == '目录':
                continue
            else:
                df = self.text_to_table(book)
                df_list.append(df)

        df = pd.concat(df_list, axis=0)

        file_name_base = self.file_name
        output_path = f'{self.output_path_base}/{self.subject}/{file_name_base}/chunked_data.csv'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        df.to_csv(output_path, index=False)
        return df
