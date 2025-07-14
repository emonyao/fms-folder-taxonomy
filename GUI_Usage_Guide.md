# FMS Folder Taxonomy - GUI Usage Guide

## Overview

FMS Folder Taxonomy is a graphical tool for image renaming that provides a user-friendly interface for managing standardized naming of image files.

## Installation and Running

### Method 1: Direct Run (Requires Python Environment)

1. **Install Python Dependencies**
   ```bash
   # Double-click to run
   install_dependencies.bat
   
   # Or run via command line
   python install_dependencies.py
   ```

2. **Launch GUI**
   ```bash
   # Double-click to run
   run_gui.bat
   
   # Or run via command line
   python run_gui.py
   ```

### Method 2: Package as exe File

1. **Install Dependencies**
   ```bash
   python install_dependencies.py
   ```

2. **Package exe**
   ```bash
   python build_exe.py
   ```

3. **Run exe**
   - After packaging, the exe file is located at `dist/FMS_Folder_Taxonomy.exe`
   - Release package is located in the `release/` directory

## Interface Features

### Main Operation Tabs

#### Directory Settings
- **Input Directory**: Select the folder containing original images
- **Output Directory**: Select the location to save renamed images

#### Operation Buttons
- **Scan Images**: Scan image files in the input directory
- **Preview Rename**: Preview rename effects (without actually renaming)
- **Start Rename**: Execute the actual rename operation
- **Open Output Directory**: Open output directory in file explorer

#### Progress Display
- Progress bar shows current operation progress
- Operation log displays processing in real-time

### Configuration Tab

#### Directory Configuration
- **DNU Output Directory**: Output directory for unpublished images
- **Review Output Directory**: Output directory for images requiring review
- **Log File**: Location to save operation logs

#### AI Configuration
- **Enable AI Fallback**: Whether to enable AI assistance
- **AI Confidence Threshold**: Confidence threshold for AI recognition
- **AI Source**: Select the AI model to use

#### Version Configuration
- **Default Version**: Starting version number
- **Version Format**: Naming format for version numbers

### Log Tab

- **Refresh Log**: Reload log file
- **Clear Log**: Clear current log
- **Export Log**: Export log to file

## Usage Process

### 1. Preparation
1. Ensure there are image files in the input directory
2. Check if configuration file settings are correct

### 2. Scan Images
1. Click the "Scan Images" button
2. View scan results and number of images found

### 3. Preview Rename
1. Click the "Preview Rename" button
2. View rename effects and confirm they are correct

### 4. Execute Rename
1. Click the "Start Rename" button
2. Wait for processing to complete
3. View rename results in the output directory

### 5. View Logs
1. Switch to the "Log" tab
2. View detailed operation records

## Important Notes

### Safety Reminders
- **Rename operations are irreversible**, it's recommended to use the preview function first
- It's recommended to backup important files before processing
- Ensure sufficient disk space is available

### Performance Optimization
- Please be patient when processing large numbers of files
- Large batches of files can be processed in smaller groups
- Close unnecessary programs to free up memory

### Troubleshooting
- If the program cannot start, check the Python environment
- If dependency installation fails, try manual installation
- Check log files for detailed error information

## Frequently Asked Questions

### Q: What should I do if the program fails to start?
A: Check if Python 3.7+ is installed, and run `install_dependencies.bat` to install dependencies.

### Q: Can't scan image files?
A: Check if the input directory path is correct, ensure there are image files (jpg, png, etc.) in the directory.

### Q: Rename failed?
A: Check if the output directory has write permissions, view logs for specific errors.

### Q: How to recover accidentally deleted files?
A: Rename operations do not delete files, they only rename them. If files are missing, please check the output directory.

## Technical Support

If you encounter issues, please:
1. Check log files for detailed error information
2. Verify configuration file settings
3. Contact technical support and provide error information

## Update Log

### v1.0.0
- Initial version release
- Support for basic image renaming functionality
- Provides graphical interface
- Support for exe packaging 