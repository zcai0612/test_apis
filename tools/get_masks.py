import json
from PIL import Image
import numpy as np
import os

# input: the list of LLM output, Eg. {"ridge": [0.2, 0.1, 0.5, 0.2], "autumn water": [0.1, 0.3, 0.7, 0.4]}
def get_box_list(output_list, output_dir, height=512, width=2048):
    num_dict = len(output_list)
    element_list = []
    for i, dict_str in enumerate(output_list):
        dict_str = dict_str.replace('Output:', '').strip()
        dict_str = dict_str.replace('\n', '')
        dict = json.loads(dict_str)
        for key, value in dict.items():
            element_list.append(key)
            image_array = np.zeros((height, width, 3))
            x, y, w, h = value
            x_start = int(x*(width//num_dict) + i*(width//num_dict))
            y_start = int(y*height)
            w_true = int(w*(width//num_dict))
            h_true = int(h*height)
            image_array[y_start:y_start+h_true, x_start:x_start+w_true, :] = [255,255,255]
            Image.fromarray(np.uint8(image_array)).save(os.path.join(output_dir, str(len(element_list)) + '.png'))
    return element_list