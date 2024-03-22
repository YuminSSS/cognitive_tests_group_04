#!/usr/bin/env python
# coding: utf-8

# In[1]:


from IPython.display import display, Image, clear_output, HTML
import time
import os
import random
import ipywidgets as widgets
import pandas as pd
import zipfile
from jupyter_ui_poll import ui_events
import requests
from bs4 import BeautifulSoup
import json 
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate


# In[2]:


event_info = {# Dictionary to store event information
    'type': '', # Type of event
    'description': '', # Description of event
    'time': -1 # Time of event occurrence
}

def wait_for_event(timeout=-1, interval=0.001, max_rate=20, allow_interupt=True):    
    start_wait = time.time()

    # Set event info to be empty
    # As this is a dictionary, we can change entries
    # Directly without using the global keyword
    event_info['type'] = ""
    event_info['description'] = ""
    event_info['time'] = -1

    n_proc = int(max_rate*interval)+1
    
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

# this function lets buttons 
# register events when clicked
def register_event(btn):
    # display button description in output area
    event_info['type'] = "click"
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
    event = wait_for_event(timeout=-1)
    text_input.disabled = True
    return event['description']


# In[3]:


def update_progress_bar(current, total):
    
    """
    Update progress bar based on current progress and total.

    Parameters:
        current (int): The current progress value.
        total (int): The total progress value.
    """
    # Calculate the progress percentage
    progress = current / total * 100
    # HTML code for progress bar
    progress_bar_html = f"""
        <div style="background-color: #ddd; width: 100%; height: 30px;">
            <div style="background-color: #4CAF50; width: {progress}%; height: 100%;"></div>
        </div>
        <p>{current}/{total}</p>
    """
    
    # Display the progress bar
    display(HTML(progress_bar_html))
    


# In[4]:


