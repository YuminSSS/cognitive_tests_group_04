#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import necessary modules and packages for the program
from IPython.display import display, clear_output, HTML
import time
import random
import ipywidgets as widgets
from jupyter_ui_poll import ui_events
import requests
from bs4 import BeautifulSoup
import json 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# In[2]:


# Create event info dictionary to store information about events
event_info = {
    'type': '',           # Type of event ('click' or 'text_entry')
    'description': '',    # Description of the event (button description or text input)
    'time': -1            # Timestamp of the event
}

# This function waits for events and updates the event_info dictionary accordingly
def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True):    
    start_wait = time.time()

    # Set event info to be empty initially
    event_info['type'] = ""
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1

    # Use ui_events to monitor UI events
    with ui_events() as ui_poll:
        keep_looping = True
        while keep_looping==True:
            # process UI events
            ui_poll(n_proc)

            # end loop if we have waited more than the timeout period
            if (timeout != -1) and (time.time() > start_wait + timeout):
                keep_looping = False
                
            # end loop if event has occured
            if allow_interupt==True and event_info['description']!="":
                keep_looping = False
                
            # add pause before looping
            # to check events again
            time.sleep(interval)
    
    # return event description after wait ends
    # will be set to empty string '' if no event occured
    return event_info

# This function registers a click event for buttons
def register_event(btn):
    
    btn.disabled = True

    # Update event_info with click event details
    event_info['type'] = "click"
    event_info['description'] = btn.description
    event_info['time'] = time.time()

    return

# These two functions register a text entry event
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
    event = wait_for_event(timeout=-1)
    text_input.disabled = True
    return event['description']

#this function sends responses to a google form
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


# In[3]:


# update progress bar based on the current progress and total steps
def update_progress_bar(current, total):
    
    # Calculate the percentage progress
    progress = current / total * 100

    # Define HTML for the progress bar
    progress_bar_html = f"""
        <div style="background-color: #ddd; width: 100%; height: 30px;">
            <div style="background-color: #4CAF50; width: {progress}%; height: 100%;"></div>
        </div>
        <p>{current}/{total}</p>
    """

    # Display the HTML content to show the progress bar
    display(HTML(progress_bar_html))


# In[4]:


# Generates a list of equations based on the specified difficulty level
# Returns:
#   - equations: A list of tuples representing equations, where each tuple contains an operator and a number
#                - For example, ('+', 5) represents addition of 5
#                - The first element in the list is a starting number
#                - The number of parts generated is proportional to the difficulty level
#                  (2 parts for level 1, 3 for level 2, and 4 for level 3)
#                - Each equation is displayed as HTML content for visualization, with a delay of 2 seconds between each equation
# Notes:
#   - All numbers are randomly generated within specified ranges for each difficulty level

def generate_equations(difficulty):

    # Define operators for equations
    operator = ['+', '-']

    # Initialize list to store equations
    equations = []

    # Generate starting number based on difficulty level
    if difficulty == 1:
        starting_num = random.randint(0, 9)  # For level 1, single digit numbers
    elif difficulty == 2:
        starting_num = random.randint(10, 49)  # For level 2, numbers ranging from 10 to 49
    elif difficulty == 3:
        starting_num = random.randint(50, 99)  # For level 3, numbers ranging from 50 to 99
    equations.append(starting_num)

    # Display starting number as HTML content
    html_out_startnum = HTML(f"""<h1>{starting_num}</h1>""")
    display(html_out_startnum)

    # Delay for 2 seconds before clearing output
    time.sleep(2)
    clear_output(wait=False)

    # Generate additional parts of equations based on difficulty level
    for _ in range(1 * difficulty):
        sign = random.choice(operator)
        if difficulty == 1:
            number = random.randint(0, 9)  # For level 1, single digit numbers
        elif difficulty == 2:
            number = random.randint(10, 49)  # For level 2, numbers ranging from 10 to 49
        elif difficulty == 3:
            number = random.randint(50, 99)  # For level 3, numbers ranging from 50 to 99
        equations.append((sign, number))

        # Display equation part as HTML content
        html_out_signnum = HTML(f"""<h1>{sign}{number}</h1>""")
        display(html_out_signnum)

        # Delay for 2 seconds before clearing output
        time.sleep(2)
        clear_output(wait=False)    
    
    return equations


# In[5]:


# Create buttons
def generate_buttons(descriptions, event_handler):
    
    buttons = []
    
    for desc in descriptions:
        btn = widgets.Button(description=str(desc))
        btn.on_click(event_handler) 
        buttons.append(btn)
        
    return buttons
    


# In[6]:


