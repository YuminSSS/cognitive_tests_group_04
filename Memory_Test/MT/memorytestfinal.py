#!/usr/bin/env python
# coding: utf-8

# In[1]:


from IPython.display import display, HTML, Image
from IPython.display import display, Image, clear_output
import time
import random
random.seed(1)
import ipywidgets as widgets
from jupyter_ui_poll import ui_events
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import matplotlib.pyplot as plt


# In[2]:


#### Functions that will be re-used several times in the test
def check_time_up(start_time, limit=180):
    return (time.time() - start_time) >= limit

def show_prompt(text, sleep_time = 2, is_clear = True):
    display(HTML(text))
    time.sleep(sleep_time)

    if is_clear:
        clear_output(wait=False)

def show_image(img_name, sleep_time = 5, is_clear = True):
    img =Image(img_name, width=400)
    display(img)
    time.sleep(sleep_time)
    clear_output(wait=False)

def instruction_display():
    time.sleep(2)
    clear_output(wait=False)


# In[3]:


#### Function displaying a bar showing time progress
def update_progress_bar(current):
    progress = current / 180 * 100
    progress_bar_html = f"""
        <div style="background-color: #ddd; width: 100%; height: 30px;">
            <div style="background-color: #4CAF50; width: {progress}%; height: 100%;"></div>
        </div>
         <p>time progress: {int(current)}s/180s</p>
    """
    display(HTML(progress_bar_html))


# In[4]:


#### Function for widgets usage
event_info = {
    'type': '',
    'description': '',
    'time': -1
}

def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True):
    start_wait = time.time()

    event_info['type'] = ""
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1

    with ui_events() as ui_poll:
        keep_looping = True
        while keep_looping==True:

            ui_poll(n_proc)

            if (timeout != -1) and (time.time() > start_wait + timeout):
                keep_looping = False

            if allow_interupt==True and event_info['description']!="":
                keep_looping = False

            time.sleep(interval)

    return event_info

def register_btn_event(btn):
    event_info['type'] = "button click"
    event_info['description'] = btn.description
    event_info['time'] = time.time()
    return

def register_text_input_event(text_input):
    event_info['type'] = "text_entry"
    event_info['description'] = text_input.value
    event_info['time'] = time.time()
    return

def text_input(prompt=None):
    text_input = widgets.Text(description=prompt, style= {'description_width': 'initial'})
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    text_input.on_submit(register_text_input_event)
    display(text_input)
    event = wait_for_event(timeout=10)
    text_input.disabled = True
    return event['description']

def create_question_btns(btns_description):
    for desc in btns_description:
      btn1 = widgets.Button(description=desc)
      btn1.on_click(register_btn_event)
      display(btn1)


# In[5]:


##### Functions for data collection
def send_to_google_form(data_dict, form_url):
    ''' Helper function to upload information to a corresponding google form
        You are not expected to follow the code within this function!
    '''
    form_id = form_url[34:90]
    view_form_url = f'https://docs.google.com/forms/d/e/{form_id}/viewform'
    post_form_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse'

    page = requests.get(view_form_url)
    content = BeautifulSoup(page.content, "html.parser").find('script', type='text/javascript')
    content = content.text[27:-1]
    result = json.loads(content)[1][1]
    form_dict = {}

    loaded_all = True
    for item in result:
        if item[1] not in data_dict:
            print(f"Form item {item[1]} not found. Data not uploaded.")
            loaded_all = False
            return False
        form_dict[f'entry.{item[4][0][0]}'] = data_dict[item[1]]

    post_result = requests.post(post_form_url, data=form_dict)
    return post_result.ok


# In[6]:


#### Question bank & answer
level1_dict = {
    1: ["what is the color of the circle?", "green", "orange", "blue", "red", 2],
    2: ["what is the color of the triangle", "yellow", "grey", "blue", "red", 3],
    3: ["whart is the color of the rhombus", "red", "orange", "purple", "yellow", 1],
    4: ["what is above the arrow", "triangle", "heart", "cross", "circle", 4],
    5: ["what is above the cross", "circle", "triangle", "heart", "rhombus", 2],
    6: ["what is next to the heart", "arrow", "heart", "triangle", "cross", 4],
}

