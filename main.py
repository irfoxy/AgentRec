from model.agent import Agent
import pandas as pd
import random

PLANNER_MODEL = "gpt-4o"
EXEC_MODEL = "gpt-4o"
MEMOEY_MODEL = "gpt-4o"
MEMORY_PATH = "../memory/all_memory.jsonl"
DATA_PATH="../data/ml100k/"

USER_AGENT_PROMPT="""
You are a UserAgent whose task is to accurately simulate a user's decision-making behavior. 
You will receive the following information:
(1) a description of the user's memory,
(2) previously simulated history and feedback, and 
(3) a new item description. Based on this information,
Your task is to predict the user's behavior toward the item. 
The possible behaviors are only: accept or reject. 
Before responding, carefully reason through the decision.
Your final output must strictly follow the JSON format below:
{
  "act": BOOL,
  "explain": "STRING"
}
Here, act is a boolean indicating the user's behavior (true = accept, false = reject), and explain is a string providing the reasoning and justification for the chosen behavior.
"""

ITEM_AGENT_PROMPT="""

"""

REC_AGENT_PROMPT="""

"""

def load_data():
    candidate_df=pd.read_csv(DATA_PATH+'dataset/candidate.csv')
    user_df=pd.read_csv(DATA_PATH+'processed/user.csv')
    item_df=pd.read_csv(DATA_PATH+'processed/item.csv')

    candidate_dict={
        row.user_id:{
            "candidate":random.sample(row.candidate.split(' '),len(row.candidate.split(' '))),
            "ground_truth":row.ground_truth
        }
        for row in candidate_df.itertuples()
    }

    user_dict = {
        row.user_id: {
            "gender": row.gender,
            "age": row.age,
            "occupation": row.occupation
        }
        for row in user_df.itertuples()
    }  

    item_dict = {
        row.item_id:row.metadata
        for row in item_df.itertuples()
    }

    train_df=pd.read_csv(DATA_PATH+'dataset/train.csv')

    return candidate_dict,user_dict,item_dict,train_df

def train_user_agent(user_agent,train_data,user_dict,item_dict):
    def build_query_prompt(item_metadata):
        prompt=(
            ""
        )
    sample_lst=train_data.sample
    label_lst=train_data.label_lst
    for i in range(len(sample_lst)):
        sample=sample_lst[i]
        label=label_lst[i]


if __name__ == "__main__":
    user_agent = Agent(
        planner_model=PLANNER_MODEL,
        exec_model=EXEC_MODEL,
        memory_model=MEMOEY_MODEL,
        role="user_agent",
        memory_path=MEMORY_PATH,
    )

    item_agent = Agent(
        planner_model=PLANNER_MODEL,
        exec_model=EXEC_MODEL,
        memory_model=MEMOEY_MODEL,
        role="item_agent",
        memory_path=MEMORY_PATH,
    )

    rec_agent = Agent(
        planner_model=PLANNER_MODEL,
        exec_model=EXEC_MODEL,
        memory_model=MEMOEY_MODEL,
        role="rec_agent",
        memory_path=MEMORY_PATH,
    )

    candidate_dict,user_dict,item_dict,train_df=load_data()
    