# Executes a single question with the specified difficulty level
def run_question(difficulty):
    score = 0

    # Generates equations using the generate_equations function and calculates correct answers
    equations = generate_equations(difficulty)
    correct_answers = [equations[0]]
    for sign, number in equations[1:]:
        if sign == '+':
            correct_answers.append(correct_answers[-1] + number)
        elif sign == '-':
            correct_answers.append(correct_answers[-1] - number)
    
    # Generate options for buttons, ensuring the other 2 options does not overlap with the correct_answer
    question_options = [correct_answers[-1]]
    while len(question_options) < 3:
        option = random.randint(correct_answers[-1] - 10, correct_answers[-1] + 10)
        if option != correct_answers[-1] and option not in question_options:
            question_options.append(option)

    question_buttons = generate_buttons(question_options, register_event)

    # Shuffle and display buttons
    random.shuffle(question_buttons)  

    response_start_time = time.time()
    question_panel = widgets.HBox(question_buttons)
    display(question_panel)
    

    # Wait for user click event
    event_info_question = wait_for_event(timeout=5)
    clear_output(wait=False)

    end_time = time.time()
    response_time = end_time - response_start_time

    # Process the event and determines correctness of the answer
    # after each question, returns the score gained and response time for that question
    if event_info_question['description'] != "":
        print(f"User clicked: {event_info_question['description']}")
        if int(event_info_question['description']) == correct_answers[-1]:
            score = difficulty
            print(f"Well done! {score} points gained!")
            time.sleep(1)
        else:
            score = 0
            print("Incorrect, next question!")
            time.sleep(1)
    else:
        print("User did not click in time")
        score = 0
        time.sleep(1)

    print(f"You took {response_time:.2f} seconds")

    time.sleep(1)
    clear_output(wait=False)
    
    # Returns the equations, response time, and score for the question
    return equations, response_time, score


# In[7]:


