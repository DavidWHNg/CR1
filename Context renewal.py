# Import packages
from psychopy import core, event, gui, visual, parallel, prefs
import math
import random
import csv
import os

ports_live = None # Set to false if parallel ports not plugged for coding/debugging other parts of exp

### Experiment details/parameters
# within experiment parameters
P_info = {"PID": ""}
info_order = ["PID"]

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
        
        # if data folder doesn"t exist, create one
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
shock_levels = 10
shock_trig = {"high": 1, "low": 11} #start on lowest levels

TENS_trig = 128 #Pin 8 TENS in AD instrument

if cb == 1:
    context_trig = {"A": 64, "B": 0, "calibration":0} # Pin 7 light for context A, dark for B
elif cb == 2:
    context_trig = {"A": 0, "B": 64, "calibration":0} # counterbalance context A and B

if ports_live == True:
    pport = parallel.ParallelPort(address=0xDFD8) #Get from device Manager
    
elif ports_live == None:
    pport = None #Get from device Manager

shock_duration = 0.5
iti = 1
pain_response_duration = float("inf")
response_hold = 1.5 # How long the rating screen is left on the response (only used for Pain ratings)

# text stimuli
instructions_text = {
    "welcome": "Welcome to the experiment! Please read the following instructions carefully.", 
    "TENS_introduction": "This experiment aims to investigate the effects of Transcutaneous Electrical Nerve Stimulation (TENS) on pain sensitivity. TENS may be able to decrease pain sensitivity by blocking the pain signals that travel up your arm and into your brain.\n\n\
        The TENS itself is not painful, but you will feel a small sensation when it is turned on",
    "calibration" : "Firstly, we are going to calibrate the pain intensity for the shocks you will receive in the experiment without TENS. As this is a study about pain, we want you to feel a moderate bit of pain, but nothing unbearable. \
The machine will start low, and then will gradually work up. We want to get to a level which is painful but tolerable, so roughly at a rating of around 7 out of 10, where 1 is not painful and 10 is very painful.\n\n\
After each shock you will be asked if that level was ok, and you will be given the option to either try the next level or set the current shock level for the experiment. You can always come back down if it becomes too uncomfortable!\n\n\
Please ask the experimenter if you have any questions at anytime",
    "calibration_finish": "Thank you for completing the calibration, your maximum shock intensity has now been set.",
    "experiment" : "We can now begin the experiment. \n\n\
You will now receive a series of electrical shocks and your task is to rate the intensity of the pain caused by each shock on a rating scale.\
This rating scale ranges from NOT PAINFUL to VERY PAINFUL. \n\n\
All shocks will be signaled by a 10 second countdown. The shock will occur when an X appears, similarly as in the calibration procedure. The TENS will now also be active on some trials.\
As you are waiting for the shock during the countdown, you will also be asked to rate how painful you expect the following shock to be.\n\n\
Please ask the experimenter if you have any questions now before proceeding.",
    "continue" : "\n\nPress spacebar to continue",
    "end" : "This concludes the experiment. Please ask the experimenter to help remove the devices.",
    "termination" : "The experiment has been terminated. Please ask the experimenter to help remove the devices."
}

cue_demo_text = "When you are completely relaxed, press any key to start the next block..."

response_instructions = {
    "Pain": "How painful was the shock?",
    "Expectancy": "How painful do you expect the next shock to be?",
    "Shock": "Press spacebar to activate the shock",
    "Check": "Please indicate whether you wouldlike to try the next level of shock, stay at this level, or go back to the previous level for the experiment.",
    "Check_max": "Note that this is the maximum level of shock.\n\n\
 Would you like to stay at this level or go down a level?"
                         }

# set up screen
win = visual.Window(
    size=(1280, 800), fullscr= True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor="testMonitor", color=[0, 0, 0], colorSpace="rgb1",
    blendMode="avg", useFBO=True,
    units="pix")

# fixation stimulus
fix_stim = visual.TextStim(win,
                            text = "x",
                            color = "white",
                            height = 50,
                            font = "Roboto Mono Medium")

#create instruction trials
def instruction_trial(instructions,holdtime): 
    visual.TextStim(win,
                    text = instructions,
                    height = 35,
                    color = "white",
                    pos = (0,0),
                    wrapWidth= 960
                    ).draw()
    win.flip()
    core.wait(holdtime)
    visual.TextStim(win,
                    text = instructions,
                    height = 35,
                    color = "white",
                    pos = (0,0),
                    wrapWidth= 960
                    ).draw()
    visual.TextStim(win,
                    text = instructions_text["continue"],
                    height = 35,
                    color = "white",
                    pos = (0,-300)
                    ).draw()
    win.flip()
    event.waitKeys(keyList=["space"])
    win.flip()
    
    core.wait(1)
    
