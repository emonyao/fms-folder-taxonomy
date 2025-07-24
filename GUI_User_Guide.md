# FMS Folder Taxonomy - GUI User Guide

## Overview

FMS Folder Taxonomy is a graphical tool for image renaming, providing a user-friendly interface to manage standardized naming of image files.

## Installation and Running

### Method 1: Direct Run (Python environment required)

1. **Install Python dependencies**
   ```bash
   # Double-click to run
   install_dependencies.bat
   
   # Or run in command line
   python install_dependencies.py
   ```

2. **Start GUI**
   ```bash
   # Double-click to run
   run_gui.bat
   
   # Or run in command line
   python run_gui.py
   ```

### Method 2: Package as exe file

1. **Install dependencies**
   ```bash
   python install_dependencies.py
   ```

2. **Package exe**
   ```bash
   python build_exe.py
   ```

3. **Run exe**
   - After packaging, the exe file is located at `dist/FMS_Folder_Taxonomy.exe`
   - The release package is in the `release/` directory

## Interface Functions

### Main Operation Tab

#### Directory Settings
- **Input Directory**: Select the folder containing the original images
- **Output Directory**: Select the location to save the renamed images

#### Operation Buttons
- **Scan Images**: Scan image files in the input directory
- **Preview Rename**: Preview the renaming effect (without actual renaming)
- **Start Rename**: Perform the actual renaming operation
- **Open Output Directory**: Open the output directory in the file manager

#### Progress Display
- The progress bar shows the progress of the current operation
- The operation log displays the processing in real time

### Configuration Tab

#### Directory Configuration
- **DNU Output Directory**: Output directory for unpublished images
- **Review Output Directory**: Output directory for images that need review
- **Log File**: Location to save the operation log

#### AI Configuration
- **Enable AI fallback**: Whether to enable AI assistance
- **AI Confidence Threshold**: Confidence threshold for AI recognition
- **AI Source**: Select the AI model to use

#### Version Configuration
- **Default Version**: Starting version number
- **Version Format**: Naming format of the version number

### Log Tab

- **Refresh Log**: Reload the log file
- **Clear Log**: Clear the current log
- **Export Log**: Export the log to a file

## Usage Process

### 1. Preparation
1. Make sure there are image files in the input directory
2. Check if the configuration file settings are correct

### 2. Scan Images
1. Click the "Scan Images" button
2. View the scan results and the number of images found

### 3. Preview Rename
1. Click the "Preview Rename" button
2. View the renaming effect and confirm it is correct

### 4. Execute Rename
1. Click the "Start Rename" button
2. Wait for the process to complete
3. View the renamed results in the output directory

### 5. View Log
1. Switch to the "Log" tab
2. View detailed operation records

## Notes

### Safety Reminder
- **Renaming operation is irreversible**, it is recommended to use the preview function first
- It is recommended to back up important files before processing
- Make sure there is enough disk space

### Performance Optimization
- Please be patient when processing a large number of files
- You can process a large number of files in batches
- Close unnecessary programs to free up memory

### Troubleshooting
- If the program cannot start, check the Python environment
- If dependency installation fails, try installing manually
- Check the log file for detailed error information

## FAQ

### Q: What should I do if the program fails to start?
A: Check if Python 3.7+ is installed and run `install_dependencies.bat` to install dependencies.

### Q: Can't scan image files?
A: Check if the input directory path is correct and make sure there are image files (jpg, png, etc.) in the directory.

### Q: Rename failed?
A: Check if the output directory has write permission and check the log for specific errors.

### Q: How to recover accidentally deleted files?
A: The renaming operation does not delete files, it only renames them. If files are missing, please check the output directory.

## Technical Support

If you encounter problems, please:
1. Check the log file for error details
2. Check the configuration file settings
3. Contact technical support and provide error information

## Changelog

### v1.0.0
- Initial version released
- Supports basic image renaming function
- Provides graphical interface
- Supports exe packaging 