# Runs test by iterating through 24 iterations
def run_mat(results_dict, total_iterations):
    total_iterations = 24

    total_scores = [0, 0, 0]
    final_scores = [0, 0, 0, 0]

    # Iterates through each question and updates the progress bar
    for i in range(0, total_iterations):
        update_progress_bar(i + 1, total_iterations)

        # Determines the difficulty level for each question
        if i < 8: 
            difficulty = 1
        elif 8 <= i < 16:  
            difficulty = 2
        else:  
            difficulty = 3


        # Runs each question through the run_question function and records the results
        # Calculates the total scores for each difficulty level
        equations, response_time, score = run_question(difficulty)
        total_scores[difficulty - 1] += score
        time.sleep(0.5)

        # Records the results for each question in the results dictionary
        results_dict['equations'].append(str(equations))
        results_dict['difficulty'].append(difficulty)
        results_dict['score'].append(score)
        results_dict['response_time'].append(response_time)

    # Calculates the final scores as percentages for each difficulty level and overall
    for i in range(3):  # Loop through each difficulty level
        final_scores[i] = (total_scores[i] / (8 * (i + 1))) * 100
    final_scores[3] = (sum(total_scores) / 48) * 100

    # Prints the completion message and final overall score
    print("Test completed!")
    print(f"Final score: {final_scores[3]: .2f}%!")

    # Retrieves historical test results from a CSV file and calculates mean, median, and standard deviation
    MAT_df = pd.read_csv("MAT test return data.csv", index_col='userid')
    results = MAT_df['total score']
    
    mean_result = np.mean(results)
    median_result = np.median(results)
    std_dev = np.std(results)

    # Plot histogram  of test results with annotations for mean, median, and user's result
    # shows users how they compare to the baseline dataset
    plt.hist(results, bins=10, edgecolor='black')
    plt.axvline(x=mean_result, color='red', linestyle='--', label=f'Mean: {mean_result:.2f}')
    plt.axvline(x=median_result, color='green', linestyle='--', label=f'Median: {median_result:.2f}')
    plt.xlabel('Test Results')
    plt.ylabel('Frequency')
    plt.title('Distribution of Test Results')
    plt.legend()
    
    # Add annotation for user's result
    plt.annotate('Your Result', xy=(final_scores[3], 1), xytext=(final_scores[3] + 5, 3),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    # Show plot
    plt.show()

    return final_scores


# In[8]:


# Executes a full Math Ability Test (MAT) including user registration, demographic information collection,
# test execution, result recording, and optional data upload
def run_full_test():

    # for reproducible randomness (same questions everytime test runs)
    random.seed(168)

    # initialise results dictionary for each user, to be stored in google forms
    results_dict = {
        'equations': [],
        'difficulty': [],
        'score': [],
        'response_time': [],
    }

    # Prompts the user to enter a unique identifier, age, ethnicity, sex, breakfast status, and sleep duration
    # Displays buttons for user selection of ethnicity, sex, breakfast, and sleep duration, and records user responses
    id_instructions = """

    Enter your anonymised ID
    
    To generate an anonymous 4-letter unique user identifier please enter:
    - two letters based on the initials (first and last name) of a childhood friend
    - two letters based on the initials (first and last name) of a favourite actor / actress
    
    e.g. if your friend was called Charlie Brown and film star was Tom Cruise
         then your unique identifier would be CBTC
    """
    
    print(id_instructions)
    user_id = input()
    while len(user_id.strip()) != 4:
        print("Invalid input! User id must be exactly 4 letters.")
        user_id = input("Please enter your user id again: ")
    print("User entered id:", user_id)

    time.sleep(1)
    clear_output(wait=False)

    
    print("Please enter your age:")
    age = input()
    while len(str(age)) == 0:
        print("Invalid input! Age cannot be empty.")
        age = input("Please enter your age again: ")
    while float(age) < 0:
        print("Invalid input! Age cannot be negative.")
        age = input("Please enter your age again: ")
    print("User entered age:", age)

    time.sleep(1)
    clear_output(wait=False)
    
    print("What is your ethnicity?")
    ethnicity_options = ['White', 'Black or African American', 'Asian', 'Other', 'Rather not say']
    ethnicity_buttons = generate_buttons(ethnicity_options, register_event)
    display(*ethnicity_buttons)  # Display the buttons
    event_info_ethnicity = wait_for_event(timeout=60)
    clear_output(wait=False)
    ethnicity = event_info_ethnicity['description']
    print(f"User clicked: {ethnicity}")

    time.sleep(1)
    clear_output(wait=False)


    print("Please enter your biological sex:")
    sex_options = ['Male', 'Female', 'Rather not say']
    sex_buttons = generate_buttons(sex_options, register_event)
    display(*sex_buttons)  # Display the buttons
    event_info_sex = wait_for_event(timeout=60)
    clear_output(wait=False)
    sex = event_info_sex['description']
    print(f"User clicked: {sex}")

    time.sleep(1)
    clear_output(wait=False)


    print("Did you have breakfast today:")
    breakfast_options = ['Yes', 'No', 'Rather not say']
    breakfast_buttons = generate_buttons(breakfast_options, register_event)
    display(*breakfast_buttons)  # Display the buttons
    event_info_breakfast = wait_for_event(timeout=60)
    clear_output(wait=False)
    breakfast = event_info_breakfast['description']
    print(f"User clicked: {breakfast}")


    time.sleep(1)
    clear_output(wait=False)
    
    print("How long did you sleep last night?")
    sleep_options = ['less than 5 hours', '5-9 hours', 'more than 9 hours', 'Rather not say']
    sleep_buttons = generate_buttons(sleep_options, register_event)
    display(*sleep_buttons)  # Display the buttons
    event_info_sleep = wait_for_event(timeout=60)
    clear_output(wait=False)
    sleep = event_info_sleep['description']
    print(f"User clicked: {sleep}")

    time.sleep(1)
    clear_output(wait=False)

    # Provides introductory messages and prompts the user to start the test
    Intro = widgets.HTML("<h1>Welcome to the Maths Ability Test</h1>")
    Intro2 = widgets.HTML("<h2>Calculate the equations and choose the correct answers.</h2>")
    Intro3 = widgets.HTML("<h2>There are 3 difficulty levels, with increasing scores for each level. \nYou have 5 seconds to answer each question. GOOD LUCK!</h2>")
        
    display(Intro)
    display(Intro2)
    display(Intro3)

    # Delays for 5 seconds before starting the test
    time.sleep(5)
    clear_output(wait=False)

    Intro4 = widgets.HTML("<h2>Ready?</h2>")
        
    display(Intro4)

    time.sleep(1)

    Intro5 = widgets.HTML("<h2>Let's start! </h2>")
        
    display(Intro5)

    time.sleep(1)

    clear_output(wait=False)
    
    # Runs the MAT with a total of 24 iterations
    total_iterations = 24
    final_scores = run_mat(results_dict, total_iterations)

    results_df = pd.DataFrame(results_dict)

    # Prepares a data dictionary with user and test result data
    data_dict = {
    'userid': user_id,
    'age': age,
    'ethnicity': ethnicity,
    'sex': sex,
    'breakfast': breakfast,
    'sleep': sleep,
    'difficulty 1 score': final_scores[0],
    'difficulty 2 score': final_scores[1],
    'difficulty 3 score': final_scores[2],
    'total score': final_scores[3],
    'results_json': results_df.to_json()
    }

    # Asks for user's consent to upload data to Google Form
    print("\nPlease read:")
    print("")
    print("We wish to record your response data to an anonymised public data repository. ")
    print("Your data will be used for educational teaching purposes practising data analysis and visualisation.")
    print("")
    print("Please type   yes   in the box below if you consent to the upload.")

    consent = text_input("> ")
    
    print("User Entered", consent)
    
    # If consent is given, prepares a data dictionary with user and test result data and uploads it to a Google Form
    # If consent is not given, concludes the test without uploading data
    if consent.lower() == "yes":
        print("Thanks for your participation. - your data will be uploaded.")
        print("Please contact a.fedorec@ucl.ac.uk if you have any questions or concerns regarding the stored results.")

        #send_to_google_form(data_dict, form_url)
        form_url = 'https://docs.google.com/forms/d/e/1FAIpQLScatG4tNxuQgUXNf1Kx7SuwWepLXMyShECc23JWCQ5B-aI6mQ/viewform'
        send_to_google_form(data_dict, form_url)
        
    else:
        print("No problem we hope you enjoyed the test.")

    return 