# Create functions
    # Save responses to a CSV file
def save_data(data):
    # Extract column names from the keys in the first trial dictionary
    colnames = list(trial_order[0].keys())

    # Open the CSV file for writing
    with open(csv_filepath, mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=colnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write each trial"s data to the CSV file
        for trial in data:
            writer.writerow(trial)
    
def exit_screen(instructions):
    win.flip()
    visual.TextStim(win,
            text = instructions,
            height = 35,
            color = "white",
            pos = (0,0)).draw()
    win.flip()
    event.waitKeys()
    win.close()
    
def termination_check(): #insert throughout experiment so participants can end at any point.
    keys_pressed = event.getKeys(keyList=["escape"])  # Check for "escape" key during countdown
    if "escape" in keys_pressed:     
        # Save participant information
        trial_order.extend(calib_trial_order)
        
        for trial in trial_order:
            trial["PID"] = P_info["PID"]
            trial["group"] = group
            trial["group_name"] = group_name
            trial["cb"] = cb
            trial["shock_level"] = shock_trig["high"]
            
        save_data(trial_order)
        exit_screen(instructions_text["termination"])
        core.quit()


# Define trials
# Calibration trials
calib_trial_order = []
for i in range(1,shock_levels+1):
    temp_trial_order = []
    trial = {
        "phase": "calibration",
        "blocknum": "calibration",
        "stimulus": 0,
        "outcome": "high",
        "context": "calibration",
        "trialname": "calibration",
        "pain_response": None
        } 
    temp_trial_order.append(trial)
    
    calib_trial_order.extend(temp_trial_order)

# Setting conditioning trial order
# Number of trials
trial_order = []

#### 4 x blocks (2 TENS + low shock, 2 control + high shock)
num_blocks_conditioning = 4
num_TENS_low = 4
num_control_high = 4

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
            "stimulus": "TENS",
            "outcome": "low",
            "context": "A",
            "trialname": "TENS_low",
            "exp_response": None,
            "pain_response": None
        }
        temp_trial_order.append(trial)
    
    for k in range(1, num_control_high + 1):
        trial = {
            "phase": "conditioning",
            "blocknum": i,
            "stimulus": "control",
            "outcome": "high",
            "context": "A",
            "trialname": "control_high",
            "exp_response": None,
            "pain_response": None
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
            "stimulus": "TENS",
            "outcome": "high",
            "context": "A",
            "trialname": "probe",
            "exp_response": None,
            "pain_response": None
        }
        trial_order.append(trial)
        
    for j in range(1, num_TENS_low + 1):
        trial = {
            "phase": "conditioning",
            "blocknum": i,
            "stimulus": "TENS",
            "outcome": "low",
            "context": "A",
            "trialname": "TENS_low",
            "exp_response": None,
            "pain_response": None
        }
        temp_trial_order.append(trial)
    
    for k in range(1, num_control_high + 1):
        trial = {
            "phase": "conditioning",
            "blocknum": i,
            "stimulus": "control",
            "outcome": "high",
            "context": "A",
            "trialname": "control_high",
            "exp_response": None,
            "pain_response": None
        }
        temp_trial_order.append(trial)
    
    random.shuffle(temp_trial_order)
    trial_order.extend(temp_trial_order)

# Setting extinction trial order
# 4 extinction blocks * (2 TENS + high shock, 2 control + high shock)
num_blocks_extinction = 4
num_TENS_high = 4
num_control_high = 4

for i in range(1, num_blocks_extinction + 1):
    temp_trial_order = []
    
    for j in range(1, num_TENS_high + 1):
        trial = {
            "phase": "extinction",
            "blocknum": i,
            "stimulus": "TENS",
            "outcome": "high",
            "trialname": "TENS_high",
            "exp_response": None,
            "pain_response": None
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
            "stimulus": "control",
            "outcome": "high",
            "trialname": "control_high",
            "exp_response": None,
            "pain_response": None
        }
        if group == 1:
            trial["context"] = "A"
        elif group == 2:
            trial["context"] = "B"

        temp_trial_order.append(trial)
    
    random.shuffle(temp_trial_order)
    trial_order.extend(temp_trial_order)
    
# Setting renewal test trial order
# 2 renewal blocks * (4 TENS + high shock, 4 control + high shock)
num_blocks_renewal = 2
num_TENS_high = 4
num_control_high = 4

