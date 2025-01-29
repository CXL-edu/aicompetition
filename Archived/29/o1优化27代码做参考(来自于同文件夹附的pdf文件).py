import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import uuid
import shutil
from threading import Lock
from collections import defaultdict
from typing import Literal
from websocietysimulator.agent import SimulationAgent
from websocietysimulator.llm import LLMBase
from websocietysimulator.agent.modules.planning_modules import PlanningBase 
from websocietysimulator.agent.modules.reasoning_modules import ReasoningBase
from langchain_chroma import Chroma
from langchain.docstore.document import Document


class MemoryBase:
    def __init__(self, memory_type: str, llm) -> None:
        self.llm = llm
        self.embedding = self.llm.get_embedding_model()
        db_path = os.path.join('./db', memory_type, f'{str(uuid.uuid4())}')
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
        self.scenario_memory = Chroma(
            embedding_function=self.embedding,
            persist_directory=db_path
        )

    def __call__(self, current_situation: str = ''):
        if 'review:' in current_situation:
            self.addMemory(current_situation.replace('review:', ''))
        else:
            return self.retriveMemory(current_situation)

    def retriveMemory(self, query_scenario: str):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def addMemory(self, current_situation: str):
        raise NotImplementedError("This method should be implemented by subclasses.")


class MemoryDILU(MemoryBase):
    def __init__(self, llm):
        super().__init__(memory_type='dilu', llm=llm)

    # 新增文本分块辅助函数
    def split_text(self, text, chunk_size=300):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)
        return chunks

    def retriveMemory(self, query_scenario: str, topk=1):
        if self.scenario_memory._collection.count() == 0:
            return ''
        similarity_results = self.scenario_memory.similarity_search_with_score(query_scenario, k=topk)

        task_trajectories = []
        for i, result in enumerate(similarity_results):
            task_trajectories.append(f"{i+1}. {result[0].metadata['task_trajectory']}")
        return '\n'.join(task_trajectories)

    def addMemory(self, current_situation: str):
        # 单条版本
        splitted_texts = self.split_text(current_situation, chunk_size=300)
        for idx, chunk_text in enumerate(splitted_texts):
            memory_doc = Document(
                page_content=chunk_text,
                metadata={
                    "task_name": current_situation[:50],
                    "task_trajectory": f"chunk_id: {idx}, review: {chunk_text}"
                }
            )
            self.scenario_memory.add_documents([memory_doc])

    def addMemories(self, current_situations: list[dict]):
        memory_docs = []
        for current_situation in current_situations:
            star_info = current_situation.get('stars', None)
            full_text = current_situation['text']
            splitted_texts = self.split_text(full_text, chunk_size=300)

            for idx, chunk_text in enumerate(splitted_texts):
                memory_doc = Document(
                    page_content=chunk_text,
                    metadata={
                        "task_name": full_text[:50],
                        "task_trajectory": f"stars: {star_info}, chunk_id: {idx}, review: {chunk_text}"
                    }
                )
                memory_docs.append(memory_doc)
        self.scenario_memory.add_documents(memory_docs)


class PlanningBaseline(PlanningBase):
    def __init__(self, llm):
        super().__init__(llm=llm)
    
    def __call__(self, task_description):
        self.plan = [
            {
                'description': 'First I need to find user information',
                'reasoning instruction': 'None', 
                'tool use instruction': {task_description['user_id']}
            },
            {
                'description': 'Next, I need to find business information',
                'reasoning instruction': 'None',
                'tool use instruction': {task_description['item_id']}
            }
        ]
        return self.plan


class ReasoningBaseline(ReasoningBase):
    def __init__(self, profile_type_prompt, llm):
        super().__init__(profile_type_prompt=profile_type_prompt, memory=None, llm=llm)
        
    def __call__(self, task_description: str):
        # 在 system role 中放入一些指令，有助于结果更稳定
        system_prompt = (
            "You are an experienced Yelp user with consistent rating habits. "
            "Use the provided user profile, item info, historical reviews, and distribution stats. "
            "Your final output must strictly follow the format: \n"
            "stars: <float>\nreview: <text>\n"
            "Only produce these lines at the end, no extra text."
        )
        prompt = task_description
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        reasoning_result = self.llm(
            messages=messages,
            max_tokens=1500,
            temperature=0.5,
            top_p=0.9
        )
        return reasoning_result


