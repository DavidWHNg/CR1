# Import packages
from psychopy import core, event, gui, visual, parallel, prefs
import math
import random
import csv
import os

ports_live = None # Set to false if parallel ports not plugged for coding/debugging other parts of exp

### Experiment details/parameters
# within experiment parameters
P_info = {'PID': ''}
info_order = ['PID']

# Participant info input
while True:
    try:
        P_info["PID"] = input("Enter participant ID: ")
        if not P_info["PID"]:
            print("Participant ID cannot be empty.")
            continue
            
        csv_filename = P_info["PID"] + "_responses.csv"
        script_directory = os.path.dirname(os.path.abspath(__file__))  #Set the working directory to the folder the Python code is opened from
        
        #set a path to a "data" folder to save data in
        data_folder = os.path.join(script_directory, "data")
        
        # if data folder doesn't exist, create one
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        #set file name within "data" folder
        csv_filepath = os.path.join(data_folder,csv_filename)
        
        if os.path.exists(csv_filepath):
            print(f"Data for participant {P_info['PID']} already exists. Choose a different participant ID.") ### to avoid re-writing existing data
            
        else:
            if int(P_info["PID"]) % 4 == 0:
                group = 1
                cb = 1 # context A = light on
                group_name = "ABA"
            elif int(P_info["PID"]) % 4 == 1:
                group = 2
                cb = 1 
                group_name = "AAA"
            elif int(P_info["PID"]) % 4 == 2:
                group = 1
                cb = 2 # context A = light off
                group_name = "ABA"
            elif int(P_info["PID"]) % 4 == 3:
                group = 2
                cb = 2 
                group_name = "AAA"
            
            break  # Exit the loop if the participant ID is valid
    except KeyboardInterrupt:
        print("Participant info input canceled.")
        break  # Exit the loop if the participant info input is canceled
    
# external equipment connected via parallel ports
TENS_trig = 128 #Pin 8 TENS in AD instrument

shock_high_trig_list = [range(1,11)] # 10 levels of shock for calibration for high (100%) shock, actual mA specified in PsychLab
shock_low_trig_list = [range(11,21)] # 10 levels of shock for corresponding low (60%) to high shock, actual mA specified in PsychLab

shock_trig = {'high': 1, 'low': 11}

if cb == 1:
    context_trig = {'A': 64, 'B': 0} # Pin 7 light for context A, dark for B
elif cb == 2:
    context_trig = {'A': 0, 'B': 64} # counterbalance context A and B
    
if ports_live == True:
    pport = parallel.ParallelPort(address=0xDFD8) #Get from device Manager
    
elif ports_live == None:
    pport = None #Get from device Manager

# set up screen
win = visual.Window(
    size=(1280, 800), fullscr= True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor='testMonitor', color=[0, 0, 0], colorSpace='rgb1',
    blendMode='avg', useFBO=True,
    units='pix')

# fixation stimulus
fix_stim = visual.TextStim(win,
                            text = '+',
                            color = 'white',
                            height = 50,
                            font = 'Roboto Mono Medium')

cue_duration = 3 #NOTE cue duration still necessary for duration of treatment active time

iti = 2
expectancy_response_duration = 4
pain_response_duration = float('inf')
response_hold = 1 # How long the rating screen is left on the response (only used for Pain ratings)

# TENS/low shock
# TENS/high shock
# no TENs/high shock
# context stuff
context = {"A":0,"B":1,"calibration":0}
stimulus_name = ["TENS", "pulse monitor"]

# text stimuli
instructions_text = {'welcome': "Welcome to the experiment! Please read the following instructions carefully.",      
                     'calibration' : "Firstly, we're going to calibrate the pain intensity for the shocks you’ll receive in the experiment. As this is a study about pain, we want you to feel a little bit of pain, but nothing unbearable.\
The machine will start very low, and then will gradually work up. We want to get to a level which is painful but tolerable, so imagine a rating of about a 6 or 7 out of 10, where 1 is no pain and 10 is very painful.\n\
After each shock you will be asked if that level was ok, and if you want to try the next level. You can always come back down if it becomes too uncomfortable!\n\
Please ask the experimenter if you have any questions at anytime",
                     'experiment' : "You will receive a series of electrical shocks and your task is to rate the intensity of the pain caused by each shock on a scale from 0-10. \
A score of 0 indicates the shock caused NO PAIN A score of 10 indicates the shock was VERY PAINFUL. \
All shocks will be signaled by a 10sec countdown.\n\
The shock will occur when an X appears. The " + stimulus_name[group-1] + " will be activated on some trials. \
As you are waiting for the shock during the countdown, you will also be asked to rate some of your emotions, e.g. expectancy and distress.\n\n\
Please ask the experimenter if you have any questions now.",
                        'continue' : "\nPress spacebar to continue",
                        'end' : "This concludes the experiment. Please ask the experimenter to help remove the devices.",
                        'termination' : "The experiment has been terminated. Please ask the experimenter to help remove the devices."
}

