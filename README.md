<img align="left" width="70" height="70" src="/commands/AdvancedParameters/resources/64x64.png" alt="Advanced Parameters">

# Advanced Parameters

An add-in for Autodesk Fusion 360 that provides advanced parameter options to help with prototyping.

## Features

![Toolbar](/commands/AdvancedParameters/resources/toolbar.png "Toolbar")
<img align="right" width="480" src="/commands/AdvancedParameters/resources/window_demo.png" alt="Window Demo">

- Slider bars to intuitively adjust user parameters (click, drag or scroll)
- Add, remove or update user parameters
- Automatic syncing of parameters between the workspace and the add-in window
- Automatic adjustment of min/max/increment of sliders based existing/new parameters
- The window stays open and updates while sketches are edited or if designs are switched/opened
- The window stays on top of other windows
- Parameters can be changed in the **Render** workspace
- Comments and expressions are supported
- No dependencies apart from Fusion 360 are required for this add-in to work

## Compatibility

Tested on:

| #   | Operating System                 | Fusion 360 Version | Advanced Parameters Version(s) |
| :-- | :------------------------------- | :----------------- | :----------------------------- |
| 1   | Windows 10 Pro 22H2 (19045.2604) | 2.0.15509 x86_64   | 1.1                            |
| 2   | Windows 10 Pro 22H2 (19045.2846) | 2.0.16009 x86_64   | 1.1, 1.2                       |

## Installation

1. Download the [source code from the latest release](https://github.com/daniel-page/advanced-parameters/archive/refs/tags/v1.2.zip) and extract the archive
2. To permanently install the add-in copy its INNER directory containing the source code to `C:\Users\%Username%\AppData\Roaming\Autodesk\Autodesk Fusion 360\API\AddIns`
3. OR to open it from its existing location go to **UTILITIES** toolbar tab > **ADD-INS** > **Add-Ins** tab > Green **+** button and locate the INNER directory containing the source code

## Running

1. Go to **UTILITIES** toolbar tab > **ADD-INS** > **Add-Ins** tab
2. Click **Advanced Parameters** in the list to highlight
3. Select **Run on Startup** (Optional)
4. Click **Run**
5. Go to the **SOLID** toolbar tab
6. Click on the red **fx** icon in the **MODIFY** panel
7. A window will load

## Using the Add-in

- Use the top toolbar to add a parameter, update a parameter or change slider settings
- Existing parameters can be updated by entries in the toolbar followed by clicking **Update**
- Drag a slider left/right, use a mouse scroll wheel or click left/right of the slider to change the value
- Click **Delete** to remove a parameter (this will only work if the parameter is not used in the workspace)

### Tips

- Expressions can be used as value input
- Other parameters can be used in expressions
- Hold down the **Shift** key to stop a slider syncing with the workspace while it is changed
- Press the **Enter** key with a text entry field selected to submit it
- To remove a comment enter a space character in the comment entry field and click **Update**
- Negative values are possible
- A mouse scroll wheel can be used to change slider settings
- The default unit is millimetres. To create a degrees slider add "deg" to the end of entered values

### Limitations

- At this stage only millimetres and degrees are supported
- Complex designs will slow down the responsiveness of the slider. For these, it is recommended to pause syncing by holding down the **Shift** key while a slider is moved or entering sketches so the whole model does not need to be updated for every change.
- Parameters cannot be updated while anything in the workspace is selected
- Parameters in the workspace will not update when the Fusion 360 parameters window is open (until it is closed)
- This add-in only works up to five decimal places
- Changing the increment can change the slider value(s) to the nearest increment multiple
