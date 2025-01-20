from websocietysimulator import Simulator
from websocietysimulator.agent import SimulationAgent
import json 
from websocietysimulator.llm import LLMBase
from websocietysimulator.agent.modules.planning_modules import PlanningBase 
from websocietysimulator.agent.modules.reasoning_modules import ReasoningBase
from websocietysimulator.agent.modules.memory_modules import MemoryBase
from websocietysimulator.simulator import logger

class MemoryDILU(MemoryBase):
    def __init__(self, llm):
        super().__init__(memory_type='dilu', llm=llm)

    def retriveMemory(self, query_scenario: str):
        task_name = query_scenario

        if self.scenario_memory._collection.count() == 0:
            return ''
            
        similarity_results = self.scenario_memory.similarity_search_with_score(task_name, k=1)
        task_trajectories = [
            result[0].metadata['task_trajectory'] for result in similarity_results
        ]
        
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

    def reinit_memory(self) -> None:
        """ reinitialize the memory"""
        try:
            self.scenario_memory.delete_collection()
            db_path = self.scenario_memory._persist_directory
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            self.scenario_memory = Chroma(
                embedding_function=self.embedding,
                persist_directory=db_path
            )
        except Exception as e:
            raise Exception(f"Failed to clear memory: {str(e)}")


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
            temperature=0.0,
            max_tokens=1000
        )
        
        return reasoning_result


class MySimulationAgent(SimulationAgent):
    """Participant's implementation of SimulationAgent."""
    
    def __init__(self, llm: LLMBase):
        """Initialize MySimulationAgent"""
        super().__init__(llm=llm)
        self.planning = PlanningBaseline(llm=self.llm)
        self.reasoning = ReasoningBaseline(profile_type_prompt='', llm=self.llm)
        self.memory = MemoryDILU(llm=self.llm)
        self.memory_user_review = MemoryDILU(llm=self.llm)
        self.interaction_tool_preprocess = False

    def preprocess_interaction_tool(self):
        def transform_book_shelves(data):
            from collections import defaultdict
            result_dict = defaultdict(list)
            for item in data:
                result_dict[item["count"]].append(item["name"])
            result = [{"count": count, "names": names} for count, names in sorted(result_dict.items(), reverse=True)]
            return result

        for user in self.interaction_tool.user_data.values():
            if user['source'] == 'yelp':
                del user['friends']

        for item in self.interaction_tool.item_data.values():
            if item['source'] == 'amazon':
                del item['images'], item['videos']
            elif item['source'] == 'goodreads':
                del item['link'], item['url'], item['image_url']
                item['book_shelves'] = transform_book_shelves(item['book_shelves'])
        
        for review in self.interaction_tool.review_data.values():
            if review['source'] == 'amazon':
                review['text'] = f'Review title: {review["title"]}\nReview content: {review["text"]}'
        self.interaction_tool_preprocess = True
        print('preprocess_interaction_tool: donedonedone')
        
        
    def workflow(self):
        """
        Simulate user behavior
        Returns:
            tuple: (star (float), useful (float), funny (float), cool (float), review_text (str))
        """
        # try:
        logger.info("开始workflow")
        print("开始workflow")
        print(f"self.interaction_tool_preprocess: {self.interaction_tool_preprocess}")
        if not self.interaction_tool_preprocess:
            self.preprocess_interaction_tool()
            print('preprocess_interaction_tool: done')
        
        plan = self.planning(task_description=self.task)

        for sub_task in plan:
            if 'user' in sub_task['description']:
                user = str(self.interaction_tool.get_user(user_id=self.task['user_id']))
            elif 'business' in sub_task['description']:
                business = str(self.interaction_tool.get_item(item_id=self.task['item_id']))
        reviews_item = self.interaction_tool.get_reviews(item_id=self.task['item_id'])
        for review in reviews_item:
            review_text = review['text']
            self.memory(f'review: {review_text}')
        reviews_user = self.interaction_tool.get_reviews(user_id=self.task['user_id'])
        review_similar = self.memory(f'{reviews_user[0]["text"]}')

        self.memory_user_review.reinit_memory()
        for review in reviews_user:
            self.memory_user_review(f'review:{review["text"]}')
        reviews_user_item = self.memory_user_review(f'{business}')

        task_description = f'''
        You are a real human user on Yelp, a platform for crowd-sourced business reviews. Here is your Yelp profile and review history: {user}

        You need to write a review for this business: {business}

        Others have reviewed this business before: {review_similar}

        Your comments on similar business: {reviews_user_item}

        Please analyze the following aspects carefully:
        1. Based on your user profile and review style, what rating would you give this business? Remember that many users give 5-star ratings for excellent experiences that exceed expectations, and 1-star ratings for very poor experiences that fail to meet basic standards.
        2. Given the business details and your past experiences, what specific aspects would you comment on? Focus on the positive aspects that make this business stand out or negative aspects that severely impact the experience.
        3. Consider how other users might engage with your review in terms of:
        - Useful: How informative and helpful is your review?
        - Funny: Does your review have any humorous or entertaining elements?
        - Cool: Is your review particularly insightful or praiseworthy?

        Requirements:
        - Star rating must be one of: 1.0, 2.0, 3.0, 4.0, 5.0
        - If the business meets or exceeds expectations in key areas, consider giving a 5-star rating
        - If the business fails significantly in key areas, consider giving a 1-star rating
        - Review text should be 2-4 sentences, focusing on your personal experience and emotional response
        - Useful/funny/cool counts should be non-negative integers that reflect likely user engagement
        - Maintain consistency with your historical review style and rating patterns
        - Focus on specific details about the business rather than generic comments
        - Be generous with ratings when businesses deliver quality service and products
        - Be critical when businesses fail to meet basic standards

        Format your response exactly as follows:
        stars: [your rating]
        review: [your review]
        '''
        result = self.reasoning(task_description)
        
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
        # except Exception as e:
        #     print(f"Error in workflow: {e}")
        #     return {
        #         "stars": 0,
        #         "review": ""
        #     }

if __name__ == "__main__":
    # poetry run python -m example.ModelingAgent_baseline
    # Set the data
    task_set = "amazon" # "goodreads" or "yelp"
    simulator = Simulator(data_dir="demo_dataset", device="gpu", cache=False)
    # simulator = Simulator(data_dir="dataset", device="gpu", cache=False)
    simulator.set_task_and_groundtruth(task_dir=f"example/track1/{task_set}/tasks", groundtruth_dir=f"example/track1/{task_set}/groundtruth")

    # Set the agent and LLM
    simulator.set_agent(MySimulationAgent)
    simulator.set_llm(InfinigenceLLM(api_key="sk-damtsffnbbpo3bbo"))

    # Run the simulation
    # If you don't set the number of tasks, the simulator will run all tasks.
    number_of_tasks = 10    # None
    outputs = simulator.run_simulation(number_of_tasks=number_of_tasks, enable_threading=True, max_workers=4)
    
    # Evaluate the agent
    evaluation_results = simulator.evaluate()       
    with open(f'./evaluation_results_track1_{task_set}.json', 'w') as f:
        json.dump(evaluation_results, f, indent=4)

    # Get evaluation history
    evaluation_history = simulator.get_evaluation_history()
    