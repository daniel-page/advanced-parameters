import adsk.core
import adsk.fusion
import os
from ... import config
from ...lib import fusion360utils as futil
from tkinter import *
from tkinter import ttk
import threading

app = adsk.core.Application.get()
ui = app.userInterface
isWindowOpen = False

CMD_NAME = "Advanced Parameters"
CMD_ID = f"{config.COMPANY_NAME}_{config.ADDIN_NAME}_{CMD_NAME}"
CMD_Description = "Opens an external window with advanced parameter settings."
IS_PROMOTED = True

# Global variables by referencing values from /config.py
WORKSPACE_ID = config.design_workspace
TAB_ID = config.tools_tab_id
TAB_NAME = config.my_tab_name

PANEL_ID = config.my_panel_id
PANEL_NAME = config.my_panel_name
PANEL_AFTER = config.my_panel_after

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "")

# Holds references to event handlers
local_handlers = []


def delete_parameter(row_number):
    """Removes a user parameter"""

    global parameters

    parameters[row_number].deleteMe()


def createScaleBlock(window, row_number, parameter_label):
    """Generates a row of information and controls for a parameter"""

    global entry_add_value, spinbox_min, spinbox_max, spinbox_increment

    length_label = Label(window, text=parameter_label, width=8, anchor="w")
    length_label.grid(
        row=row_number, column=0, sticky=W, pady=(17, 0), padx=(0, 20), columnspan=10
    )

    slider_min = Label(window, text=spinbox_min.get(), width=4)
    slider_min.grid(row=row_number, column=10, pady=(17, 0), columnspan=10)

    slider = Scale(
        window,
        from_=float(spinbox_min.get()),
        to=float(spinbox_max.get()),
        resolution=float(spinbox_increment.get()),
        orient="horizontal",
        length=269,
    )
    slider.grid(row=row_number, column=20, columnspan=10)

    slider.bind(
        "<MouseWheel>",
        lambda event: slider.set(slider.get() - float(spinbox_increment.get()))
        if event.delta == -120
        else slider.set(slider.get() + float(spinbox_increment.get()))
        if event.delta == 120
        else ...,
    )

    slider_max = Label(window, text=spinbox_max.get(), width=4)
    slider_max.grid(
        row=row_number, column=30, padx=(0, 17), pady=(17, 0), columnspan=10
    )

    button_delete = Button(
        window, text="Delete", width=6, command=lambda: delete_parameter(row_number)
    )
    button_delete.grid(
        row=row_number, column=40, pady=(17, 0), padx=(0, 20), columnspan=10
    )

    button_update = Button(
        window,
        text="Update",
        width=6,
        command=lambda: slider.set(entry_add_value.get()),
    )
    button_update.grid(
        row=row_number, column=50, pady=(17, 0), padx=(0, 0), columnspan=10
    )

    return slider, slider_min, slider_max


def addParameter(name, value):
    """Adds a user parameter"""

    global parameters

    parameters.add(name, adsk.core.ValueInput.createByString(value), "mm", "")


def updateSettings():
    """Updates window to reflect changed settings"""
    global scaleBlocks, spinbox_min, spinbox_max, spinbox_increment

    if (
        scaleBlocks != None
        and spinbox_min != None
        and spinbox_max != None
        and spinbox_increment != None
    ):
        for i, _ in enumerate(scaleBlocks):
            scaleBlocks[i][0].configure(
                from_=float(spinbox_min.get()),
                to=float(spinbox_max.get()),
                resolution=float(spinbox_increment.get()),
            )
            scaleBlocks[i][1].configure(text=spinbox_min.get())
            scaleBlocks[i][2].configure(text=spinbox_max.get())


def queueSettingsUpdate():
    """Queues an update for min/min/increment settings in the mainloop"""

    global is_settings_update

    is_settings_update = True


