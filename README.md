# TextChunking_and_KnowledgeGraph
This program is used to chunk textbook and papers and then structurize them into a DAG using neo4j, we silmutaneously conbine the data you input with knowledge instance offered by THU.
- for Textbook: we chunked the textbook into -> text content chunks with length between 600 and 1000, title to which it belongs and parent title to which it belongs, knowledge instance, relationships
- for Papers: we chunked the Papers into -> question, answer and analysis, knowledge

## MinerU configuration:
1. Inside the TextChunking_and_KnowledgeGraph folder, pull the MinerU repositpry
   - git clone https://github.com/opendatalab/MinerU.git
2. **Create a virtual environment, run the requirement.txt：** pip install -r requirements.txt
3. **(API version)Confugure:** Apply MinerU API om the official website: https://mineru.net/apiManage

## Dify configuration:
1. Open Dify_DSL and import the yml files
2. Create a knowledge and import the knowledge tables from Entity Data
3. Enter into each app to configure **Knowledge Retrieval** node.

## USING Guidance:
- Open the Config.Settings：
     - Dify Confuguration: Configure the API keys
     - NEO4J API key
     - MinerU token
     - Deepseek API
- Update the input and output data paths (MD_file, Chunked_paper, Chunked_book) as needed(**If you are Mac user, do not modify, just skip this**)
  - (**For windows user**): Complete the file path prefix, for example: from ***./Data/Updated/Papers*** to ***D://USER/..../TextChunking_and_KnowledgeGraph/Data/Updated/Papers***
- Open the UserImplementation folder to run the UserCommand.py
- **For input data**:
     - For textbook: No specific requirement
     - For papers: Only special requirements for English, **Do not input a paper, Only one pdf of collection of question type within \['阅读理解', '完形填空', '语法填空'， '七选五'\] is acceptable**
- Lastly, follow the guidance within the instructions during code execution to complete the inspection and modification

### YML file declaration:
  - DIFY_ENG_Paper_Parser_API: Input is a paragragh string containing question and analysis, output is parsing structure signal
  - DIFY_Entity_Linking_API: Input is a question string output is an entity string
  - DIFY_Entity_Book_Linking_API: Input is a book title(or subtitle or subsubtitle or subsubsubtitle), output is an entity string
  - DIFY_Correction_API: Input is a chunk of text
  - DIFY_GEO_Paper_Parser_API: Input is a Geography choice question string, output is chunking signal
  - DIFY_TextBook_Question_Answer: Input is a question, output is answer and analysis



#### Acknowledgement:
1. Thanks for **[MinerU](https://github.com/opendatalab/MinerU)** for offering fundamental pdf transformation tool.
2. Thanks for **[DeepSeek](https://github.com/deepseek-ai)** for offering advanced AI models and open-source resources.
