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

    button_update = Button(window, text="Update")
    button_update.grid(row=row_number, column=5, pady=(17, 0), padx=(0, 20))

    return slider


def add_parameter(name, value):
    """Adds a user parameter"""

    global parameters

    parameters.add(name, adsk.core.ValueInput.createByString(value), "mm", "")


def focus_on(_):
    """GUI focus state changed to True"""

    global gui_in_focus

    gui_in_focus = True


def focus_off(_):
    """GUI focus state changed to False"""

    global gui_in_focus

    gui_in_focus = False


def updateParameters():
    """Syncs parameters between the Fusion360 workspace and the external window GUI"""

    global scaleBlocks, parameters, window, last_num_parameters, gui_in_focus

    # Checks if there is a change in the number of parameters
    if last_num_parameters != len(parameters):
        last_num_parameters = len(parameters)

        for l in window.grid_slaves():
            l.destroy()

        scaleBlocks = []

        for i, _ in enumerate(parameters):
            scaleBlocks.append(createScaleBlock(window, i, parameters.item(i).name))
            scaleBlocks[i].set(parameters.item(i).value * 10)

        label_add_name = Label(window, text="Name: ")
        label_add_name.grid(row=i + 1, column=0, sticky=W + E, padx=(20, 0))

        entry_add_name = Entry(window)
        entry_add_name.grid(row=i + 1, column=1, sticky=W + E, padx=(20, 0))

        label_add_value = Label(window, text="Value: ")
        label_add_value.grid(row=i + 1, column=2, sticky=W + E, padx=(20, 0))

        entry_add_value = Entry(window)
        entry_add_value.grid(row=i + 1, column=3, sticky=W + E, padx=(20, 0))

        button_add = Button(
            window,
            text="Add",
            command=lambda: add_parameter(entry_add_name.get(), entry_add_value.get()),
        )
        button_add.grid(row=i + 1, column=5, padx=(0, 20))

    if len(parameters) == len(scaleBlocks) > 0 and gui_in_focus:
        for i, _ in enumerate(parameters):
            parameters.item(i).value = scaleBlocks[i].get() / 10

    window.after(100, updateParameters)  # Runs the function again after 100ms


def externalWindow():
    """Opens and intialises an external window"""

    global parameters, scaleBlocks, window, last_num_parameters, gui_in_focus

    window = Tk()
    window.title("Advanced Parameters")
    window.iconbitmap(
        os.path.dirname(os.path.abspath(__file__)) + "\\resources\\16x16.ico"
    )

    # Mouse position monitored to prevent conflicts occuring if dimensions/parameters are changed in the Fusion360 workspace
    gui_in_focus = False
    window.bind("<Enter>", focus_on)  # Mouse enters the gui
    window.bind("<Leave>", focus_off)  # Mouse exits the gui

    last_num_parameters = None
    if len(parameters) > 0:
        updateParameters()

    window.columnconfigure(1, weight=1)  # Allow widgets to expand to full width

    window.mainloop()  # Starts the gui (blocking method)

    del scaleBlocks  # Resets the sliders when gui closed
    del window  # Resets tkinter global instance


# Executed when add-in is run.
def start():

    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)

    # if not design:
    #     ui.messageBox("A Fusion design must be active when invoking this command.")
    #     return ()

    global parameters

    parameters = design.userParameters

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
    window_process = threading.Thread(target=externalWindow)
    window_process.start()
    futil.log(f"{CMD_NAME} Command Execute Event")
    # msg = f"Hello World"
    # ui.messageBox(msg)


# This function will be called when the user completes the command.
def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
    futil.log(f"{CMD_NAME} Command Destroy Event")