level2_dict = {
    1: ["what is the color of the square?", "blue", "yellow", "red", "green", 1],
    2: ["what is the color of the triangle", "green", "black", "red", "purple", 3],
    3: ["what is the color of the rhombus", "red", "green", "grey", "yellow", 1],
    4: ["what is the color of the arrow", "green", "yellow", "red", "blue", 4],
    5: ["what is the color of the cross", "red", "black", "grey", "green", 2],
    6: ["what is below the plus sign", "parallelogram", "triangle", "circle", "heart", 1],
    7: ["what is above the circle", "rhombus", "square", "cross", "plus sign", 1],
    8: ["what is next to the heart", "circle", "triangle", "rhombus", "arrow", 4],
    9: ["what is above parallelogram", "rhombus", "plus sign", "circle", "triangle", 2],
}

level3_dict = {
    1: ["what is the color of circle?", "blue", "black", "orange", "red", 2],
    2: ["what is the color of the sun", "grey", "green", "orange", "red", 3],
    3: ["what is the shape inside the cross", "triangle", "heart", "sun", "star", 1],
    4: ["what is the shape inside the hexagon", "circle", "arrow", "parallelogram", "lightning", 4],
    5: ["what is the color of the star", "red", "grey", "yellow", "green", 2],
    6: ["waht is the color of the rectangle", "yellow", "blue", "green", "red", 1],
    7: ["what is inside the rhombus", "smile", "arrow", "circle", "hexagon", 1],
    8: ["what is the color of the parallelogram", "black", "white", "green", "red", 4],
    9: ["what is the color of the trapezium", "white", "red", "black", "orange", 3],
}


# In[7]:


def run_full_test():
    #### Default setting 
    GAME_DURATION = 180
    questions_level = [level1_dict, level2_dict, level3_dict]
    levels_image = ["memory_test_level1.png", "memory_test_level2.png", "memory_test_level3.png"]
    scores = []
    levels = []
    
    quiz_num_level = [3, 3, 4]
    user_info = {}
    questions_time = []
    level = 0
    
    ##### Data collection
    #### User coming up with an unique ID
    id_instructions = """
    
    Enter your anonymised ID
    
    To generate an anonymous 4-letter unique user identifier please enter:
    - two letters based on the initials (first and last name) of a childhood friend
    - two letters based on the initials (first and last name) of a favourite actor / actress
    
    e.g. if your friend was called Charlie Brown and film star was Tom Cruise
         then your unique identifier would be CBTC
    """    
    print(id_instructions)
    
    while True:
        user_input = input("> ")
        if len(user_input) == 4 and user_input.isalpha():
            user_id = user_input
            break
        else:
            print("Please ensure that your ID is four letters long and contains only alphabetic characters.")

    user_info = {}
    user_info['name'] = user_id
    
    instruction_display()
    
    #### User clarifying his age
    while True:
        age_str = input('Enter your age: ')
    
        if not age_str.isdigit():
            print("Age must be a numerical value. Please try again.")
            continue
        
        age = int(age_str)
        
        if 0 <= age <= 100:
            user_info['age'] = age
            break
        else:
            print("Age must be between 0 and 100. Please try again.")
    
    instruction_display()
    
    print("Gender:")
    btns_desc = ["Male", "Female", "Prefer not to say"]
    
    create_question_btns(btns_desc)
    event_info = wait_for_event()
    user_info['sex'] = event_info['description']
    
    instruction_display()
    
    print("Ethnicity:")
    btns_desc = ["White", "Black or African American", "Asian", "Other", "Rather not say" ]
    
    create_question_btns(btns_desc)
    event_info = wait_for_event()
    user_info['ethnicity'] = event_info['description']
    
    instruction_display()
    
    print("Did you have breakfast today:")
    btns_desc = ["Yes", "No", "Rather no to say"]
    
    create_question_btns(btns_desc)
    event_info = wait_for_event()
    user_info['breakfast'] = event_info['description']
    
    instruction_display()
    
    print("How long did you sleep last night:")
    btns_desc = ["less than 5 hours", "5-9 hours", "More than 9 hours", "Rather not say" ]
    
    create_question_btns(btns_desc)
    event_info = wait_for_event()
    user_info['sleep'] = event_info['description']
    
    clear_output(wait=False)

    #### Welcome message& game introduction    
    s = """
    <h1><center>  Welcome to memory test, 
    if the elapsed time exceeds <strong style="color: red;">three minutes</strong>, the game will end automatically.
    answer as much question as you can  </center></h1><br>
    """
    show_prompt(s, 2, True)
    
    s = """
    <h2><center>Quiz Rule: 
    check if you could remember the shape, or color, or other patterns </center></h2><br>
    """
    show_prompt(s, 2, True)
    
    btn1 = widgets.Button(description="Start", button_style = 'info')
    btn1.on_click(register_btn_event)
    display(btn1)
    wait_for_event()
    
    beginning_time=time.time()

    #### The actual game
    while level < 3:
        ques_index =list(questions_level[level].keys())
        random.shuffle(ques_index)
    
        s = "<h1><center>Level " + str(level + 1) + " starts!</center></h1><br>"
        show_prompt(s, 2, True)
    
        s = """
        <h2><center>Observe the following grid and answer questions. 
        Attention: it will disappear within <strong style="color: red;">30 seconds</strong>.</center></h2><be>
        """
        show_prompt(s, 2, False)
    
        show_image(levels_image[level],30 , True)
    
        questions = questions_level[level]
        score = 0

        #### Loop running through each individual question under each level
        for i in range(quiz_num_level[level]):
            
            progress=time.time()-beginning_time
            update_progress_bar(progress)
            
            info = questions[ques_index[i]]
            query = info[0]
            answers = info[1:5]
            cor_answer = info[info[5]]
    
            print("")
            show_prompt(query, 1, False)
            start_time = time.time()
    
            create_question_btns(answers)
            event_info = wait_for_event()
            user_answer = event_info['description']
            
            if user_answer ==cor_answer:
                show_prompt("<font color='green'>Correct!</font><br>", 1, False)
                scores.append(1)
                level_elapsed_time = time.time() - start_time
                questions_time.append(level_elapsed_time)
            else:
                scores.append(0)
                show_prompt(f"<font color='red'>Oops! The right answer is {cor_answer}.</font><br>", 1, False)
                nd_time = time.time()
                level_elapsed_time = time.time() - start_time
                questions_time.append(level_elapsed_time)
    
            levels.append(level)
            clear_output(wait=False)
    
            if check_time_up(beginning_time, GAME_DURATION):
                s = "<h2><center>Time's up or max number of questions reached. The game is over.</center></h2><br>"
                show_prompt(s, 2, False)
                break
    
        level += 1

    final_score=sum(scores)
    s= "<h1>Game ended. Score:" + str(final_score) + ". Keep on your effort!</h1>"
    show_prompt(s, 2, False)

    
    #### Histogram to show user their ranking
    MT_df = pd.read_csv("MT_df.csv", index_col='name')
    results = MT_df['total_score']
    
    mean_result = np.mean(results)
    median_result = np.median(results)
    std_dev = np.std(results)
    plt.hist(results, bins=10, edgecolor='black')
    plt.axvline(x=mean_result, color='red', linestyle='--', label=f'Mean: {mean_result:.2f}')
    plt.axvline(x=median_result, color='green', linestyle='--', label=f'Median: {median_result:.2f}')
    plt.xlabel('Test Results')
    plt.ylabel('Frequency')
    plt.title('Distribution of Test Results')
    plt.legend()
    plt.annotate('Your Result', xy=(final_score, 1), xytext=(final_score + 5, 3),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.show()

    time.sleep(2)
    clear_output(wait=False)
 
    ##### Giving consent to upload data
    user_ls = [user_info['name']] * 10
    data_frame= pd.DataFrame({"üser_name": user_ls, "score": scores, "time": questions_time, "level": levels })
    
    user_info['total_score'] = str(sum(scores))
    user_info['results_json'] = data_frame.to_json()
    
    data_consent_info = """DATA CONSENT INFORMATION:
    
    Please read:
    
    We wish to record your response data
    to an anonymised public data repository. 
    Your data will be used for educational teaching purposes
    practising data analysis and visualisation.
    
    Please type   yes   in the box below if you consent to the upload."""
    
    print(data_consent_info)
    result = text_input("> ").lower().replace(" ", "")
    
    if result == "yes": 
        print("Thanks for your participation.")
        print("Please contact a.fedorec@ucl.ac.uk")
        print("If you have any questions or concerns")
        print("regarding the stored results.")
        form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSdunA35DCFNjNrz9WEAk-aCBcKoqhMz2YNJIDqX1bdT9NnnEQ/viewform'
        send_to_google_form(user_info, form_url)
    else: 
        raise(Exception("User did not consent to continue test."))
    return