class MySimulationAgent(SimulationAgent):
    _interaction_tool_preprocess = False
    _preprocess_lock = Lock()
    
    def __init__(self, llm: LLMBase):
        super().__init__(llm=llm)
        self.planning = PlanningBaseline(llm=self.llm)
        self.reasoning = ReasoningBaseline(profile_type_prompt='', llm=self.llm)
        self.memory = MemoryDILU(llm=self.llm)

    def preprocess_interaction_tool(self):
        print(f"开始预处理，当前类预处理状态: {self.__class__._interaction_tool_preprocess}")

        def transform_book_shelves(data):
            result_dict = defaultdict(list)
            for item in data:
                result_dict[item["count"]].append(item["name"])
            result = [{"count": count, "names": names} for count, names in sorted(result_dict.items(), reverse=True)]
            return result

        for user in self.interaction_tool.user_data.values():
            if user['source'] == 'yelp':
                user.pop('friends', None)

        for item in self.interaction_tool.item_data.values():
            if item['source'] == 'amazon':
                item.pop('images', None)
                item.pop('videos', None)
            elif item['source'] == 'goodreads':
                item.pop('link', None)
                item.pop('url', None)
                item.pop('image_url', None)
                shelves_data = item['popular_shelves']
                item['popular_shelves'] = transform_book_shelves(shelves_data)
        
        for review in self.interaction_tool.review_data.values():
            if review['source'] == 'amazon':
                review['text'] = f'Review title: {review["title"]}\nReview content: {review["text"]}'
            review['text'] = re.sub(r'\s+', ' ', review['text'])
        
        self.__class__._interaction_tool_preprocess = True
        print(f'预处理完成，类预处理状态: {self.__class__._interaction_tool_preprocess}')

    def get_statistics_from_reviews(self, reviews: list[dict], source: Literal['user','item'], mode: Literal['text','table']):
        statistics = defaultdict(int)
        for review in reviews:
            statistics[review['stars']] += 1
        
        for i in range(1, 6):
            statistics[float(i)] += 0
        cnt_sum = sum(statistics.values())

        if source == 'item':
            title = "**The review information for the item or business is as follows:**"
        else:
            title = "**Summary of User's Ratings and Reviews:**"
        if mode == 'text':
            infos = [title]
            template = "- Rating {i}: Number of reviews is {cnt}, accounting for {percentage}% of total reviews."
            for i in range(1, 6):
                i = float(i)
                infos.append(template.format(i=i, cnt=statistics[i], percentage=f"{statistics[i] / cnt_sum * 100:.2f}"))
            return '\n'.join(infos)
        elif mode == 'table':
            infos = [title, "| Rating | Number of Reviews | Percentage |", "|--------|--------------------|------------|"]
            for i in range(1, 6):
                i = float(i)
                infos.append(f"| {i} | {statistics[i]} | {statistics[i] / cnt_sum * 100:.2f}% |")
            return '\n'.join(infos)

    # 可选：对用户多条评论做简短summarize
    def summarize_reviews(self, reviews: list[dict]) -> str:
        if not reviews:
            return "No historical reviews."
        # 简单拼成大段，再让LLM做1次总结
        all_text = "\n".join([f"stars: {r['stars']}, text: {r['text']}" for r in reviews])
        prompt = f"请对下面用户多条历史评论进行简短总结，突出他的评分倾向与写作风格：\n{all_text}"
        messages = [{"role": "user", "content": prompt}]
        summary = self.llm(messages=messages, max_tokens=500, temperature=0.5)
        return summary

    def workflow(self):
        try:
            with self.__class__._preprocess_lock:
                if not self.__class__._interaction_tool_preprocess:
                    self.preprocess_interaction_tool()
                    print('preprocess_interaction_tool: done')
            plan = self.planning(task_description=self.task)

            # 简单取出 user 和 business 信息
            user_str = ""
            business_str = ""
            for sub_task in plan:
                if 'user' in sub_task['description']:
                    user_str = str(self.interaction_tool.get_user(user_id=self.task['user_id']))
                elif 'business' in sub_task['description']:
                    business_str = str(self.interaction_tool.get_item(item_id=self.task['item_id']))

            # 获取商品、用户历史评论
            reviews_item = self.interaction_tool.get_reviews(item_id=self.task['item_id'])
            reviews_user = self.interaction_tool.get_reviews(user_id=self.task['user_id'])

            # 将Item的所有review加入内存
            self.memory.addMemories(reviews_item)

            # 检索与用户第一条评论相似的Item评价（可改为多条评论后做合并）
            if reviews_user:
                review_similar = self.memory.retriveMemory(reviews_user[0]["text"], topk=3)
            else:
                review_similar = "No user review available."

            # 新开一份Memory，用于用户自身历史评论
            self.memory_user_review = MemoryDILU(llm=self.llm)
            self.memory_user_review.addMemories(reviews_user)
            reviews_user_item = self.memory_user_review.retriveMemory(business_str, topk=3)

            # 统计信息
            item_review_statistics = self.get_statistics_from_reviews(reviews_item, source='item', mode='table')
            user_review_statistics = self.get_statistics_from_reviews(reviews_user, source='user', mode='table')

            # 也可以做个简单的用户历史评论总结
            user_reviews_summary = self.summarize_reviews(reviews_user)

            task_description = f"""**User's historical review summary:**
{user_reviews_summary}

**You are a real human user on Yelp. Here is your Yelp profile and review history:**
{user_str}

**You need to write a review for this business:**
{business_str}

**Others have reviewed this business before (similar to your style):**
{review_similar}

**Your comments on similar business:**
{reviews_user_item}

{item_review_statistics}

{user_review_statistics}

**Please analyze the following aspects carefully:**
1. Based on your user profile and review style, what rating would you give this business? 
2. Given the business details and your past experiences, what specific aspects would you comment on?

**Requirements:**
- Star rating must be one of: 1.0, 2.0, 3.0, 4.0, 5.0
- 2-4 sentences focusing on your personal experience
- Consistent with your historical style and rating distribution
- Format output exactly:
stars: [your rating]
review: [your review text]
"""
            result = self.reasoning(task_description)
            
            try:
                lines = result.split('\n')
                stars_line = next(line for line in lines if 'stars:' in line)
                review_line = next(line for line in lines if 'review:' in line)
            except:
                print('Error:', result)
                return {"stars": 0, "review": ""}

            stars = float(stars_line.split(':', 1)[1].strip())
            review_text = review_line.split(':', 1)[1].strip()
            if len(review_text) > 512:
                review_text = review_text[:512]
                
            return {
                "stars": stars,
                "review": review_text
            }
        except Exception as e:
            print(f"Error in workflow: {e}")
            return {
                "stars": 0,
                "review": ""
            }