for i in range(1, num_blocks_renewal + 1):
    temp_trial_order = []
    
    for j in range(1, num_TENS_high + 1):
        trial = {
            "phase": "renewal",
            "blocknum": i,
            "stimulus": "TENS",
            "outcome": "high",
            "trialname": "TENS_high",
            "context": "A",
            "exp_response": None,
            "pain_response": None
        }
        
        temp_trial_order.append(trial)
    
    for k in range(1, num_control_high + 1):
        trial = {
            "phase": "renewal",
            "blocknum": i,
            "stimulus": "control",
            "outcome": "high",
            "trialname": "control_high",
            "context": "A",
            "exp_response": None,
            "pain_response": None
        }
        temp_trial_order.append(trial)
    
    random.shuffle(temp_trial_order)
    trial_order.extend(temp_trial_order)

# Assign trial numbers
for trialnum, trial in enumerate(trial_order, start=1):
    trial["trialnum"] = trialnum
    
#Test questions
rating_stim = { "Calibration": visual.Slider(win,
                                    pos = (0,-200),
                                    ticks=(0,50,100),
                                    labels=(1,5,10),
                                    granularity=0,
                                    size=(600,60),
                                    style=["rating"],
                                    autoLog = False),
                "Pain": visual.Slider(win,
                                    pos = (0,-200),
                                    ticks=(0,100),
                                    labels=("Not painful","Very painful"),
                                    granularity=0,
                                    size=(600,60),
                                    style=["triangleMarker"],
                                    autoLog = False),
                "Expectancy": visual.Slider(win,
                                    pos = (0,-200),
                                    ticks=[0,100],
                                    labels=("Not painful","Very painful"),
                                    granularity=0,
                                    size=(600,60),
                                    style=["triangleMarker"],
                                    autoLog = False)}

rating_stim["Pain"].marker.size = (30,30)
rating_stim["Pain"].marker.color = "yellow"
rating_stim["Calibration"].marker.size = (30,30)
rating_stim["Calibration"].marker.color = "yellow"
rating_stim["Expectancy"].marker.size = (30,30)
rating_stim["Expectancy"].marker.color = "yellow"

# Define button_text and calib_buttons dictionaries
button_text = {
    "Next": visual.TextStim(win,
                            text="Try the next shock level",
                            color="white",
                            height=25,
                            pos=(400, -200),
                            wrapWidth=300
                            ),                            
    "Stay": visual.TextStim(win,
                            text="Stay at this shock level",
                            color="white",
                            height=25,
                            pos=(0, -200),
                            wrapWidth=300),
    "Previous": visual.TextStim(win,
                            text="Set the previous shock level",
                            color="white",
                            height=25,
                            pos=(-400, -200),
                            wrapWidth=300)
}

calib_buttons = {
    "Next": visual.Rect(win,
                        width=300,
                        height=80,
                        fillColor="black",
                        lineColor="white",
                        pos=(400, -200)),
    "Stay": visual.Rect(win,
                        width=300,
                        height=80,
                        fillColor="black",
                        lineColor="white",
                        pos=(0, -200)),
    "Previous": visual.Rect(win,
                    width=300,
                    height=80,
                    fillColor="black",
                    lineColor="white",
                    pos=(-400, -200))
}

calib_finish = False

#### Make trial functions
    # calibration trials
def show_calib_trial(current_trial):
    global calib_finish
    termination_check()
    
    # Wait for participant to ready up for shock
    visual.TextStim(win,
        text=response_instructions["Shock"],
        height = 35,
        pos = (0,0),
        wrapWidth= 800
        ).draw()
    
    win.flip()
    event.waitKeys(keyList = ["space"])
    
    # deliver pain
    fix_stim.draw()
    win.flip()
    
    # deliver shock
    if pport != None:
        pport.setData(shock_trig["high"])
        core.wait(shock_duration)
        pport.setData(0)
    
    core.wait(1)
    
    # Get pain rating
    calib_rating = rating_stim["Calibration"]
    calib_rating.reset()
    
    while calib_rating.getRating() is None:
        termination_check()
            
        visual.TextStim(win,
                text=response_instructions["Pain"],
                height = 35,
                pos = (0,-100),
                ).draw()
        calib_rating.draw()
        win.flip()
         
    current_trial["pain_response"] = calib_rating.getRating()
    
    win.flip()
    core.wait(1)
    
    if shock_trig["high"] < 10:
        visual.TextStim(win,
                text=response_instructions["Check"],
                height = 35,
                pos = (0,0),
                ).draw()
    elif shock_trig["high"] == 10:
                visual.TextStim(win,
                text=response_instructions["Check_max"],
                height = 35,
                pos = (0,0),
                ).draw()

    # Draw buttons and text
    if shock_trig["high"] == 1:
        buttons_keylist = ["Next", "Stay"]
    elif shock_trig["high"] == 10:
        buttons_keylist = ["Previous", "Stay"]
    else:
        buttons_keylist = calib_buttons.keys()

    for button_name in buttons_keylist:
        calib_buttons[button_name].draw()
        button_text[button_name].draw()

    win.flip()
    
    # Wait for a mouse click
    trial_finish = False
    mouse = event.Mouse()
    mouse.clickReset()
    
    while trial_finish == False:
        for button_name, button_rect in calib_buttons.items():
            if mouse.isPressedIn(button_rect):
                if button_name == "Next":
                        shock_trig["high"] = shock_trig["high"] + 1
                        shock_trig["low"] = shock_trig["low"] + 1
                        trial_finish = True
                    
                elif button_name == "Stay":
                    calib_finish = True
                    trial_finish = True
                    
                elif button_name == "Previous":
                    shock_trig["high"] = shock_trig["high"] - 1
                    shock_trig["low"] = shock_trig["low"] - 1
                    calib_finish = True
                    trial_finish = True
                    
    win.flip()
    
    core.wait(iti)