def run_ANS(results_dict):
    
    """
    Run the ANS test.

    Parameters:
        results_dict (dict): A dictionary to store results.

    Returns:
        int: The total score obtained in the test.
    """
    
    #Set and upload ANS images
    # Define image file names for left and right options (bigger value: Left/Right)
    ANS0 = "12_9.png"
    ANS1 = "16_12.png" #Left
    ANS2 = "20_15.png" #Left
    ANS3 = "14_12.png" #Left
    ANS4 = "21_18.png" #Left
    ANS5 = "18_16.png" #Left
    ANS6= "10_9.png" #Left
    ANS7 = "20_18.png" #Left

    ANS8 = "9_12.png" #Right
    ANS9 = "12_16.png" #Right
    ANS10 = "15_20.png" #Right
    ANS11 = "12_14.png" #Right
    ANS12 = "18_21.png" #Right
    ANS13 = "16_18.png" #Right
    ANS14 = "9_10.png" #Right
    ANS15 = "18_20.png" #Right
    

    # List of ANS images, file names, and ratios
    # ANS_left is list of images that has more dots in the left side
    ANS_list = [ANS0, ANS1, ANS2, ANS3, ANS4, ANS5, ANS6, ANS7, ANS8, ANS9, ANS10, ANS11, ANS12, ANS13, ANS14, ANS15, ANS15]
    ANS_left =[ANS0, ANS2, ANS3, ANS4, ANS5, ANS6, ANS7, ANS7]
    ANS_right=[ANS8, ANS9, ANS10, ANS11, ANS12, ANS13, ANS14, ANS15]
    
    # Create a list of file names
    filename =[]
    for i in range (16):
        filename.append(ANS_list[i])
        
    # Define image ratios  
    ratio= ['4:3', '4:3', '4:3','7:6', '7:6', '9:8', '10:9', '10:9', '3:4','3:4', '3:4', '6:7', '6:7', '9:8', '9:10', '9:10' ]

     #Zip ANS images, filename, and ratios
    zip_result=zip(ANS_list, filename, ratio)
    zip_list=list(zip_result)
   

    # Set up buttons for left and right options, function when clicked
    btn1 = widgets.Button(description="Left")
    btn2 = widgets.Button(description="Right")

    btn1.on_click(register_event) 
    btn2.on_click(register_event) 
    
    # Set random seed for reproducibility
    random.seed(64)
    score=0 # Initialize score
    correctness=[] # Initialize correctness list
    
    
    #Display instructions 
    myhtml0 = HTML("<h1 style='text-align:center;'>Look at the following images and <br> select the oval (left/right) with more dots.</h1>")
    display(myhtml0)
    myhtml00 = HTML("<h1 style='text-align:center;'>You have 3 seconds to answer each question.</h1>")
    display(myhtml00)
    myhtml000 = HTML("<h1 style='text-align:center;'>The test will start after 10-second count-down</h1>")
    display(myhtml000)
    time.sleep(5)
    clear_output()
    
    # Define countdown function
    def countdown(seconds):
        while seconds > 0:
            # Calculate the number of spaces needed to center-align the countdown
            spaces = (80 - len(str(seconds))) // 2  # Assuming 80 characters width for centering
            # Create the centered countdown string
            centered_countdown = " " * spaces + f"{seconds}"
            # Create HTML content for the countdown string
            html_content = f"<h1 style='text-align:center;'>{centered_countdown}</h1>"
            # Display the countdown as HTML
            display(HTML(html_content))
            
            
            time.sleep(1)
            seconds -= 1
            
            clear_output()
            
            
        time.sleep(1)
        html_content = "<h1 style='text-align:center;'>START!</h1>"
        display(HTML(html_content))
        
    # Count down 10-1 before the test starts
    countdown(10)
    time.sleep(1)
    clear_output()

    # Loop through the 16 images for 4 times
    for n in range (4):
        for i in range(16):
            random.shuffle(zip_list)
            
            # Set dataframe
            mydataframe=pd.DataFrame (zip_list, columns = ['ANS','file name', 'ratio'])
            
            # Extract image information
            Extracted_ANS= mydataframe['ANS'].tolist()
            Extracted_filename= mydataframe['file name'].tolist()
            Extracted_ratio= mydataframe['ratio'].tolist()
            
            # Display progress bar (1~64)
            update_progress_bar(16*n+(i + 1), 64)
            
            
            # Define HTML content to display the image centered
            html_content = f"<div style='text-align: center;'><img src='{Extracted_ANS[i]}' width='500'></div>"
            # Display the HTML content
            display(HTML(html_content))
            
            # Pause for 0.75 seconds
            time.sleep(0.75)

            # Clear the output
            clear_output()
            
            update_progress_bar(16*n+(i + 1), 64)
            # Start timer
            start_time = time.time()
            
            # Display question & buttons to pick Left or Right
            myhtml1 = HTML("<h1 style='text-align:center;'>Which side had more number of dots?</h1>")
            display(myhtml1)
            myhtml2 = HTML("<h2 style='text-align:center;'>You have 3 seconds to answer</h2>")
            display(myhtml2)
                   
            panel = widgets.HBox([btn1, btn2], layout=widgets.Layout(justify_content='center'))
            display(panel)
            result = wait_for_event(timeout=3)
            clear_output()
            
            # Scoring-right answer+1, wrong answer 0
            if result['description'] == "Left" and Extracted_ANS[i] in ANS_left:
                
                score += 1  
                correctness.append("1")
            elif result['description'] == "Right" and Extracted_ANS[i] in ANS_right:
                
                score += 1
                correctness.append("1")
            elif time.time() - start_time >= 3:  # 3s response time
                html_content = "<h1 style='text-align:center;'>Time's up! You didn't answer</h1>"
                display(HTML(html_content))
                score += 0
                correctness.append("0")
            else:
                
                score += 0
                correctness.append("0")
            
            # End time and time taken
            end_time = time.time()
            time_taken = end_time - start_time
            formatted_time=f"{time_taken:.2f}"
            html_content = f"<h1 style='text-align:center;'>Time taken: {formatted_time} seconds</h1>"
            display(HTML(html_content))
            
            #Pause between images
            time.sleep(1.5)
            clear_output()
            
            rounded_time_taken = round(time_taken, 2)
        
            # Data of each questions added to dictionary 
            results_dict['filename'].append(Extracted_filename[i])
            results_dict['ratio'].append(Extracted_ratio[i])
            results_dict['correct'].append(correctness[i])
            results_dict['response_time'].append(rounded_time_taken)
        



    #Print total score 
    overall_score = round(100 * (score / 64), 2) #percentage total score
    rounded_overall_score = int(round(overall_score)) #rounded percentage score in int 
    print(f"Your total score is: {score} / 64 ({overall_score}%) \n' ")
    print("Feel free to compare you score with other data!")

    
    # To show statistics, plot histogram with saved ANS test group data collected via Google form
    ANS_results_df = pd.read_csv("ANS test data.csv", index_col='user_id')
    results = ANS_results_df['total_score']
    
    #mean,median,and standard deviation of group data 
    mean_result = np.mean(results)
    median_result = np.median(results)
    std_dev = np.std(results)

    # Plot histogram of group data 
    plt.hist(results, bins=10, range=(0,100), edgecolor='black')
    plt.axvline(x=mean_result, color='red', linestyle='--', label=f'Mean: {mean_result:.2f}')
    plt.axvline(x=median_result, color='green', linestyle='--', label=f'Median: {median_result:.2f}')
    plt.xlabel('Test Results')
    plt.ylabel('Frequency')
    plt.title('Distribution of Test Results')
    plt.legend()

    # Add annotation for user's result in the plot
    plt.annotate(f'Your Result: {rounded_overall_score}', xy=(rounded_overall_score, 1), xytext=(rounded_overall_score + 5, 3),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    # Show plot
    plt.show()
    
    time.sleep(5)
    clear_output()
    
    
    return score



# In[5]:


def send_to_google_form(data_dict, form_url):
    ''' 
    Helper function to upload information to a corresponding google form 
    
    Parameters:
        data_dict (dict): A dictionary containing data to be uploaded.
        form_url (str): The URL of the Google Form.

    Returns:
        bool: True if the upload was successful, False otherwise.
    '''
    
    # Extract form ID from the form URL
    form_id = form_url[34:90]

     # Construct URLs for viewing and posting form responses
    view_form_url = f'https://docs.google.com/forms/d/e/{form_id}/viewform'
    post_form_url = f'https://docs.google.com/forms/d/e/{form_id}/formResponse'

    # Get the content of the form page
    page = requests.get(view_form_url)
    content = BeautifulSoup(page.content, "html.parser").find('script', type='text/javascript')
    content = content.text[27:-1]
    result = json.loads(content)[1][1]
    form_dict = {}
    
    loaded_all = True
    # Iterate over form fields and match them with data from data_dict
    for item in result:
        if item[1] not in data_dict:
            print(f"Form item {item[1]} not found. Data not uploaded.")
            loaded_all = False
            return False
        form_dict[f'entry.{item[4][0][0]}'] = data_dict[item[1]]
    
    # Post the form data
    post_result = requests.post(post_form_url, data=form_dict)
    return post_result.ok



# In[6]:


def run_full_test():
    ''' 
    Runs a full test, collecting demographic information and running the ANS test.

    Returns:
        None
    '''
    # Initialize results dictionary
    results_dict = {
        'filename': [],
        'ratio': [],
        'correct': [],
        'response_time':[]
    }
    
    time.sleep(1)
    clear_output(wait=False)

    # ID generation instructions
    id_instructions = """
    
    Enter your anonymised ID
    
    To generate an anonymous 4-letter unique user identifier please enter:
    - two letters based on the initials (first and last name) of a childhood friend
    - two letters based on the initials (first and last name) of a favourite actor / actress
    
    e.g. if your friend was called Charlie Brown and film star was Tom Cruise
         then your unique identifier would be CBTC
    """


    
    # Print the ID generation instructions
    print(id_instructions)
    # Prompt the user to enter their anonymised ID
    user_id = input("> ")
    while len(user_id.strip()) != 4:
        print("Invalid input! User id must be exactly 4 letters.")
        user_id = input("Please enter your user id again: ")
    # Confirm the user-entered ID
    print("User entered id:", user_id)

    time.sleep(1)
    clear_output(wait=False)
    
    # 1. Collect age
    print("1. Please enter your age:")
    age = input()
    while len(str(age)) == 0:
        print("Invalid input! Age cannot be empty.")
        age = input("Please enter your age again: ")
    if int(age) < 0:
        print("Invalid input! Age cannot be negative.")
        age = input("Please enter your age again: ")

    time.sleep(1)
    clear_output(wait=False)
    
    
    
     # 2. Collect ethnicity
    print("2. What is your ethnicity?")
    
    # Create buttons with options
    btna1 = widgets.Button(description='White')
    btna2 = widgets.Button(description='Black or African American/British')
    btna3 = widgets.Button(description='Asian')
    btna4 = widgets.Button(description='Other')
    btna5 = widgets.Button(description='Rather not say')
    
    
    # Assign event handlers to buttons
    btna1.on_click(register_event) 
    btna2.on_click(register_event) 
    btna3.on_click(register_event) 
    btna4.on_click(register_event) 
    btna5.on_click(register_event) 

    display(btna1, btna2, btna3, btna4, btna5)
    event_infoa = wait_for_event(timeout=60)

    ethnicity = event_infoa['description']
    print(f"User clicked: {event_infoa['description']}")

    time.sleep(1)
    clear_output(wait=False)

    
    
    # 3. Collect sex
    print("3. Please enter your biological sex:")
    
    btnb1 = widgets.Button(description='Male')
    btnb2 = widgets.Button(description='Female')
    btnb3 = widgets.Button(description='Rather not say')
    
    # Assign event handlers to buttons
    btnb1.on_click(register_event) 
    btnb2.on_click(register_event) 
    btnb3.on_click(register_event) 

    display(btnb1, btnb2, btnb3)
    event_infob = wait_for_event(timeout=60)

    sex = event_infob['description']
    print(f"User clicked: {event_infob['description']}")

    time.sleep(1)
    clear_output(wait=False)

    
    
    # 4. Collect breakfast information
    print("4. Did you have breakfast today:")
    btnc1 = widgets.Button(description='Yes')
    btnc2 = widgets.Button(description='No')
    btnc3 = widgets.Button(description='Rather not say')
    
    
    btnc1.on_click(register_event) 
    btnc2.on_click(register_event) 
    btnc3.on_click(register_event) 

    display(btnc1, btnc2, btnc3)
    event_infoc = wait_for_event(timeout=60)

    breakfast = event_infoc['description']
    print(f"User clicked: {event_infoc['description']}")

    time.sleep(1)
    clear_output(wait=False)
    
    
    # 5. Collect sleep information
    print("5. How long did you sleep last night?")
    btnd1 = widgets.Button(description='less than 5 hours')
    btnd2 = widgets.Button(description='5-9 hours')
    btnd3 = widgets.Button(description='more than 9 hours')
    btnd4 = widgets.Button(description='Rather not say')
    
    # Assign event handlers to buttons
    btnd1.on_click(register_event) 
    btnd2.on_click(register_event) 
    btnd3.on_click(register_event) 
    btnd4.on_click(register_event) 

    display(btnd1, btnd2, btnd3, btnd4)
    event_infod = wait_for_event(timeout=60)

    sleep = event_infod['description']
    print(f"User clicked: {event_infod['description']}")

    time.sleep(1)
    clear_output(wait=False)
    
    

    # Run the ANS test
    score= run_ANS(results_dict)

    
    # Create results dictionary 
    results_df = pd.DataFrame(results_dict)
    
    results_json=results_df.to_json()
    
    # Combine collected data into a dictionary
    data_dict = {
    'user_id': user_id,
    'age': age,
    'ethnicity': ethnicity,
    'sex': sex,
    'breakfast': breakfast,
    'sleep': sleep,
    'total_score': round(100*(score/64), 2),
    'results_json': results_df.to_json()
    }
    

    # Prompt for data consent
    data_consent_info = """DATA CONSENT INFORMATION:

    Please read:

    We wish to record your response data
    to an anonymised public data repository. 
    Your data will be used for educational teaching purposes
    practising data analysis and visualisation.

    Please type   yes   in the box below if you consent to the upload."""

    print(data_consent_info)
    result = text_input("> ") 
    if result == "yes" or "YES":
        print("Thanks for your participation.")
        print("Please contact a.fedorec@ucl.ac.uk")
        print("If you have any questions or concerns")
        print("regarding the stored results.")

        #send_to_google_form(data_dict, form_url)
        
        form_url = 'https://docs.google.com/forms/d/e/1FAIpQLSdBT5f3_u9lA3zd0qHG3JqFsPT0RQSE1SbvVt_xQ0MkjcSwGA/viewform?usp=sf_link'
        send_to_google_form(data_dict, form_url)
        
    else:
        # end code execution by raising an exception
        raise(Exception("User did not consent to continue test."))


    return 

