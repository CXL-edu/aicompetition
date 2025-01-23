import sys  
import os  
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  
import time
import json
from typing import Literal
from collections import defaultdict
from threading import Lock
from websocietysimulator.agent import SimulationAgent
from websocietysimulator.llm import LLMBase
from websocietysimulator.agent.modules.planning_modules import PlanningBase 
from websocietysimulator.agent.modules.reasoning_modules import ReasoningBase
from websocietysimulator.agent.modules.memory_modules import MemoryBase
from langchain.docstore.document import Document


class MemoryDILU(MemoryBase):
    def __init__(self, llm):
        super().__init__(memory_type='dilu', llm=llm)

    def retriveMemory(self, query_scenario: str, topk=1):
        task_name = query_scenario
        if self.scenario_memory._collection.count() == 0:
            return ''
            
        similarity_results = self.scenario_memory.similarity_search_with_score(task_name, k=topk)
            
        task_trajectories = []
        if topk == 1:
            task_trajectories.append(similarity_results[0][0].metadata['task_trajectory'])
        else:
            for i, result in enumerate(similarity_results):
                task_trajectories.append(f"{i+1}. {result[0].metadata['task_trajectory']}")
        
        return '\n'.join(task_trajectories)

    def addMemory(self, current_situation: str):
        task_name = current_situation
        
        memory_doc = Document(
            page_content=task_name,
            metadata={
                "task_name": task_name,
                "task_trajectory": current_situation
            }
        )
        
        self.scenario_memory.add_documents([memory_doc])

    def addMemories(self, current_situations: list[dict]):
        memory_docs = []
        for current_situation in current_situations:
            task_name = current_situation['text']
            memory_doc = Document(
                page_content=task_name,
                metadata={
                    "task_name": task_name,
                    "task_trajectory": f"stars: {current_situation['stars']}, review: {current_situation['text']}"
                }
            )
            memory_docs.append(memory_doc)
        
        self.scenario_memory.add_documents(memory_docs)


class PlanningBaseline(PlanningBase):
    """Inherit from PlanningBase"""
    
    def __init__(self, llm):
        """Initialize the planning module"""
        super().__init__(llm=llm)
    
    def __call__(self, task_description):
        """Override the parent class's __call__ method"""
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
    """Inherit from ReasoningBase"""
    
    def __init__(self, profile_type_prompt, llm):
        """Initialize the reasoning module"""
        super().__init__(profile_type_prompt=profile_type_prompt, memory=None, llm=llm)
        
    def __call__(self, task_description: str):
        """Override the parent class's __call__ method"""
        prompt = '''
{task_description}'''
        prompt = prompt.format(task_description=task_description)
        
        messages = [{"role": "user", "content": prompt}]
        reasoning_result = self.llm(
            messages=messages,
            max_tokens=2000
        )
        
        return reasoning_result