# if pain rating < 65, give option to go to the next one. If it"s too high, give option to go back a level. Do we need to tell them what the target pain rating is? 
    # need to also give option to go backwards
    
def show_trial(current_trial):
    if pport != None:
        pport.setData(context_trig[current_trial["context"]])
    win.flip()
    core.wait(3)
    
    exp_rating = rating_stim["Expectancy"]
    win.flip()
    
    # Start countdown to shock
    # Make a count-down screen
    countdown_timer = core.CountdownTimer(10)  # Set the initial countdown time to 10 seconds
    while countdown_timer.getTime() > 8:
        termination_check()
        visual.TextStim(win, 
                        color="white", 
                        height = 50,
                        text=str(int(math.ceil(countdown_timer.getTime())))).draw()
        win.flip()
    
    while countdown_timer.getTime() < 8 and countdown_timer.getTime() > 7: #turn on TENS at 8 seconds
        if pport != None:
            pport.setData(context_trig[current_trial["context"]]+TENS_trig)
            
        termination_check()
        visual.TextStim(win, 
                        color="white", 
                        height = 50,
                        text=str(int(math.ceil(countdown_timer.getTime())))).draw()
        win.flip()
    
    while countdown_timer.getTime() < 7 and countdown_timer.getTime() > 0: #ask for expectancy at 7 seconds
        termination_check()
        visual.TextStim(win, 
                        color="white", 
                        height = 50,
                        text=str(int(math.ceil(countdown_timer.getTime())))).draw()
        visual.TextStim(win,
                text=response_instructions["Expectancy"],
                height = 35,
                pos = (0,-100),
                ).draw()
        
        # Ask for expectancy rating 
        exp_rating.draw()

        win.flip()
        
    current_trial["exp_response"] = exp_rating.getRating() #saves the expectancy response for that trial
    exp_rating.reset() #resets the expectancy slider for subsequent trials
        
    # deliver pain
    fix_stim.draw()
    win.flip()
    
    if pport != None:
        pport.setData(context_trig[current_trial["context"]]+shock_trig[current_trial["outcome"]])
        core.wait(shock_duration)
        pport.setData(context_trig[current_trial["context"]])
        
    core.wait(1)
    
    # Get pain rating
    pain_rating = rating_stim["Pain"]
    pain_rating.reset()
    
    while pain_rating.getRating() is None:
        termination_check()
            
        visual.TextStim(win,
                text=response_instructions["Pain"],
                height = 35,
                pos = (0,-100),
                ).draw()
        pain_rating.draw()
        win.flip()
        
    pain_response_end_time = core.getTime() + response_hold # amount of time for participants to adjust slider after making a response
    
    while core.getTime() < pain_response_end_time:
        termination_check()
            
        visual.TextStim(win,
            text=response_instructions["Pain"],
            height = 35,
            pos = (0,-100),
            ).draw()
        pain_rating.draw()
        win.flip()
        current_trial["pain_response"] = pain_rating.getRating()

    win.flip()
    
    core.wait(iti)
    
# #check values
# check_values = [trial["trialnum"] for trial in trial_order]
# print(check_values)

# check_values = [trial["trialname"] for trial in trial_order]
# print(check_values)

exp_finish = False

# Run experiment
while not exp_finish:
    #display welcome and calibration instructions
    instruction_trial(instructions_text["welcome"],3)
    instruction_trial(instructions_text["TENS_introduction",3])
    instruction_trial(instructions_text["calibration"],8)
    
    for trial in calib_trial_order:
        show_calib_trial(trial)
        if calib_finish == True:
            break
    
    instruction_trial(instructions_text["calibration_finish"],3)
    
    #display main experiment phase
    instruction_trial(instructions_text["experiment"],5)
    for trial in trial_order:
        show_trial(trial)

        
    # save trial data
    save_data(trial_order)
    exit_screen(instructions_text["end"])
    
    exp_finish = True
    
win.close()