def updateWindow():
    """Syncs parameters between the Fusion360 workspace and the external window GUI"""

    global scaleBlocks, parameters, window, last_num_parameters, entry_add_value, spinbox_min, spinbox_max, spinbox_increment, is_settings_update

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    parameters = design.userParameters

    if is_settings_update:
        updateSettings()
        is_settings_update = False

    # Checks if there is a change in the number of parameters
    if last_num_parameters != len(parameters):
        last_num_parameters = len(parameters)

        for l in window.grid_slaves():
            l.destroy()

        scaleBlocks = []

        if len(parameters) > 0:

            window_top = Frame(window)
            window_top.grid(row=0, column=0, columnspan=70, padx=(10, 10), pady=(10, 0))

            label_add_name = Label(window_top, text="Name: ", anchor="w")
            label_add_name.grid(row=0, column=0, sticky=W, padx=(0, 5), columnspan=10)

            entry_add_name = Entry(
                window_top,
                width=15,
                relief=FLAT,
                highlightbackground="grey",
                highlightthickness=1,
            )
            entry_add_name.grid(row=0, column=10, sticky=W, padx=(0, 20), columnspan=10)

            label_add_value = Label(window_top, text="Value: ", anchor="w")
            label_add_value.grid(row=0, column=20, sticky=W, padx=(0, 5), columnspan=10)

            entry_add_value = Entry(
                window_top,
                width=15,
                relief=FLAT,
                highlightbackground="grey",
                highlightthickness=1,
            )
            entry_add_value.grid(
                row=0, column=30, sticky=W, padx=(0, 20), columnspan=10
            )

            label_add_comment = Label(window_top, text="Comment: ", anchor="w")
            label_add_comment.grid(
                row=0, column=40, sticky=W, padx=(0, 5), columnspan=10
            )

            entry_add_comment = Entry(
                window_top,
                width=15,
                relief=FLAT,
                highlightbackground="grey",
                highlightthickness=1,
            )
            entry_add_comment.grid(
                row=0, column=50, sticky=W, padx=(0, 20), columnspan=10
            )

            button_add = Button(
                window_top,
                text="Add",
                width=6,
                command=lambda: addParameter(
                    entry_add_name.get(), entry_add_value.get()
                ),
            )
            button_add.grid(row=0, column=60, padx=(0, 0), columnspan=10)

            label_add_min = Label(window_top, text="Min: ", anchor="w")
            label_add_min.grid(
                row=1, column=0, sticky=W, padx=(0, 5), pady=(6, 0), columnspan=10
            )

            spinbox_min = ttk.Spinbox(
                window_top, width=12, command=queueSettingsUpdate, from_=0, to=10000
            )
            spinbox_min.grid(
                row=1,
                column=10,
                sticky=W + E,
                padx=(0, 20),
                pady=(6, 0),
                columnspan=10,
            )
            spinbox_min.delete(0)
            spinbox_min.insert(0, "5")

            label_add_max = Label(window_top, text="Max: ", anchor="w")
            label_add_max.grid(
                row=1,
                column=20,
                sticky=W + E,
                padx=(0, 5),
                pady=(6, 0),
                columnspan=10,
            )

            spinbox_max = ttk.Spinbox(
                window_top, width=12, command=queueSettingsUpdate, from_=0, to=10000
            )
            spinbox_max.grid(
                row=1,
                column=30,
                sticky=W + E,
                padx=(0, 20),
                pady=(6, 0),
                columnspan=10,
            )
            spinbox_max.delete(0)
            spinbox_max.insert(0, "100")

            label_add_min = Label(window_top, text="Increment: ", anchor="w")
            label_add_min.grid(
                row=1,
                column=40,
                sticky=W + E,
                padx=(0, 5),
                pady=(6, 0),
                columnspan=10,
            )

            spinbox_increment = ttk.Spinbox(
                window_top, width=12, command=queueSettingsUpdate, from_=0, to=10000
            )
            spinbox_increment.grid(
                row=1,
                column=50,
                sticky=W + E,
                padx=(0, 20),
                pady=(6, 0),
                columnspan=10,
            )
            spinbox_increment.delete(0)
            spinbox_increment.insert(0, "2")

            button_apply = Button(
                window_top, text="Apply", width=6, command=updateSettings
            )
            button_apply.grid(row=1, column=60, padx=(0, 0), pady=(6, 0), columnspan=10)

            window_bottom = Frame(window)
            window_bottom.grid(
                row=1, column=0, columnspan=70, padx=(10, 10), pady=(0, 10)
            )

            for i, _ in enumerate(parameters):
                scaleBlocks.append(
                    createScaleBlock(window_bottom, i, parameters.item(i).name)
                )
                scaleBlocks[i][0].set(parameters.item(i).value * 10)

    if len(parameters) == len(scaleBlocks):
        for i, _ in enumerate(parameters):
            if (
                round(parameters.item(i).value, 2)
                != round(scaleBlocks[i][0].get() / 10, 2)
                and len(ui.activeSelections) == 0
            ):
                slider_val = scaleBlocks[i][0].get() / 10
                param_val = parameters.item(i)
                param_val.value = round(slider_val, 2)

    window.after(150, updateWindow)  # Runs the function again after a time


