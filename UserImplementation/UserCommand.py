class Implement:

    def Question_Generate(self):
        # 出题助手：Input subject(s)
        knowledge_options = ['语文(CHI)', '数学(MAT)', '英语(ENG)', '物理(PHY)', 
                            '化学(CHM)', '生物(BIO)', '政治(POL)', '历史(HIS)', '地理(GEO)']
        
        for i, subject in enumerate(knowledge_options, 1):
            print(f"{i}. {subject}")

        print("Please choose subjects(Input the number and Separate by commas):")
        choice = input("你的选择(如:1,3,5): ").strip()
        selected_indices = [int(idx.strip())-1 for idx in choice.split(',')]
        selected_subjects = [knowledge_options[idx] for idx in selected_indices]
        from Config.Settings import setting
        setting.USER['knowledge'] = selected_subjects
        
        
        # Dealing with muktiple subjects(出题助手, 对接章哥)

    def Corpus_Search(self):
        # Search for corpus(ES Importer)
        return

    def Knowlwdge_Graph(self):
        # Input subject
        from Config.Settings import setting

        while True:
            check = input("""Please go to the setting page to configure the following:
                        1. DIFY_ENG_Paper_Parser_API
                        2. DIFY_Entity_Linking_API
                        3. DIFY_Entity_Book_Linking_API
                        4. DIFY_Correction_API
                        5. DIFY_GEO_Paper_Parser_API
                        6. DIFY_TextBook_Question_Answer
                        7. DIFY_USER
                        8. MinerU_Token
                        9. MD_file
                        10. Chunked_paper
                        11. Chunked_book
              
              If all done, enter ok
              """)
            if check == 'ok':
                break
            else:
                print('Invalid input')
                continue

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
        setting.USER['file_path'] = input('Please enter your file path(Drag the file into the terminal): ').strip("'\"") #'./Data/Original/教材/高中数学必修第一册A版/高中数学必修第一册A版.md'

        from PDF_to_MD.Check_File_Type import CheckFileType
        check = CheckFileType()
        file_name = check.get_filename_from_path()
        file_judge = check.File_type()

        from PDF_to_MD.MinerU_Transform import PDFProcessor
        processor = PDFProcessor(file_judge, file_name)
        mineru_zip_path = processor.main()

        from PDF_to_MD.LLM_correction import correction
        Correction = correction(mineru_zip_path, file_name, file_judge)
        corrected_md, md_content_path = Correction.pre_processing()
        corrected_md, md_content_path = Correction.main()
        print('Revision complete!')

        from Parser.Invoke_Parser import InvokeParser
        parser = InvokeParser(md_content_path, file_name, file_judge)
        Chunked_df = parser.invoke_parser()

        if file_judge['file_type'] == 'Book':
            check = input('Do you want to chunk text book questions?(yes/no): ')
            if check == 'yes':
                from Parser.MD_section_parser import MD_parser
                Parser = MD_parser(md_content_path)
                BookTree = Parser.parse_markdown_to_linked_lists()
                from Parser.Chunking_TextBook_Questions import TextBookQuestion
                Chunker = TextBookQuestion(BookTree, file_name)
                TBQ_df = Chunker.Question_Chunking()
            
        return Chunked_df
    
implementation = Implement()
Chunked_df = implementation.Knowlwdge_Graph()
