#  Copyright 2022 by Autodesk, Inc.
#  Permission to use, copy, modify, and distribute this software in object code form
#  for any purpose and without fee is hereby granted, provided that the above copyright
#  notice appears in all copies and that both that copyright notice and the limited
#  warranty and restricted rights notice below appear in all supporting documentation.
#
#  AUTODESK PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. AUTODESK SPECIFICALLY
#  DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.
#  AUTODESK, INC. DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE
#  UNINTERRUPTED OR ERROR FREE.

import adsk.core
import adsk.fusion
import os
from ... import config
from ...lib import fusion360utils as futil

from tkinter import *
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

    global entry_add_value

    length_label = Label(window, text=parameter_label)
    length_label.grid(row=row_number, column=0, pady=(17, 0), padx=(0, 10))

    slider_min_value = 1
    slider_min = Label(window, text=str(slider_min_value))
    slider_min.grid(row=row_number, column=1, pady=(17, 0))

    slider_max_value = 1_000
    slider_max = Label(window, text=str(slider_max_value))
    slider_max.grid(row=row_number, column=3, padx=(0, 0), pady=(17, 0))

    slider = Scale(
        window,
        from_=slider_min_value,
        to=slider_max_value,
        orient="horizontal",
        length=400,
    )
    slider.grid(row=row_number, column=2)

    slider.bind(
        "<MouseWheel>",
        lambda event: slider.set(slider.get() - 1)
        if event.delta == -120
        else slider.set(slider.get() + 1)
        if event.delta == 120
        else ...,
    )

    button_delete = Button(
        window, text="Delete", command=lambda: delete_parameter(row_number)
    )
    button_delete.grid(row=row_number, column=4, pady=(17, 0), padx=(0, 20))

    button_update = Button(
        window,
        text="Update",
        command=lambda: slider.set(entry_add_value.get()),
    )
    button_update.grid(row=row_number, column=5, pady=(17, 0), padx=(0, 20))

    return slider


def add_parameter(name, value):
    """Adds a user parameter"""

    global parameters

    parameters.add(name, adsk.core.ValueInput.createByString(value), "mm", "")


def updateParameters():
    """Syncs parameters between the Fusion360 workspace and the external window GUI"""

    global scaleBlocks, parameters, window, last_num_parameters, entry_add_value

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    parameters = design.userParameters

    # Checks if there is a change in the number of parameters
    if last_num_parameters != len(parameters):
        last_num_parameters = len(parameters)

        for l in window.grid_slaves():
            l.destroy()

        scaleBlocks = []

        if len(parameters) > 0:

            frame = Frame(window)
            frame.grid(row=0, column=0, columnspan=8, padx=(0, 0), pady=(10, 0))

            label_add_name = Label(frame, text="Name: ")
            label_add_name.grid(row=0, column=0, sticky=W + E, padx=(20, 0))

            entry_add_name = Entry(frame)
            entry_add_name.grid(row=0, column=1, sticky=W + E, padx=(20, 0))

            label_add_value = Label(frame, text="Value: ")
            label_add_value.grid(row=0, column=2, sticky=W + E, padx=(20, 0))

            entry_add_value = Entry(frame)
            entry_add_value.grid(row=0, column=3, sticky=W + E, padx=(20, 0))

            label_add_comment = Label(frame, text="Comment: ")
            label_add_comment.grid(row=0, column=4, sticky=W + E, padx=(20, 0))

            entry_add_comment = Entry(frame)
            entry_add_comment.grid(row=0, column=5, sticky=W + E, padx=(20, 0))

            button_add = Button(
                frame,
                text="Add",
                command=lambda: add_parameter(
                    entry_add_name.get(), entry_add_value.get()
                ),
            )
            button_add.grid(row=0, column=6, padx=(0, 20))

            label_add_min = Label(frame, text="Min: ")
            label_add_min.grid(row=1, column=0, sticky=W + E, padx=(20, 0))

            spinbox_min = Spinbox(frame, from_=0, to=10)
            spinbox_min.grid(row=1, column=1, sticky=W + E, padx=(20, 0))

            label_add_min = Label(frame, text="Max: ")
            label_add_min.grid(row=1, column=2, sticky=W + E, padx=(20, 0))

            spinbox_min = Spinbox(frame, from_=0, to=10)
            spinbox_min.grid(row=1, column=3, sticky=W + E, padx=(20, 0))

            label_add_min = Label(frame, text="Increment: ")
            label_add_min.grid(row=1, column=4, sticky=W + E, padx=(20, 0))

            spinbox_min = Spinbox(frame, from_=0, to=10)
            spinbox_min.grid(row=1, column=5, sticky=W + E, padx=(20, 0))

            button_apply = Button(
                frame,
                text="Apply",
                command=lambda: add_parameter(
                    entry_add_name.get(), entry_add_value.get()
                ),
            )
            button_apply.grid(row=1, column=6, padx=(0, 20))

            for i, _ in enumerate(parameters):
                scaleBlocks.append(
                    createScaleBlock(window, i + 1, parameters.item(i).name)
                )
                scaleBlocks[i].set(parameters.item(i).value * 10)

    if len(parameters) == len(scaleBlocks):
        for i, _ in enumerate(parameters):
            if (
                round(parameters.item(i).value, 2)
                != round(scaleBlocks[i].get() / 10, 2)
                and len(ui.activeSelections) == 0
            ):
                slider_val = scaleBlocks[i].get() / 10
                param_val = parameters.item(i)
                param_val.value = round(slider_val, 2)

    window.after(150, updateParameters)  # Runs the function again after a time


def on_closing():
    global window, isWindowOpen
    isWindowOpen = False
    window.destroy()


def externalWindow():
    """Opens and intialises an external window"""

    global parameters, scaleBlocks, window, last_num_parameters, entry_add_value

    window = Tk()
    window.title("Advanced Parameters")
    window.iconbitmap(
        os.path.dirname(os.path.abspath(__file__)) + "\\resources\\16x16.ico"
    )
    window.attributes("-topmost", True)

    last_num_parameters = None
    updateParameters()

    window.columnconfigure(1, weight=1)  # Allow widgets to expand to full width
    window.protocol("WM_DELETE_WINDOW", on_closing)

    window.mainloop()  # Starts the gui (blocking method)

    # Resets created global variables after the gui is closed
    del scaleBlocks
    del window
    del last_num_parameters
    if "entry_add_value" in globals():
        del entry_add_value
    if "parameters" in globals():
        del parameters


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


# This function will be called when the user hits the OK button in the command dialog
def command_execute(args: adsk.core.CommandEventArgs):
    global isWindowOpen

    if not isWindowOpen:
        window_process = threading.Thread(target=externalWindow)
        window_process.start()
        isWindowOpen = True
    futil.log(f"{CMD_NAME} Command Execute Event")
    # msg = f"Hello World"
    # ui.messageBox(msg)


# This function will be called when the user completes the command.
def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
    futil.log(f"{CMD_NAME} Command Destroy Event")
