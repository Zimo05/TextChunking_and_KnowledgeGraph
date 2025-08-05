from elasticsearch import Elasticsearch
from Config.Settings import settings
from elasticsearch.helpers import bulk
from typing import List, Dict

"""
修改搜索逻辑和搜索范围：

"""

class ESImporter:
    def __init__(self):
        self.es = Elasticsearch(hosts=[settings.Designer['ES']['ES_URL']],
                                http_auth=(settings.Designer['ES']['ES_USER'], settings.Designer['ES']['ES_PASSWORD']),
                                headers={"Accept":"application/json","Content-Type": "application/json"})
        self.index_name = "textbook_sections"

    def create_index(self,  index_name: str = "textbook_sections"):
        mapping = {
            "mappings": {
                "properties": {
                    #ik_max_word:分出尽量多的关键词，ik_smart:分出语义更相关的关键词
                    "title": {"type": "text", "analyzer": "ik_max_word"},
                    "content": {"type": "text", "analyzer": "ik_max_word"},
                    "level": {"type": "integer"}
                }
            }
        }
        self.index_name=index_name
        self.es.indices.create(index=self.index_name, body=mapping)

    #查询是否已有index
    def has_index(self,index_name):
        return self.es.indices.exists(index=index_name)

    #查询是否已有data
    def has_data(self,index_name):
        return self.es.count(index=index_name)["count"] > 0

    def import_sections(self, sections: List[Dict]):
        actions = [
            {
                "_index": self.index_name,
                "title": section["title"],
                "content": ". ".join(section["content"]),
                "level": section["level"],
                "reference":section["reference"]
            }
            for section in sections
        ]
        bulk(client=self.es, actions=actions)

    def match_phrase(self, query: str):
        body = {
            "query": {
                "match_phrase": {
                    "content":query
                }
            },
            # "min_score": 3.0
        }
        return self.es.search(index=self.index_name, body=body)

    def fuzzy_search(self, query: str, fuzziness: str = "AUTO"):
        body = {
            "query": {
                "match": {
                    "key":query,
                    "fuzziness": fuzziness
                }
            }
        }
        return self.es.search(index=self.index_name, body=body)

    def delete_index(self, index_name):
        return self.es.indices.delete(index=index_name)
    
Importer = ESImporter()