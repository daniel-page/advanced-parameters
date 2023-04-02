import adsk.core
import adsk.fusion
import os
from ... import config
from ...lib import fusion360utils as futil
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading
import traceback

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


def addParameter(name, value, comment):
    """Adds a user parameter"""

    global parameters

    try:
        if len(ui.activeSelections) == 0:
            parameters.add(
                name, adsk.core.ValueInput.createByString(value), "mm", comment
            )
        else:
            messagebox.showwarning(
                "Warning", "Cannot update with selections in the workspace."
            )
    except RuntimeError as err:
        messagebox.showwarning("Runtime Error", err)


def deleteParameter(row_number):
    """Removes a user parameter"""

    global parameters

    delete_succesful = parameters[row_number].deleteMe()

    if not delete_succesful:
        messagebox.showinfo(
            "Info",
            "Deletion of this parameter was unsuccessful. This is likely due to it being used in the workspace.",
        )


def updateParameter(row_number, slider, comment, name):
    """Update the value/comment/name of a parameter"""

    global scaleBlocks, parameters, entry_add_value, entry_add_comment
    global entry_add_name, spinbox_max, spinbox_min, spinbox_min_value, spinbox_max_value

    comment_input = entry_add_comment.get()
    if comment_input == " ":
        scaleBlocks[row_number][3].grid_remove()
    elif len(comment_input) > 0:
        comment.configure(text=comment_input)
        parameters[row_number].comment = comment_input
        scaleBlocks[row_number][3].grid(
            row=1,
            column=0,
            sticky=W,
            pady=(0, 0),
            padx=(0, 0),
            columnspan=10,
        )

    name_input = entry_add_name.get()
    if len(name_input) > 0:
        name.configure(text=name_input)
        parameters[row_number].name = name_input

    value_input = entry_add_value.get()
    if len(value_input) > 0:
        try:
            if len(ui.activeSelections) == 0:
                parameters.item(row_number).expression = value_input

                if parameters.item(row_number).value > float(spinbox_max.get()):
                    spinbox_max.delete(0, 20)
                    spinbox_max.insert(0, parameters.item(row_number).value)
                    spinbox_max_value = parameters.item(row_number).value
                    updateSettings()
                elif parameters.item(row_number).value < float(spinbox_min.get()):
                    spinbox_min.delete(0, 20)
                    spinbox_min.insert(0, parameters.item(row_number).value)
                    spinbox_min_value = parameters.item(row_number).value
                    updateSettings()

                slider.set(parameters.item(row_number).value * 10)
            else:
                messagebox.showwarning(
                    "Warning", "Cannot update with selections in the workspace."
                )

        except NameError as err:
            messagebox.showwarning("Name Error", err)
        except TypeError as err:
            messagebox.showwarning("Type Error", err)


def updateSettings():
    """Updates window to reflect changed settings"""

    global scaleBlocks, spinbox_min, spinbox_max, spinbox_increment, spinbox_min_value, spinbox_max_value, spinbox_increment_value

    try:
        if (
            scaleBlocks != None
            and spinbox_min != None
            and spinbox_max != None
            and spinbox_increment != None
        ):
            spinbox_min.configure(increment=float(spinbox_increment.get()))
            spinbox_max.configure(increment=float(spinbox_increment.get()))

            for row_number, _ in enumerate(scaleBlocks):
                scaleBlocks[row_number][0].configure(
                    from_=float(spinbox_min.get()),
                    to=float(spinbox_max.get()),
                    resolution=float(spinbox_increment.get()),
                )
                spinbox_increment_value = float(spinbox_increment.get())
                scaleBlocks[row_number][1].configure(
                    text="%g" % (float(spinbox_min.get()))
                )
                spinbox_min_value = float(spinbox_min.get())
                scaleBlocks[row_number][2].configure(
                    text="%g" % (float(spinbox_max.get()))
                )
                spinbox_max_value = float(spinbox_max.get())

    except ValueError as err:
        messagebox.showwarning("Value Error", err)


def queueSettingsUpdate():
    """Queues an update for min/min/increment settings in the mainloop"""

    global is_settings_update

    is_settings_update = True


def sliderMoved(row_number):
    """Records whether a slider is moved by the user"""

    global sliders_moved

    sliders_moved[row_number] = True  # Records whether a slider has been moved