def onClosing():
    """Window state updated and object destroyed so another instance can be opened"""

    global window, isWindowOpen

    isWindowOpen = False
    window.destroy()


def externalWindow():
    """Opens and intialises an external window"""

    global parameters, scaleBlocks, window, last_num_parameters, entry_add_value, spinbox_min, spinbox_max, spinbox_increment, is_settings_update

    entry_add_value = None
    spinbox_max = None
    spinbox_min = None
    spinbox_increment = None
    parameters = None
    scaleBlocks = None
    is_settings_update = False

    window = Tk()
    window.title("Advanced Parameters")
    window.iconbitmap(
        os.path.dirname(os.path.abspath(__file__)) + "\\resources\\16x16.ico"
    )
    window.resizable(width=False, height=False)
    window.attributes("-topmost", True)

    last_num_parameters = None
    updateWindow()

    # window.columnconfigure(1, weight=1)  # Allow widgets to expand to full width
    window.protocol("WM_DELETE_WINDOW", onClosing)

    window.mainloop()  # Starts the gui (blocking method)

    # Resets created global variables after the gui is closed
    del scaleBlocks
    del window
    del last_num_parameters
    del entry_add_value
    del parameters
    del spinbox_min
    del spinbox_max
    del spinbox_increment
    del is_settings_update


# Executed when add-in is run.
def start():

    # if not design:
    #     ui.messageBox("A Fusion design must be active when invoking this command.")
    #     return ()

    # ******************************** Create Command Definition ********************************
    cmd_def = ui.commandDefinitions.addButtonDefinition(
        CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER
    )

    # Add command created handler. The function passed here will be executed when the command is executed.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******************************** Create Command Control ********************************
    # Get target workspace for the command.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get target toolbar tab for the command and create the tab if necessary.
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    if toolbar_tab is None:
        toolbar_tab = workspace.toolbarTabs.add(TAB_ID, TAB_NAME)

    # Get target panel for the command and and create the panel if necessary.
    panel = toolbar_tab.toolbarPanels.itemById(PANEL_ID)
    if panel is None:
        panel = toolbar_tab.toolbarPanels.add(PANEL_ID, PANEL_NAME, PANEL_AFTER, False)

    # Create the command control, i.e. a button in the UI.
    control = panel.controls.addCommand(cmd_def, "ChangeParameterCommand", False)

    # Now you can set various options on the control such as promoting it to always be shown.
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    toolbar_tab = workspace.toolbarTabs.itemById(TAB_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()

    # Delete the panel if it is empty
    if panel.controls.count == 0:
        panel.deleteMe()

    # Delete the tab if it is empty
    if toolbar_tab.toolbarPanels.count == 0:
        toolbar_tab.deleteMe()


# Function to be called when a user clicks the corresponding button in the UI
# Here you define the User Interface for your command and identify other command events to potentially handle
def command_created(args: adsk.core.CommandCreatedEventArgs):

    # General logging for debug
    futil.log(f"{CMD_NAME} Command Created Event")

    # Connect to the events that are needed by this command.
    futil.add_handler(
        args.command.execute, command_execute, local_handlers=local_handlers
    )

    futil.add_handler(
        args.command.destroy, command_destroy, local_handlers=local_handlers
    )


def command_execute(args: adsk.core.CommandEventArgs):
    """Opens the Advanced Parameters window if another istance is not already open"""

    global isWindowOpen

    if not isWindowOpen:
        window_process = threading.Thread(target=externalWindow)
        window_process.start()
        isWindowOpen = True

    futil.log(f"{CMD_NAME} Command Execute Event")


def command_destroy(args: adsk.core.CommandEventArgs):
    """This function will be called when the user completes the command"""

    global local_handlers

    local_handlers = []

    futil.log(f"{CMD_NAME} Command Destroy Event")
