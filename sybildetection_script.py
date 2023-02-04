# Define imports
from pathlib import Path
import pandas as pd
import seaborn as sns 
import networkx as nx
import asyncio
# import matplotlib.pyplot as plt
# from requests import get
# from matplotlib import pyplot as plt
from datetime import datetime
import time
# import xgboost as xgb
# from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
import math
# import pyvis
from datetime import timedelta
import json
import os
# Import data
path = Path("./briq-merged.json")
# path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'briq.json'))

# data = []
if path.exists():
    data = pd.read_json(path)

data['datetime']=pd.to_datetime(data['time'],unit='s')
#remove rows with null address because its just an artifact
data = data[data.recipient!='0x0000000000000000000000000000000000000000000000000000000000000000']

async def main():
    # Create a node class
    class Node:
        #in a node you have either a sender or recipient
        def __init__(self, contract, name, time, block, hash, value):
            self.contract = contract
            self.name = name
            self.time = time
            self.block = block
            self.hash = hash
            self.value = value

    # Parse the unique # of recipients, total transaction counts, and time diff between first and last transaction
    unique_senders = data['sender'].unique()
    time_diffs = {}
    total_count_transactions = {}
    number_of_unique_recipients = {}
    all_data = {}
    for i in unique_senders:
        sender_times=[]
        count_transactions = 0
        unique_recipients=[]
        for index, row in data.iterrows():
            if row['sender']==i:
                count_transactions+=1
                sender_times.append(row['datetime'])
                unique_recipients.append(row['recipient'])

        #dedupe and sort the times in ascending order
        sender_times = sorted(list(sender_times))
        num_unique_recipients = len(np.unique(unique_recipients))
        max_time = max(sender_times)
        min_time = min(sender_times)
        time_diff = (max_time - min_time).seconds
        all_data[i] = {'time_difference': time_diff,'count_transactions': count_transactions, 'num_unique_recipients': num_unique_recipients}
        time_diffs[i] = time_diff
        total_count_transactions[i] = count_transactions
        number_of_unique_recipients[i] = num_unique_recipients
    # number_of_unique_recipients

    #time difference
    value_key_pairs = ((value, key) for (key,value) in time_diffs.items())
    sorted_value_key_pairs = sorted(value_key_pairs, reverse=True)
    sorted_value_key_pairs

    td = pd.DataFrame(sorted_value_key_pairs, columns=['time_difference', 'sender'])

    #count transactions
    value_key_pairs = ((value, key) for (key,value) in total_count_transactions.items())
    sorted_value_key_pairs = sorted(value_key_pairs, reverse=True)
    sorted_value_key_pairs
    count_transactions = pd.DataFrame(sorted_value_key_pairs, columns=['total_count_transactions', 'sender'])

    value_key_pairs = ((value, key) for (key,value) in number_of_unique_recipients.items())
    sorted_value_key_pairs = sorted(value_key_pairs, reverse=True)
    sorted_value_key_pairs

    # number_of_unique_recipients
    num_unique_recipients = pd.DataFrame(sorted_value_key_pairs, columns=['num_unique_recipients', 'sender'])

    #time diffs standard deviations from the mean 
    std_1 = round(td['time_difference'].mean() + 1 * td['time_difference'].std(),0)
    std_2 = round(td['time_difference'].mean() + 2 * td['time_difference'].std(),0)
    std_3 = round(td['time_difference'].mean() + 3 * td['time_difference'].std(),0)
    std_4 = round(td['time_difference'].mean() + 4 * td['time_difference'].std(),0)

    time_diff_scores = {}
    for index, row in td.iterrows():
        if row['time_difference']<=std_1:
            time_diff_scores[row['sender']]=0
        if row['time_difference']>=std_1 and row['time_difference']<std_2:
            time_diff_scores[row['sender']]=0.5
        if row['time_difference']>=std_2:
            time_diff_scores[row['sender']]=1

    std_1 = round(num_unique_recipients['num_unique_recipients'].mean() + 1 * num_unique_recipients['num_unique_recipients'].std(),0)
    std_2 = round(num_unique_recipients['num_unique_recipients'].mean() + 2 * num_unique_recipients['num_unique_recipients'].std(),0)
    std_3 = round(num_unique_recipients['num_unique_recipients'].mean() + 3 * num_unique_recipients['num_unique_recipients'].std(),0)
    std_4 = round(num_unique_recipients['num_unique_recipients'].mean() + 4 * num_unique_recipients['num_unique_recipients'].std(),0)
    # num unique recipients standard deviations from the mean
    num_unique_recipients_scores = {}
    for index, row in num_unique_recipients.iterrows():
        if row['num_unique_recipients']<=std_1:
            num_unique_recipients_scores[row['sender']]=0
        if row['num_unique_recipients']>=std_1 and row['num_unique_recipients']<std_2:
            num_unique_recipients_scores[row['sender']]=0.5
        if row['num_unique_recipients']>=std_2:
            num_unique_recipients_scores[row['sender']]=1

    # count transactions standard deviations from the mean
    std_1 = round(count_transactions['total_count_transactions'].mean() + 1 * count_transactions['total_count_transactions'].std(),0)
    std_2 = round(count_transactions['total_count_transactions'].mean() + 2 * count_transactions['total_count_transactions'].std(),0)
    std_3 = round(count_transactions['total_count_transactions'].mean() + 3 * count_transactions['total_count_transactions'].std(),0)
    std_4 = round(count_transactions['total_count_transactions'].mean() + 4 * count_transactions['total_count_transactions'].std(),0)

    count_transation_scores = {}
    for index, row in count_transactions.iterrows():
        if row['total_count_transactions']<=std_1:
            count_transation_scores[row['sender']]=0
        if row['total_count_transactions']>=std_1 and row['total_count_transactions']<std_2:
            count_transation_scores[row['sender']]=0.5
        if row['total_count_transactions']>=std_2:
            count_transation_scores[row['sender']]=1

    # get an average score of all of the scores from the above lists
    # lists = [count_transation_scores, num_unique_recipients_scores, time_diff_scores]
    unique_senders = data['sender'].unique()

    sender_scores = {}
    for sender in unique_senders:
        temp_sender_score = 0
        temp_sender_count = 0 
        for k, v in count_transation_scores.items():
            if k==sender:
                temp_sender_count+=1
                temp_sender_score +=v
        for k, v in num_unique_recipients_scores.items():
            if k==sender:
                temp_sender_count+=1
                temp_sender_score +=v
        for k, v in time_diff_scores.items():
            if k==sender:
                temp_sender_count+=1
                temp_sender_score +=v
        total_score = temp_sender_score / temp_sender_count
        sender_scores[sender]=total_score


    # redundant code below could just do sender_scores.get(address, 0)
    #TODO Cleanup code below
    def to_return(data):
        G = nx.from_pandas_edgelist(data, source = 'sender', target = 'recipient', edge_attr=True)
        all_scores = {}
        addresses_added = []
        for row, score in sender_scores.items():
            all_scores[row]=score
            addresses_added.append(row)

        for address in G.nodes:
            if address not in addresses_added:
            #if there isnt the score in the sender_scores then set to 0 
                all_scores[address]=0
                addresses_added.append(address)
                    
        nodes = [
            {'id': address, 'name': address, 'val': 1, 'score': all_scores.get(address,0)}
            if int(address, 16) != 0 else
            {'id': address, 'name': address, 'val': 5, 'score': 0}
            for address in all_scores
        ]

        links = [
            {'source': s, 'target': r}
            for s, r in zip(data.sender, data.recipient)
        ]

        #sum integer of source and target 
        unique_links = list({
            int(link['source'], 16) + int(link['target'], 16): link
            for link in links
        }.values())
        return {'nodes': nodes, 'links': unique_links}
    to_return(data)
if __name__ == "__main__":
    asyncio.run(main())