cue_demo_text = 'When you are completely relaxed, press any key to start the next block...'

response_instructions = {'Pain': 'How painful was the shock?',
                         'Expectancy': 'How painful do you <b>expect</b> the shock to be?'}

#create instruction trials

def instruction_trial(instructions,spacetime): 
    visual.TextStim(win,
                    text = instructions,
                    color = 'white',
                    pos = (0,0)).draw()
    win.flip()
    core.wait(spacetime)
    visual.TextStim(win,
                    text = instructions,
                    color = 'white',
                    pos = (0,0)).draw()
    visual.TextStim(win,
                    text = instructions_text['continue'],
                    color = 'white',
                    pos = (0,-300)).draw()
    win.flip()
    event.waitKeys(keyList=['space'])
    
# Create functions
    # Save responses to a CSV file
def save_data(data):
    # Extract column names from the keys in the first trial dictionary
    colnames = list(trial_order[0].keys())

    # Open the CSV file for writing
    with open(csv_filepath, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=colnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each trial's data to the CSV file
        for trial in data:
            writer.writerow(trial)
    
def exit_screen(instructions):
    win.flip()
    visual.TextStim(win,
            text = instructions,
            color = 'white',
            pos = (0,0)).draw()
    win.flip()
    event.waitKeys()
    win.close()
    
def termination_check(): #insert throughout experiment so participants can end at any point.
    keys_pressed = event.getKeys(keyList=['escape'])  # Check for 'escape' key during countdown
    if 'escape' in keys_pressed:
        save_data(trial_order)
        exit_screen(instructions_text["termination"])
        core.quit()


# Define trials
# Calibration trials
trial_order = []

for i in range(1,len(shock_high_trig)):
    trial = {
        "phase": "calibration",
        "blocknum": i,
        "stimulus": 0,
        "outcome": 'high',
        "context": "calibration",
        "trialname": "calibration"
        } 

# Setting conditioning trial order
#### 4 x blocks (2 TENS + low shock, 2 control + high shock)
num_blocks_conditioning = 4
num_TENS_low = 2
num_control_high = 2

# 2 probe trials in last 2 blocks
num_probe_blocks = 2
num_probe = 1  # per block

# Creating conditioning trials for first blocks without probes
for i in range(1, num_blocks_conditioning - num_probe_blocks + 1):
    temp_trial_order = []
    
    for j in range(1, num_TENS_low + 1):
        trial = {
            "phase": "conditioning",
            "blocknum": i,
            "stimulus": 1,
            "outcome": 'low',
            "context": "A",
            "trialname": "TENS_low"
        }
        temp_trial_order.append(trial)
    
    for k in range(1, num_control_high + 1):
        trial = {
            "phase": "conditioning",
            "blocknum": i,
            "stimulus": 0,
            "outcome": 'high',
            "context": "A",
            "trialname": "control_high"
        }
        temp_trial_order.append(trial)
    
    random.shuffle(temp_trial_order)
    trial_order.extend(temp_trial_order)

# Creating trials for last blocks that include probe trials 
for i in range(num_blocks_conditioning - num_probe_blocks + 1, num_blocks_conditioning + 1):
    temp_trial_order = []
    for j in range(num_probe):
        trial = {
            "phase": "conditioning",
            "blocknum": i,
            "stimulus": 1,
            "outcome": 1,
            "context": "A",
            "trialname": "probe"
        }
        trial_order.append(trial)
        
    for j in range(1, num_TENS_low + 1):
        trial = {
            "phase": "conditioning",
            "blocknum": i,
            "stimulus": 1,
            "outcome": 0,
            "context": "A",
            "trialname": "TENS_low"
        }
        temp_trial_order.append(trial)
    
    for k in range(1, num_control_high + 1):
        trial = {
            "phase": "conditioning",
            "blocknum": i,
            "stimulus": 0,
            "outcome": 1,
            "context": "A",
            "trialname": "control_high"
        }
        temp_trial_order.append(trial)
    
    random.shuffle(temp_trial_order)
    trial_order.extend(temp_trial_order)

# Setting extinction trial order
# 4 extinction blocks * (2 TENS + high shock, 2 control + high shock)
num_blocks_extinction = 4
num_TENS_high = 2
num_control_high = 2

for i in range(1, num_blocks_extinction + 1):
    temp_trial_order = []
    
    for j in range(1, num_TENS_high + 1):
        trial = {
            "phase": "extinction",
            "blocknum": i,
            "stimulus": 1,
            "outcome": 0,
            "trialname": "TENS_high"
        }
        if group == 1:
            trial["context"] = "A"
        elif group == 2:
            trial["context"] = "B"
        temp_trial_order.append(trial)
    
    for k in range(1, num_control_high + 1):
        trial = {
            "phase": "extinction",
            "blocknum": i,
            "stimulus": 0,
            "outcome": 1,
            "trialname": "control_high"
        }
        if group == 1:
            trial["context"] = "A"
        elif group == 2:
            trial["context"] = "B"

        temp_trial_order.append(trial)
    
    random.shuffle(temp_trial_order)
    trial_order.extend(temp_trial_order)

# Assign trial numbers
for trialnum, trial in enumerate(trial_order, start=1):
    trial['trialnum'] = trialnum
    
# Put in participant information

for trial in trial_order:
    trial['PID'] = P_info['PID']
    trial['group'] = group
    trial['group_name'] = group_name
    trial['cb'] = cb

#Test questions
rating_stim = { 'Pain': visual.Slider(win,
                                    pos = (0,-200),
                                    ticks=[0,100],
                                    labels=('Not painful','Very painful'),
                                    granularity=0,
                                    size=(400,50),
                                    style=['triangleMarker'],
                                    autoLog = False),
                'Expectancy': visual.Slider(win,
                                    pos = (0,-200),
                                    ticks=[0,100],
                                    labels=('No pain','High pain'),
                                    granularity=0,
                                    size=(400,50),
                                    style=['triangleMarker'],
                                    autoLog = False)}

rating_stim['Pain'].marker.size = (30,30)
rating_stim['Pain'].marker.color = 'yellow'
rating_stim['Expectancy'].marker.size = (30,30)
rating_stim['Expectancy'].marker.color = 'yellow'

#### Make trial
def show_calib_trial(current_trial):
    win.flip()

def show_trial(current_trial):
    if pport != None:
        pport.setData(context_trig[current_trial['context']])
    fix_stim.draw()
    win.flip()
    core.wait(3)
    
    exp_rating = rating_stim['Expectancy']
    win.flip()
    
    # Start countdown to shock
    # Make a count-down screen
    countdown_timer = core.CountdownTimer(10)  # Set the initial countdown time to 10 seconds
    while countdown_timer.getTime() > 8:
        termination_check()
        visual.TextStim(win, 
                        color='white', 
                        text=str(int(math.ceil(countdown_timer.getTime())))).draw()
        win.flip()
    
    while countdown_timer.getTime() > 8: #turn on TENS at 8 seconds
        if pport != None:
            pport.setData(context_trig[current_trial['context']]+TENS_trig)
            
        termination_check()
        visual.TextStim(win, 
                        color='white', 
                        text=str(int(math.ceil(countdown_timer.getTime())))).draw()
        win.flip()
    
    while countdown_timer.getTime() > 7: #ask for expectancy at 7 seconds
        termination_check()
        visual.TextStim(win, 
                        color='white', 
                        text=str(int(math.ceil(countdown_timer.getTime())))).draw()
        visual.TextStim(win,
                text=response_instructions['Expectancy'],
                pos = (0,-100),
                ).draw()
        # Ask for expectancy rating 
        exp_rating.draw()

        win.flip()
        
    current_trial['exp_response'] = exp_rating.getRating() #saves the expectancy response for that trial
    exp_rating.reset() #resets the expectancy slider for subsequent trials
        
    # deliver pain
    fix_stim.draw()
    win.flip()
    
    if pport != None:
        pport.setData(context_trig[current_trial['context']]+shock_trig[current_trial['outcome']])
        core.wait(0.5)
        pport.setData(context_trig[current_trial['context']])
    
    # Get pain rating
    pain_rating = rating_stim['Pain']
    pain_rating.reset()
    
    while pain_rating.getRating() is None:
        termination_check()
            
        visual.TextStim(win,
                text=response_instructions['Pain'],
                pos = (0,-100),
                ).draw()
        pain_rating.draw()
        win.flip()
        
    pain_response_end_time = core.getTime() + response_hold # amount of time for participants to adjust slider after making a response
    
    while core.getTime() < pain_response_end_time:
        termination_check()
            
        visual.TextStim(win,
            text=response_instructions['Pain'],
            pos = (0,-100),
            ).draw()
        pain_rating.draw()
        win.flip()
        current_trial['pain_response'] = pain_rating.getRating()

    win.flip()
    core.wait(iti)
    
# #check values
# check_values = [trial['trialnum'] for trial in trial_order]
# print(check_values)

# check_values = [trial['trialname'] for trial in trial_order]
# print(check_values)

exp_finish = False

# Run experiment
while not exp_finish:
    instruction_trial(instructions_text['welcome'],3)
    instruction_trial(instructions_text["calibration"],5)
    instruction_trial(instructions_text["experiment"],5)
    
    for trial in trial_order:
        show_trial(trial)
              
    save_data(trial_order)
    exit_screen(instructions_text["end"])
    
    exp_finish = True
    
win.close()