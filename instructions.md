# Run8 Industry Tool - Instructions

## Overview
This tool allows you to view and edit Run8 Train Simulator industry configuration files (.ind).

## Getting Started

### **Important**: Always back up your original files before making changes! ###
### Opening a File
1. Go to **File → Open** (or press Ctrl+O)
2. Navigate to the specific Run8 Regions directory (ex: \Content\V3Routes\Regions\SouthernCA)
3. Select an industry configuration file (typically "Config.ind")
4. The main window will display all industries in the file

## Viewing and Editing Industries

### Main Window
The main window displays a table with the following columns:
- **Name**: Industry name
- **Tag**: Track symbol/identifier
- **Local Name**: Symbol for local which services this industry
- **# Tracks Nodes**: Number of track nodes
- **Incoming cars**: Number of producer configurations
- **Process in Blocks**: Whether the industry processes cars in blocks
#### Find/replace:
In the lower right corner of the main window there is a `find` button. This will bring up a dialog allowing you to search / replace strings in the industry symbol, local name, and processed tag fields.

### Editing an Industry
1. **Double-click** any row in the table to open the detail dialog
2. In the detail dialog, you can edit:
   - Basic information (name, local name, symbol)
   - Track assignments
   - Producer configurations (car types, hours, capacity, tags)
3. Click **Update** to keep changes or **Cancel** to discard

### Track Management
- **Remove Selected Track**: Select a track row and click this button to remove it
- Track fields: Route Prefix, Track Section, Track Direction

### Producer Management
- View car type information (read-only)
- Edit whether the producer creates Empties or Loads
- Adjust processing hours and capacity
- Modify processed tags (enter using spaces or commas as separators)

#### Find/replace:
In the lower right corner of the industry window there is a `find` button. This will bring up a dialog allowing you to search / replace strings in the processed tag fields of the particular industry.

## Saving Changes

### Save File
- Go to **File → Save** to overwrite the file originally loaded.
- Use **File → Save As...** to create a new file.
- *Note*: If overwriting the original file, you'll be prompted to confirm



