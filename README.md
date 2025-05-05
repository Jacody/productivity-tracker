# Productivity Tracker

A comprehensive tool to boost your productivity with todo list management, time tracking, and Google Calendar integration. Optionally includes face recognition to ensure you're actually working on your tasks.



![Bildschirmfoto 2025-05-05 um 11 03 49](https://github.com/user-attachments/assets/6846de5f-545c-4d36-9d70-62b5fdbdbc55)




## Main Features

- **Todo Manager**: Manage and organize your tasks with main and subtasks
- **Time Tracking**: Precisely track how much time you spend on each task
- **Google Calendar Integration**: Automatically import calendar events as tasks
- **CSV Export**: Export your time data for further analysis
- **Face Recognition** (optional): Monitors whether you're actually working at your computer
- **Data Visualization**: Analyze your productivity patterns with charts and diagrams

## System Requirements

- Python 3.8 or higher
- macOS (primarily tested) / Windows / Linux
- Webcam (for the face recognition feature)

## Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/Jacody/productivity-tracker.git
   cd productivity-tracker
   ```

2. **Set up Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up Google Calendar API (optional)**
   
   For Google Calendar integration:
   
   a. Visit the [Google Cloud Console](https://console.cloud.google.com/)
   b. Create a new project
   c. Enable the Google Calendar API:
      - Navigate to "APIs & Services" > "Library"
      - Search for "Google Calendar API" and enable it
   d. Create OAuth 2.0 credentials:
      - Go to "APIs & Services" > "Credentials"
      - Click on "Create credentials" > "OAuth client ID"
      - Select "Desktop application" as the application type
      - Enter a name for the credentials
   e. Download the JSON file with the credentials
   f. Save the file as `src/credentials.json`

   **IMPORTANT: Never add your `credentials.json` to the Git repository!**

## Starting the Application

### Standard Todo Manager
```bash
python src/todo_manager.py
```

### Todo Manager with Google Calendar Integration
```bash
python src/todo_manager_calendar.py
```

### Productivity Tracker with Face Recognition
```bash
python src/tracker.py
```

### Visualization of Productivity Data
```bash
python src/visualization.py
```

## Launcher Scripts

This project contains various scripts to make starting the Productivity Tracker easier:

- `productivity_launcher.py`: Main launch script
- `launch_productivity_tracker.sh`: Shell script to start the application
- Various scripts for creating desktop shortcuts and app bundles for macOS

## Project Structure

- `src/`: Application source code
  - `todo_manager.py`: Main component for todo management
  - `tracker.py`: Implementation of face recognition and time tracking
  - `google_calendar_integration.py`: Google Calendar API integration
  - `data_processing.py`: Processing and analysis of productivity data
  - `visualization.py`: Graphical representation of productivity data
- `data/`: Storage location for exported CSV files and other data
- `sounds/`: Audio files for notifications

## Security Notes

- **Credentials**: The `credentials.json` and `token.pickle` contain sensitive data and are excluded in `.gitignore`. Never share these files publicly.
- **Face Recognition**: All face recognition data is processed locally and not sent to external servers.
- **Privacy**: The application stores all data locally on your device.

## Troubleshooting

- **Camera Issues**: If the camera doesn't work, restart your computer or use the `camera_reset.sh` script
- **Google Calendar Problems**: Make sure your credentials are current and renew them if necessary

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions to the project are welcome! Please make sure not to include any sensitive data in your pull requests.
