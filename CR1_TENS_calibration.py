
from psychopy import core, event, gui, visual, parallel, prefs
pport = parallel.ParallelPort(address=0xDFD8)

win = visual.Window(
    size=(1920, 1080), fullscr= True, screen=0,
    allowGUI=False, allowStencil=False,
    monitor="testMonitor", color=[0, 0, 0], colorSpace="rgb1",
    blendMode="avg", useFBO=True,
    units="pix")

visual.TextStim(win,
                text="Please let the experimenter know when you begin to feel the TENS",
                color="white",
                height=25,
                pos=(0, 0),
                wrapWidth=600
                ).draw()

win.flip()

calib_finish = False

while calib_finish == False:
    keys_pressed = event.getKeys()  
    if 'space' in keys_pressed:  # Check for "spacebar" to end calibration
        calib_finish = True
    pport.setData(128)
    core.wait(0.1)
    pport.setData(0)
    core.wait(0.1)

pport.setData(0)
core.quit()