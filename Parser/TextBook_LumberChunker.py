from Parser.MD_section_parser import BookTree, Node
from Config.Settings import setting
from openai import OpenAI
import pandas as pd
from EntityLinking.Entity_Linking import Linking
from PDF_to_MD.Check_File_Type import file_name
import re
import queue
import spacy

"""
最后要整理成df的形式
"""

class LumberChunker:
    def __init__(self, BookTree):
        self.client = OpenAI(api_key = setting.Designer['DEEPSEEK']['API'], base_url="https://api.deepseek.com")
        self.nlp_Chi = spacy.load("zh_core_web_sm")
        self.nlp_Eng = spacy.load("en_core_web_sm")
        self.subject = setting.USER['subject']
        self.output_path_base = setting.Designer['Storage']['Parser']['Chunked_book']
        self.file_name = file_name
        self.BookTree = BookTree

    def lumberchunker(self):
        chunked_data = []
    # data_separate是不管层级的展开的分类，   NewBookTree是管层级的
        for chapter1 in self.BookTree: # 一集
            NewBookTree = self._initialize_chapter_structure(chapter1)
            extra_question = queue.Queue()

            for chapter2 in chapter1.children: # 二级
                chapter2_content_list = []
                data_separate = self._initialize_data_separate(chapter2)
                
                NewBookTree[chapter1]["sections"][chapter2] = chapter2_content_list   
                # 后面记得处理二级标题下的内容，用三级标题多出来的extra question，二级一下的多出来的储存好，最后放进大章节的内容里
                for chapter3 in chapter2.children:
                    # 判断节点是否为知识点，是的话就形成dict加进chapter2的list，不是的话，就加进问题,最后统一处理进chapter2的问题块

                    self._classify_node(chapter3, data_separate, chapter2_content_list)

                    if chapter3 in data_separate['知识']:
                        chapter3_content_dict = {chapter3:[]}
                        chapter2_content_list.append(chapter3_content_dict)
                        # child chapters，处理四级标题的东西
                        self._process_child_chapters(chapter3, data_separate, chapter3_content_dict[chapter3])
                        # 以上就是把所有的知识节点都存进去了，下面处理content

                # question content
                question_content = self._clean_question_content(data_separate['题目'])
                question_content_queue = self._split_sentences_general(question_content)

                # 处理知识节点
                for entry in chapter2_content_list:
                    for key in entry.keys():
                        self._chunk_all_nodes(key, question_content_queue, entry)

                # 处理chapter2.content：
                self._classify_node(chapter3, data_separate, chapter2_content_list)

                if not question_content_queue.empty(): # Remaining question content
                    self._handle_remaining_questions(question_content_queue, chapter2_content_list, extra_question)

            self._process_top_level_chapter_content(chapter1, NewBookTree, extra_question)            

            chunked_data.append(NewBookTree)
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
        chapter_content = chapter.content
        check = self._check_len(chapter_content)
        content_list = book_tree[chapter]['content']
        
        if check == 'OK':
            content_list.append(chapter_content)
        elif check == 'LARGE':
            sentences = self._split_sentences_general(chapter_content)
            tmp_chunk = ''
            while not sentences.empty():
                sentence = sentences.get()
                if 600 < len(tmp_chunk) + len(sentence) < 1000:
                    tmp_chunk += sentence + "\n"
                    content_list.append(tmp_chunk)
                    tmp_chunk = ''
                elif len(tmp_chunk) + len(sentence) < 600:
                    tmp_chunk += sentence + "\n"
                else:
                    content_list.append(tmp_chunk[:1000])
                    tmp_chunk = sentence + "\n"
            
            if tmp_chunk:
                content_list.append(tmp_chunk)
        else:  # SMALL
            while not extra_questions.empty() and len(chapter_content) < 600:
                chapter_content += "\n" + extra_questions.get()
            
            if len(chapter_content) > 1000:
                content_list.append(chapter_content[:1000])
                remaining = chapter_content[1000:]
                if remaining:
                    extra_questions.put(remaining)
            else:
                content_list.append(chapter_content)

        if not extra_questions.empty() and content_list:
            last_chunk = content_list[-1]
            while not extra_questions.empty():
                next_question = extra_questions.get()
                combined_length = len(last_chunk) + len(next_question) + 1 
                
                if combined_length <= 1000:
                    last_chunk += "\n" + next_question
                    content_list[-1] = last_chunk 
                else:
                    extra_questions.put(next_question)
                    break
        tmp_chunk = ''
        while not extra_questions.empty():
            question = extra_questions.get()
            if len(tmp_chunk) + len(question) + 1 <= 1000: 
                tmp_chunk += question + "\n"
                if len(tmp_chunk) >= 600:
                    content_list.append(tmp_chunk.strip())
                    tmp_chunk = ''
            else:
                if tmp_chunk:
                    content_list.append(tmp_chunk.strip())
                    tmp_chunk = question + "\n"
                else:
                    content_list.append(question[:1000])
                    remaining = question[1000:]
                    if remaining:
                        extra_questions.put(remaining)
        if tmp_chunk:
            content_list.append(tmp_chunk.strip())

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

        for child in parent_chapter.children:  # relative二级
            self._classify_node(child, data_separate, parent_content_list)           
            if child in data_separate['知识']:
                parent_content_list.append({child:[]})

    def _clean_question_content(self, question_content):
        return "\n".join([line for line in question_content.splitlines() if line.strip()])

    def _chunk_all_nodes(self, chapter:dict, question_content_queue:queue.Queue, chapter_dict):
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
        
        while not tmp_queue.empty() and iteration < max_iterations:
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
            parent_content_list.append({ChapterNode: []})

        else:
            content = ChapterNode.content
            data_separate['题目'] += content
        
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

        file_name_base = self.file_name
        file_name_base = file_name_base.replace('.md', '')

        output_path = f'{self.output_path_base}/{self.subject}/{file_name_base}/'
        df.to_csv(output_path, index=False)

        return df

    def main(self):
        Book = self.lumberchunker()
        Chunked_book = Book[0]
        df = self.text_to_table(Chunked_book)

        return Chunked_book, df

Chunker = LumberChunker(BookTree)
