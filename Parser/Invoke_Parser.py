from Parser.TextBook_LumberChunker import Chunker
from Parser.md_paper_parser import paper_parser
from Config.Settings import setting
from PDF_to_MD.Check_File_Type import file_judge
from openai import OpenAI

class InvokeParser:
    def __init__(self):
        self.file_judge = file_judge
    def invoke_parser(self):
        if self.file_judge['file_type'] == 'Book':
            # 教材
            chunked_book, df = Chunker.main()
            return chunked_book, df
        else:
            # 试卷
            if self.file_judge['is ENG']:
                # 英语
                paper_df = paper_parser.ENG_parser()
                return None, paper_df
            else:
                paper_df = paper_parser.GENERAL_parser()
                return None, paper_df

invoking_Parser = InvokeParser()  
chunk, df = invoking_Parser.invoke_parser()  