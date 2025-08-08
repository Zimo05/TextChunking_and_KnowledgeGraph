from Parser.TextBook_LumberChunker import LumberChunker
from Parser.md_paper_parser import PaperParser

class InvokeParser:
    def __init__(self, BookTree, md_content_path, file_name, file_judge):
        self.file_judge = file_judge
        self.file_name = file_name
        self.BookTree = BookTree
        self.md_content_path = md_content_path

    def invoke_parser(self):
        if self.file_judge['file_type'] == 'Book':
            # 教材
            Chunker = LumberChunker(self.BookTree, self.file_name)
            chunked_book = Chunker.main1()
            df = Chunker.mian2()
            return chunked_book, df
        else:
            # 试卷
            paper_parser = PaperParser(self.md_content_path, self.file_name)
            if self.file_judge['is ENG']:
                # 英语
                paper_df = paper_parser.ENG_parser()
                return None, paper_df
            else:
                paper_df = paper_parser.GENERAL_parser()
                return None, paper_df
