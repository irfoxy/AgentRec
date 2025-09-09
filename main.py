from model.agent import Agent
import pandas as pd
import random

PLANNER_MODEL = "gpt-4o"
EXEC_MODEL = "gpt-4o"
MEMOEY_MODEL = "gpt-4o"
MEMORY_PATH = "../memory/all_memory.jsonl"
DATA_PATH="../data/ml100k/"

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

    return candidate_dict,user_dict,item_dict

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

    candidate_dict,user_dict,item_dict=load_data()

    