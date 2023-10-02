from config.chatgpt_config import config_dict
from src.openai_request import OpenAI_Request
import time
from tools.cfg_wrapper import load_config
from tools.context import ContextHandler
from tools.tokennizer import Tokennizer
from tools.get_masks import get_box_list

template = '''Now you are an assistant to help me design a layout given a verse. Concretely, a layout denotes a directory containing sets of "object: bounding box" items. "object" means the object name in the scene that the verse describes, while "bounding box" is formulated as [x, y, w, h], where "x, y" denotes the top left coordinate of the bounding box, "w" denotes the width, and "h" denotes the height. The six values "x, y, w, h, x+w, y+h" are all larger than 0 and smaller than 1. Next, I will give you several examples for you to understand this task.

Input: Green hills and clear waters, a wonderful fate begins,
Output:
{“hills”: [0.1, 0.2, 0.4, 0.3],
“waters”: [0.1, 0.5, 0.6, 0.4]}

Input: Distant mountains faintly visible by the lake shore.
Output:
{“mountains”: [0.3, 0.2, 0.4, 0.6],
“lake”: [0.1, 0.5, 0.7, 0.3]}

Input: '''

def get_response(keys, model_name, request_address, input_s, context_handler, tokenizer, log_time=False, context_max=3200):
    context_handler.clear()
    
    input_s = template + input_s + "\nJust give me the Ouput, don't mention others."
    
    requestor = OpenAI_Request(keys, model_name, request_address)
    inputs_length = tokenizer.num_tokens_from_string(input_s)
    context_handler.append_cur_to_context(input_s,inputs_length)

    st_time = time.time()

    res = requestor.post_request(context_handler.context)
    ed_time = time.time()

    if res.status_code == 200:
        response = res.json()['choices'][0]['message']['content']
        # cut \n for show
        response = response.lstrip("\n")

        completion_length = res.json()['usage']['completion_tokens']
        total_length = res.json()['usage']['total_tokens']
        print(f"\nresponse : {response}")

        context_handler.append_cur_to_context(response,completion_length,tag=1)
        if total_length > context_max:
            context_handler.cut_context(total_length,tokenizer)

    else:
        status_code = res.status_code
        reason = res.reason
        des = res.text
        raise print(f'visit error :\n status code: {status_code}\n reason: {reason}\n err description: {des}\n '
                    f'please check whether your account  can access OpenAI API normally')
    
    if log_time:
        print(f'time cost : {ed_time - st_time}')
    
    return response


if __name__ == '__main__':

    # load config
    config = load_config(config_dict)
    keys = config.Acess_config.authorization
    model_name = config.Model_config.model_name
    request_address = config.Model_config.request_address

    # load context
    context_manage_config = config.Context_manage_config
    del_config = context_manage_config.del_config
    max_context = context_manage_config.max_context
    context = ContextHandler(max_context=max_context,context_del_config=del_config)

    # load tokenizer
    tokenizer = Tokennizer(model_name)

    # for test
    input_list = [
        "Lifting eyes to the sky, clouds are a light red,",
        "At the ridge's top, autumn water ripples in the wind.",
        "The setting sun's afterglow illuminates the forest's shadows,",
        "In the boat, the sage quietly contemplates the void."
    ]

    output_list = []
    for input_s in input_list:
        response = get_response(keys, model_name, request_address,input_s, context, tokenizer)
        output_list.append(response)

    element_list = get_box_list(output_list, './mask', height=512, width=512*len(output_list))
    