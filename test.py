import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.errors import SlackClientError

client = WebClient(token="xoxp-的那个token")

claude_id = "U058A16GFC5"

channel_id = 'C059CJAMWBH'

tsss = '1686232870.084249'



def send_message(text):

    message_text = f"<@{claude_id}> {text}" # 艾特机器人ID的一个操作text是要输入的文字

    result = client.chat_update(channel=channel_id, text=message_text,ts= tsss) # 发送给机器人 channel_id 是频道ID 发送信息给机器人

    print(result['ts']) # 我们打印一下ts 它其实是一个时间戳，我们可以利用时间戳来制作更深层次的对话，比如上下文的对话

    # ts就是一个时间戳，它代表的就是本次的对话，可以根据时间戳来写一个上下文的对话，在同一个消息列中进行收发消息

    # 记录响应开始时间,重试次数

    all_messages = [] # message 的 列表存储



    while True: # 我们的这个整个循环是为了等待机器人回复完毕，而这个等待的参数是以Typing…_这个结尾进行判断是否完成的。

        time.sleep(5) # 等待五秒机器人回复

        latest_res = client.conversations_replies(channel=channel_id, ts=result['ts'],oldest=tsss)

        messages = latest_res['messages']

        print(messages)

        all_messages.extend(messages) # 追加新的消息

    # 如果响应以_Typing…_结尾，则继续等待响应

        for message in all_messages:

            if message['user'] == claude_id and message['text'].strip().endswith('_Typing…_'): # 这里是机器人回复是否完成的一个判断

                continue # 如果没完成则继续循环等待，如果完成了，则打印输出！

            if message['user'] == claude_id:

                response = message['text']

            print(response)

            return response





send_message(input('人类：'))