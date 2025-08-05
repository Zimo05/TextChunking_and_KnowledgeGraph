class settings:
    Designer = {
        'DIFY': {
            'DIFY_ENG_Paper_Parser_API': '',
            'DIFY_Entity_Linking_API': '',
            'DIFY_Entity_Book_Linking_API': '',
            'DIFY_Correction_API': '',
            'DIFY_URL': "http://localhost/v1/workflows/run",
            'DIFY_USER': ''
            },
<<<<<<< HEAD
        'MinerU':{
            'API': 'eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI5MDMwOTkwMCIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc1NDM3MTEzMiwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiMjk4MDBjMzktMjg4ZS00MzVjLWFlZjEtZDVkNGE0MWQ3OWY3IiwiZW1haWwiOiIiLCJleHAiOjE3NTU1ODA3MzJ9.hCmv_9U2agTlLa_1UmVybmgLdFfYw7uaDXd36GS5Y-eKhB5OUdpHqfYRnuVVbJ4RSbm-dCKh5VX9b1fdRiajEw'
        },
=======
        'MinerU_Token': '', 
>>>>>>> 3d38c2326831804e4163824b0558d098a1d9032d
        'NEO4J': {
            'NEO4J_URL': '',
            'NEO4J_USERNAME': '',
            'NEO4J_PASSWORD': ''
            },
        'ES': {
            'ES_URL': '',
            'ES_USER': '',
            'ES_PASSWORD': ''
            },
        'DEEPSEEK': {
            'API': 'sk-16528769d4794f44a01c283443c88bec'
            },
        'Storage':{
                'PDF_to_MD':{
                    'MD_file':'' 
                },
                'Parser':{
                    'Chunked_paper':'./Data/Updated/Papers/',
                    'Chunked_book': './Data/Updated/TextBooks' 
                },            
            },
        'Entity_linking':{
            'Edukg_instance_info': '',
            'Entity_Table_Path': '', # 根据用户输入的科目，index to the table corresponding to the subject
            'Entity_level_index': '',
            'Output_path': '' # 用来存更新后的entity linking table
        }
        }
    
    USER = {
            'file_path': '',
            'knowledge': '',
            'interdisciplinary': '', # true or false, if true, choose subject_field, if false, choose subject
            'subject_field': '', 
            'subject':'',
            'question_type':'' # 出题助手
        }
    
setting = settings()


# Graph integration
