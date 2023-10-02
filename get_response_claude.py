# coding=utf-8

import requests
import json
import time
import pandas as pd
from slack_sdk import WebClient
from tools.get_masks import get_box_list

token = ''
channel = "" 
claude_id = ''
tsss = ''

client = WebClient(token=token)

template = '''Now you are an assistant to help me design a layout given a verse. Concretely, a layout denotes a directory containing sets of "object: bounding box" items. "object" means the object name in the scene that the verse describes, while "bounding box" is formulated as [x, y, w, h], where "x, y" denotes the top left coordinate of the bounding box, "w" denotes the width, and "h" denotes the height. The six values "x, y, w, h, x+w, y+h" are all larger than 0 and smaller than 1. Next, I will give you several examples for you to understand this task.

Input: Green hills and clear waters, a wonderful fate begins,
Output:
{"hills": [0.1, 0.2, 0.4, 0.3],
"waters": [0.1, 0.5, 0.6, 0.4]}

Input: Distant mountains faintly visible by the lake shore.
Output:
{"mountains": [0.3, 0.2, 0.4, 0.6],
"lake": [0.1, 0.5, 0.7, 0.3]}

Input: '''

def get_claude_response(prompt):
    input_prompt = f"<@{claude_id}> " + template + prompt + "\nJust give me the Ouput, don't mention others."
    client.chat_postMessage(channel=channel, text=input_prompt, as_user=True)

    result = client.chat_postMessage(channel=channel, text=input_prompt, as_user=True)
    print(result['ts'])
    all_messages = []

    while True:
        time.sleep(1) 

        latest_res = client.conversations_replies(channel=channel, ts=result['ts'], oldest=tsss)
        messages = latest_res['messages']
        all_messages.extend(messages)

        for message in all_messages:
            if message['user'] == claude_id and message['text'].strip().endswith('_Typing…_'):
                continue
            if message['user'] == claude_id:
                response = message['text']
                print(response)
                return response

def get_mask_results(input_list, output_mask_dir, height=512, width=2048):
    output_list = []
    for input_s in input_list:
        response = get_claude_response(input_s)
        output_list.append(response)

    element_list = get_box_list(output_list, output_mask_dir, height=height, width=width)

    return element_list

if __name__ == '__main__':
    input_list = [
        "Lifting eyes to the sky, clouds are a light red,",
        "At the ridge's top, autumn water ripples in the wind.",
        "The setting sun's afterglow illuminates the forest's shadows,",
        "In the boat, the sage quietly contemplates the void."
    ]

    element_list = get_mask_results(input_list, './mask', 512, 2048)