def createScaleBlock(row_number):
    """Generates a row of information and controls for a parameter"""

    global parameters, entry_add_value, spinbox_min, spinbox_max, spinbox_increment, window_bottom

    length_details = Frame(window_bottom)
    length_details.grid(
        row=row_number, column=0, sticky=W, pady=(17, 0), padx=(0, 20), columnspan=10
    )
    length_label = Label(
        length_details, text=parameters.item(row_number).name, width=8, anchor="w"
    )
    length_label.grid(
        row=0, column=0, sticky=W, pady=(0, 0), padx=(0, 0), columnspan=10
    )

    comment_label = Label(
        length_details,
        text=parameters.item(row_number).comment,
        font=("Arial", 7),
        width=8,
        state="disabled",
        anchor="w",
    )

    # Only show comment if one exists
    if len(parameters.item(row_number).comment) > 0:
        comment_label.grid(
            row=1,
            column=0,
            sticky=W,
            pady=(0, 0),
            padx=(0, 0),
            columnspan=10,
        )

    slider_min = Label(window_bottom, text="%g" % float(spinbox_min.get()), width=4)
    slider_min.grid(row=row_number, column=10, pady=(17, 0), columnspan=10)

    slider_value = DoubleVar()
    slider = Scale(
        window_bottom,
        from_=float(spinbox_min.get()),
        to=float(spinbox_max.get()),
        resolution=float(spinbox_increment.get()),
        orient="horizontal",
        command=lambda _: sliderMoved(row_number),
        length=269,
        variable=slider_value,
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

    slider_max = Label(window_bottom, text="%g" % float(spinbox_max.get()), width=4)
    slider_max.grid(
        row=row_number, column=30, padx=(0, 17), pady=(17, 0), columnspan=10
    )

    button_delete = Button(
        window_bottom,
        text="Delete",
        width=6,
        command=lambda: deleteParameter(row_number),
    )
    button_delete.grid(
        row=row_number, column=40, pady=(17, 0), padx=(0, 20), columnspan=10
    )

    button_update = Button(
        window_bottom,
        text="Update",
        width=6,
        command=lambda: updateParameter(
            row_number, slider, comment_label, length_label
        ),
    )
    button_update.grid(
        row=row_number, column=50, pady=(17, 0), padx=(0, 0), columnspan=10
    )

    return slider, slider_min, slider_max, comment_label, slider_value


def loadToolbar():
    """Loads the toolbar with text input fields and buttons at the top of the window"""

    global entry_add_value, entry_add_name, window_top
    global spinbox_min, spinbox_max, spinbox_increment, entry_add_comment
    global spinbox_min_value, spinbox_max_value, spinbox_increment_value

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
    entry_add_value.grid(row=0, column=30, sticky=W, padx=(0, 20), columnspan=10)

    label_add_comment = Label(window_top, text="Comment: ", anchor="w")
    label_add_comment.grid(row=0, column=40, sticky=W, padx=(0, 5), columnspan=10)

    entry_add_comment = Entry(
        window_top,
        width=15,
        relief=FLAT,
        highlightbackground="grey",
        highlightthickness=1,
    )
    entry_add_comment.grid(row=0, column=50, sticky=W, padx=(0, 20), columnspan=10)

    button_add = Button(
        window_top,
        text="Add",
        width=6,
        command=lambda: addParameter(
            entry_add_name.get(),
            entry_add_value.get(),
            entry_add_comment.get(),
        ),
    )
    button_add.grid(row=0, column=60, padx=(0, 0), columnspan=10)

    spinbox_increment = ttk.Spinbox(
        window_top,
        width=12,
        command=queueSettingsUpdate,
        from_=-10000,
        to=10000,
    )
    spinbox_increment.grid(
        row=1,
        column=50,
        sticky=W,
        padx=(0, 20),
        pady=(6, 0),
        columnspan=10,
    )
    spinbox_increment.delete(0)
    spinbox_increment.insert(0, str(spinbox_increment_value))

    label_add_min = Label(window_top, text="Min: ", anchor="w")
    label_add_min.grid(
        row=1, column=0, sticky=W, padx=(0, 5), pady=(6, 0), columnspan=10
    )

    spinbox_min = ttk.Spinbox(
        window_top,
        width=12,
        command=queueSettingsUpdate,
        from_=-10000,
        to=10000,
        increment=float(spinbox_increment.get()),
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
    spinbox_min.insert(0, str(spinbox_min_value))

    label_add_max = Label(window_top, text="Max: ", anchor="w")
    label_add_max.grid(
        row=1,
        column=20,
        sticky=W,
        padx=(0, 5),
        pady=(6, 0),
        columnspan=10,
    )

    spinbox_max = ttk.Spinbox(
        window_top,
        width=12,
        command=queueSettingsUpdate,
        from_=-10000,
        to=10000,
        increment=float(spinbox_increment.get()),
    )
    spinbox_max.grid(
        row=1,
        column=30,
        sticky=W,
        padx=(0, 20),
        pady=(6, 0),
        columnspan=10,
    )
    spinbox_max.delete(0)
    spinbox_max.insert(0, str(spinbox_max_value))

    label_add_min = Label(window_top, text="Increment: ", anchor="w")
    label_add_min.grid(
        row=1,
        column=40,
        sticky=W,
        padx=(0, 5),
        pady=(6, 0),
        columnspan=10,
    )

    button_apply = Button(window_top, text="Apply", width=6, command=updateSettings)
    button_apply.grid(row=1, column=60, padx=(0, 0), pady=(6, 0), columnspan=10)


def updateWindow():
    """Syncs parameters between the Fusion360 workspace and the external window GUI"""

    global scaleBlocks, parameters, window, last_num_parameters, entry_add_value, entry_add_name
    global spinbox_min, spinbox_max, spinbox_increment, is_settings_update, entry_add_comment
    global sliders_moved, spinbox_min_value, spinbox_max_value, spinbox_increment_value, selected_flag, window_bottom

    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        parameters = design.userParameters

        if is_settings_update:
            updateSettings()
            is_settings_update = False

        # Checks if there is a change in the number of parameters
        if last_num_parameters != len(parameters):
            last_num_parameters = len(parameters)

            for widget in window_bottom.grid_slaves():
                widget.destroy()

            scaleBlocks = []

            if len(parameters) > 0:

                window_bottom.grid(
                    row=1, column=0, columnspan=70, padx=(10, 10), pady=(0, 10)
                )

                for row_number, _ in enumerate(parameters):
                    scaleBlocks.append(createScaleBlock(row_number))
                    sliders_moved.append(True)
                    scaleBlocks[row_number][0].set(
                        parameters.item(row_number).value * 10
                    )
                    param_val = parameters.item(row_number)

                    if param_val.value * 10 > float(spinbox_max.get()):
                        spinbox_max.delete(0, 20)
                        spinbox_max.insert(0, "%g" % (param_val.value * 10))
                        spinbox_max_value = param_val.value * 10
                        updateSettings()
                        scaleBlocks[row_number][0].set(param_val.value * 10)
                    elif param_val.value * 10 < float(spinbox_min.get()):
                        spinbox_min.delete(0, 20)
                        spinbox_min.insert(0, "%g" % (param_val.value * 10))
                        spinbox_min_value = param_val.value * 10
                        updateSettings()
                        scaleBlocks[row_number][0].set(param_val.value * 10)

        if len(parameters) == len(scaleBlocks):
            for row_number, _ in enumerate(parameters):
                if (
                    round(parameters.item(row_number).value, 5)
                    != round(scaleBlocks[row_number][0].get() / 10, 5)
                    and len(ui.activeSelections) == 0
                    and sliders_moved[row_number]
                ):
                    param_val = parameters.item(row_number)
                    slider_val = scaleBlocks[row_number][0].get() / 10
                    param_val.value = round(slider_val, 5)
                    selected_flag = False

                elif (
                    round(parameters.item(row_number).value, 5)
                    != round(scaleBlocks[row_number][0].get() / 10, 5)
                    and len(ui.activeSelections) > 0
                    and not selected_flag
                ):
                    messagebox.showwarning(
                        "Warning", "Cannot update with selections in the workspace."
                    )
                    selected_flag = True
                elif round(parameters.item(row_number).value, 5) == round(
                    scaleBlocks[row_number][0].get() / 10, 5
                ):
                    sliders_moved[row_number] = False

                elif not sliders_moved[row_number]:
                    param_val = parameters.item(row_number)
                    scaleBlocks[row_number][4].set(param_val.value * 10)

        window.after(150, updateWindow)  # Runs the function again after a time

    except RuntimeError:
        window.destroy()  # This closes the window when Fusion 360 is closed


def onClosing():
    """Window state updated and object destroyed so another instance can be opened"""

    global window, isWindowOpen

    isWindowOpen = False
    window.destroy()


def externalWindow():
    """Opens and intialises an external window"""

    try:

        global parameters, scaleBlocks, window, last_num_parameters, entry_add_value, spinbox_min_value, spinbox_max_value
        global spinbox_increment_value, selected_flag
        global spinbox_min, spinbox_max, spinbox_increment, is_settings_update, entry_add_comment, entry_add_name, sliders_moved
        global window_top, window_bottom

        # Default values for global variables
        entry_add_value = None
        spinbox_max = None
        spinbox_min = None
        spinbox_increment = None
        parameters = None
        scaleBlocks = None
        is_settings_update = False
        entry_add_comment = None
        entry_add_name = None
        sliders_moved = []
        spinbox_min_value = 0
        spinbox_max_value = 1000
        spinbox_increment_value = 1
        selected_flag = False
        last_num_parameters = None

        window = Tk()
        window_top = Frame(window)
        window_bottom = Frame(window)

        window.title("Advanced Parameters")
        window.iconbitmap(
            os.path.dirname(os.path.abspath(__file__)) + "\\resources\\16x16.ico"
        )
        window.resizable(width=False, height=False)
        window.attributes("-topmost", True)
        window.protocol("WM_DELETE_WINDOW", onClosing)

        loadToolbar()

        updateWindow()

        window.mainloop()  # Starts the gui (blocking method)

        # Resets created global variables after the gui is closed
        del (
            scaleBlocks,
            window,
            last_num_parameters,
            entry_add_value,
            parameters,
            spinbox_min,
            spinbox_max,
            spinbox_increment,
            is_settings_update,
            entry_add_comment,
            entry_add_name,
            sliders_moved,
            spinbox_min_value,
            spinbox_max_value,
            spinbox_increment_value,
            selected_flag,
            window_top,
            window_bottom,
        )

    except:
        messagebox.showerror("Error", traceback.format_exc())


# Executed when add-in is run.
def start():

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