class MySimulationAgent(SimulationAgent):
    """Participant's implementation of SimulationAgent."""
    _interaction_tool_preprocess = False
    _preprocess_lock = Lock()
    
    def __init__(self, llm: LLMBase):
        """Initialize MySimulationAgent"""
        super().__init__(llm=llm)
        self.planning = PlanningBaseline(llm=self.llm)
        self.reasoning = ReasoningBaseline(profile_type_prompt='', llm=self.llm)
        self.memory = MemoryDILU(llm=self.llm)

    def preprocess_interaction_tool(self):
        print(f"开始预处理，当前类预处理状态: {self.__class__._interaction_tool_preprocess}")
        def transform_book_shelves(data):
            from collections import defaultdict
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
                review['text'] = f'Review title: {review["title"]}, Review content: {review["text"]}'
        
        self.__class__._interaction_tool_preprocess = True
        print(f'预处理完成，类预处理状态: {self.__class__._interaction_tool_preprocess}')
        

    def get_statistics_from_reviews(self, reviews:list[dict], source:Literal['user', 'item'], mode:Literal['text', 'table']):
        statistics = defaultdict(int)
        for review in reviews:
            statistics[review['stars']] += 1
        
        for i in range(1, 6):
            statistics[float(i)] += 0
        cnt_sum = sum(statistics.values())

        if source == 'item':
            title = "**The review information for the item or business is as follows:**"    # Summary of Product Ratings and Reviews
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


    def workflow(self):
        """
        Simulate user behavior
        Returns:
            tuple: (star (float), useful (float), funny (float), cool (float), review_text (str))
        """
        try:
            # print(f"workflow开始，类预处理状态: {self.__class__._interaction_tool_preprocess}")
            with self.__class__._preprocess_lock:
                if not self.__class__._interaction_tool_preprocess:
                    self.preprocess_interaction_tool()
                    print('preprocess_interaction_tool: done')
            for val in self.interaction_tool.user_data.values():
                if 'friends' in val: del val['friends']
            plan = self.planning(task_description=self.task)

            for sub_task in plan:
                if 'user' in sub_task['description']:
                    user = str(self.interaction_tool.get_user(user_id=self.task['user_id']))
                elif 'business' in sub_task['description']:
                    business = str(self.interaction_tool.get_item(item_id=self.task['item_id']))
            reviews_item = self.interaction_tool.get_reviews(item_id=self.task['item_id'])
            # for review in reviews_item:
            #     review_text = review['text']
            #     self.memory(f'review: {review_text}')
            reviews_user = self.interaction_tool.get_reviews(user_id=self.task['user_id'])
            # review_similar = self.memory(f'{reviews_user[0]["text"]}')
            # review_similar = '\n'.join([f"stars: {review['stars']}, review: {review['text']}" for review in reviews_user])
            k = min(1, len(reviews_item))
            review_similar = '\n'.join([f"{i+1}. {review['text']}" for i, review in enumerate(reviews_item[:k])])

            # self.memory_user_review = MemoryDILU(llm=self.llm)
            # # for review in reviews_user:
            # #     self.memory_user_review(f'review:{review["text"]}')
            # self.memory_user_review.addMemories(reviews_user)
            # reviews_user_item = self.memory_user_review(f'{business}')

            # 在workflow中
            item_review_statistics = self.get_statistics_from_reviews(reviews_item, source='item', mode='table')
            user_review_statistics = self.get_statistics_from_reviews(reviews_user, source='user', mode='table')
            print(f"len(item_review_statistics): {len(item_review_statistics)}, len(user_review_statistics): {len(user_review_statistics)}")

            task_description = \
f'''**You are a real human user on Yelp, a platform for crowd-sourced business reviews. Here is your Yelp profile and review history:**
{user}

**You need to write a review for this business:**
{business}

**Others have reviewed this business before:**
{review_similar}

{item_review_statistics}

{user_review_statistics}

**Please analyze the following aspects carefully:**
1. Based on your user profile and review style, what rating would you give this business? Remember that many users give 5-star ratings for excellent experiences that exceed expectations, and 1-star ratings for very poor experiences that fail to meet basic standards.
2. Given the business details and your past experiences, what specific aspects would you comment on? Focus on the positive aspects that make this business stand out or negative aspects that severely impact the experience.

**Requirements:**
- Star rating must be one of: 1.0, 2.0, 3.0, 4.0, 5.0
- If the business meets or exceeds expectations in key areas, consider giving a 5-star rating
- If the business fails significantly in key areas, consider giving a 1-star rating
- Review text should be 2-4 sentences, focusing on your personal experience and emotional response
- Maintain consistency with your historical review style and rating patterns
- Focus on specific details about the business rather than generic comments
- Be generous with ratings when businesses deliver quality service and products
- Be critical when businesses fail to meet basic standards

**Format your response exactly as follows:**
stars: [your rating]
review: [your review]'''
            result = self.reasoning(task_description)
            time.sleep(30)
            
            try:
                stars_line = [line for line in result.split('\n') if 'stars:' in line][0]
                review_line = [line for line in result.split('\n') if 'review:' in line][0]
            except:
                print('Error:', result)

            stars = float(stars_line.split(':')[1].strip())
            review_text = review_line.split(':')[1].strip()

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
            