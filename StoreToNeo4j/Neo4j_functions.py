import os
from datetime import datetime
import pandas as pd
from neo4j import GraphDatabase, RoutingControl
from Config.Settings import settings

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    def create_knowledge_node(self, name: str, node_type: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MERGE (n:Knowledge {name: $name, type: $type})",
                    name=name, type=node_type
                )
            )

    def create_relationship(self, parent: str, child: str, rel_type: str):
        with self.driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    "MATCH (p:Knowledge {name: $parent}), (c:Knowledge {name: $child}) "
                    "MERGE (p)-[r:" + rel_type + "]->(c)",
                    parent=parent, child=child
                )
            )

    #输入实体类型查询实体
    def query_entities(self, entity_type: str,database="neo4j"):
        result = self.driver.execute_query(
            f"MATCH (n:{entity_type}) RETURN n.name",database_=database,
        )[0]
        entities = [record["n.name"] for record in result]
        entities=list(set(entities))
        return entities,len(entities)



    #输入实体名称和关系名称查询尾头实体
    def query_head_entities(self,entity_type:str, entity_name: str, relation_type: str,database="neo4j"):
        res=[]
        heads,tails,relations =[],[],[]
        if ',' in relation_type:
            tmp=relation_type.split(',')
            tmp=['`'+item+'`' for item in tmp]
            tmp='|'.join(tmp)
            result = self.driver.execute_query(
            f"MATCH (n)-[r:{tmp}]->(m:{entity_type} {{name: '{entity_name}'}}) RETURN n.name,type(r),m.name limit 10",database_=database,)
        else:
            result = self.driver.execute_query(
            f"MATCH (n:{entity_type} {{name: '{entity_name}'}})-[r:{relation_type}]->(m) RETURN n.name,type(r),m.name limit 10",database_=database,)
        if result.records:
            for record in result.records:
                entities = record["n.name"]
                heads.append(entities)
                tails.append(record["m.name"])
                relations.append(record["type(r)"])
                if entities not in res:
                    res.append(entities)
        df=pd.DataFrame({"head":heads,"tail":tails,"relation":relations})

        return res,len(res),df

    #查询跨学科相关实体
    def query_md_head_tail_entities(self,entity_type:str, entity_name: str, database="neo4j"):
        res=[]
        heads,tails,relations =[],[],[]
        result = self.driver.execute_query(
        f"MATCH (n:物理实体|化学实体|生物实体|语文实体|英语实体|政治实体|历史实体|地理实体)-[r]->(m:{entity_type} {{name: '{entity_name}'}}) RETURN n.name,type(r),m.name limit 10",database_=database,)

        result2 = self.driver.execute_query(
        f"MATCH (n:{entity_type} {{name: '{entity_name}'}})-[r]->(m:物理实体|化学实体|生物实体|语文实体|英语实体|政治实体|历史实体|地理实体) RETURN n.name,type(r),m.name limit 10",database_=database,)
        if result.records:
            for record in result.records:
                entities = record["n.name"]
                heads.append(entities)
                tails.append(record["m.name"])
                relations.append(record["type(r)"])
                if entities not in res:
                    res.append(entities)
        if result2.records:
            for record in result2.records:
                entities = record["n.name"]
                heads.append(entities)
                tails.append(record["m.name"])
                relations.append(record["type(r)"])
                if entities not in res:
                    res.append(entities)
        df=pd.DataFrame({"head":heads,"tail":tails,"relation":relations})

        return res,len(res),df

    #输入实体名称和关系名称查询尾实体和三元组属性
    def query_tail_entities(self,entity_type:str, entity_name: str, relation_type: str,database="neo4j"):
        res=[]
        heads,tails,relations =[],[],[]
        if relation_type=='真题' or relation_type=='教科书':
            result = self.driver.execute_query(
                #真题："properties": {"reference": "2022·高考数学真题/浙江","answer": "（1）
                #教科书："properties": {"reference": "高中数学必修第一册A版","level": 4,"title": "5.4.3 正切函数的性质与图象   -1.周期性"}
            f"MATCH (n:{entity_type} {{name: '{entity_name}'}})-[r:{relation_type}]->(m) RETURN n.name,type(r),m.name,properties(r) limit 5",database_=database,)
            if result.records:
                for record in result.records:
                    entities = record["m.name"]
                    properties = record["properties(r)"]
                    heads.append(record["n.name"])
                    #tmp=row['tail'].replace("\\","\\\\").replace("$","\$")[:40]+"..."
                    if relation_type=='真题':
                        tails.append(properties["reference"]+'\n'+entities.replace('$','\$')
                                     .replace('\\','\\\\')[:30]+"...")
                    elif relation_type=='教科书':
                        tails.append(properties["reference"]+'\n'+properties["title"])
                    relations.append(record["type(r)"])
                    res.append(entities+str(properties))
        else:
            if ',' in relation_type:
                tmp = relation_type.split(',')
                tmp = ['`' + item + '`' for item in tmp]
                tmp = '|'.join(tmp)
                result = self.driver.execute_query(
                f"MATCH (n:{entity_type} {{name: '{entity_name}'}})-[r:{tmp}]->(m) RETURN n.name,type(r),m.name limit 10",database_=database,)
            else:
                result = self.driver.execute_query(
                f"MATCH (n:{entity_type} {{name: '{entity_name}'}})-[r:{relation_type}]->(m) RETURN n.name,type(r),m.name limit 10",database_=database,)
            if result.records:
                for record in result.records:
                    entities = record["m.name"]
                    heads.append(record["n.name"])
                    tails.append(entities)
                    relations.append(record["type(r)"])
                    if entities not in res:
                        res.append(entities)
        df = pd.DataFrame({"head": heads, "tail": tails, "relation": relations})
        return res,len(res),df

    #输入实体名称，进行多跳查询
    def query_multi_hop(self,entity_type:str, entity_name: str, relation_types: list,hop_count=2,database="neo4j"):
        result = self.driver.execute_query(
            f"MATCH p=(n:{entity_type} {{name: '{entity_name}'}})-[*..{hop_count}]-(m) WHERE ALL(r IN "
            f"[rel IN relationships(p) | type(r) IN {relation_types}]) RETURN m.name,r.properties,r.relation_type",database_=database,
        )[0]
        entities = [record["m.name"] for record in result]
        properties=[record["r.properties"] for record in result]
        relation_type=[record["r.relation_type"] for record in result]
        res={}
        for e,p,r in zip(entities,properties,relation_type):
            res[e]={"relation_type":r,"properties":p}
        return res,len(res)

    #输入实体名称，进行社区发现
    def community_detection(self,entity_name:str,relation_type:str,database_:str="neo4j"):
        result=self.driver.execute_query(
            f"MATCH (n) {{name:'{entity_name}'}} SET n.community=id(n)"
            f"MATCH (n)-[:{relation_type}]-(m"
            f"WITH n,m.community AS neighborCommunity,count(*) AS freq"
            f"ORDER BY freq DESC"
            f"LIMIT 1"
            f"SET n.community=neighborCommunity "
            f"RETURN n.community "
        )
        return result,len(result)

    #输入实体名称，进行随机游走
    def random_walk(self,entity_name:str,relation_type:str,database_:str="neo4j"):
        result=self.driver.execute_query(
            f"MATCH (start:NodeLabel {id: '{entity_name}'})"
            f"CALL apoc.path.expandConfig(start,{{relationshipFilter:'{relation_type}',"
            f"minLevel:1,maxLevel:5,"
            f"uniqueness:'NODE_GLOBAL',"
            f"random:true}}"
            f") YIELD path RETURN [node in nodes(path)|node.id] AS randomWalkPath"
        )
        return result,len(result)

    #输入两个实体名称，通过lca比较相似度
    def lca(self,entity1:str,entity2:str,database_:str="neo4j"):
        result=self.driver.execute_query(
            f"MATCH (a:Node {id: '{entity1}'}),(b:Node {id:'{entity2}'})"
            f"CALL apoc.path.expandConfig(a,{{relationshipFilter:'<PARENT',"
            f"minLevel:1,maxLevel:10,"
            f"uniqueness:'NODE_GLOBAL',"
            f"random:true}}"
            f") YIELD path AS pathA"
            f"WITH b,nodes(pathA) as ancestorsA "
            f"CALL apoc.path.expandConfig(b,{{relationshipFilter:'<PARENT',"
            f"minLevel:1,maxLevel:10,"
            f"uniqueness:'NODE_GLOBAL',"
            f"random:true}}"
            f") YIELD path AS pathB"
            f"WITH ancestorsA,nodes(pathB) as ancestorsB"
            f"UNWIND ancestorA as ancestor"
            f"WHERE ancestor IN ancestorsB"
            f"RETURN ancestor"
            f"ORDER BY size([(ancestor)<-[:PARENT*0..10]-()|ancestor]) DESC "
            f"LIMIT 1"
        )
        return result,len(result)