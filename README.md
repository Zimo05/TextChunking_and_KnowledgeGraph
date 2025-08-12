# TextChunking_and_KnowledgeGraph
This program is used to chunk textbook and papers and then structurize them into a DAG using neo4j, we silmutaneously conbine the data you input with knowledge instance offered by THU.
- for Textbook: we chunked the textbook into -> text content chunks with length between 600 and 1000, title to which it belongs and parent title to which it belongs, knowledge instance, relationships
- for Papers: we chunked the Papers into -> question, answer and analysis, knowledge

## MinerU configuration:
1. Inside the TextChunking_and_KnowledgeGraph folder, pull the MinerU repositpry
   - git clone https://github.com/opendatalab/MinerU.git
2. **Create a virtual environment, run the requirement.txt：** pip install -r requirements.txt
3. **(API version)Confugure:** Apply MinerU API om the official website: https://mineru.net/apiManage

## USING Guidance:
1. Designer:
- Open the Config.Settings to modify the dify, neo4j and elastic search API key and personal settings
- Update the input and output data paths as needed
2. User:
- Open the UserImplementation folder to run the UserCommand.py
- follow the guidance to complete the file uploading and Configure settings
- **For input data**:
     - If you are using this to chunk English questions, do not input English paper, because this chunking program of English is specialized for chunking “阅读理解， 完形填空， 语法填空， 七选五”，and please name the file as the question type within.
     - For input papers: you are recommended to input papers with answer and analysis.
 



Acknowledgement:
1. Thanks for **[MinerU](https://github.com/opendatalab/MinerU)** for offering fundamental pdf transformation tool.
2. Thanks for **[DeepSeek](https://github.com/deepseek-ai)** for offering advanced AI models and open-source resources.
