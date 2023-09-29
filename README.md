<img width="804" alt="Screenshot 2023-09-28 at 10 14 59 PM" src="https://github.com/gabgren/notarizer/assets/1724721/505ede5c-24c4-48f4-91c7-1fa1172583f2">

# Notatizer

Simple tool to notarize a software by drag and drop

### Contribution

This tool is very simple and can be improved, and the UI is not very nice. PRs are welcome :) 


## Installation

The UI is made with Kivy, so:
`pip install kivy`

## Usage

1. First, you will need to create a certificate with Apple. Then, save your profile using `xcrun notarytool store-credentials`

2. When needed, run the tool with:
`python main.py`

3. Enter your profile name (same name you used in step 1). This profile name will be saved locally for the next run

4. Drag your .app, .bundle or .plugin file. The tool will zip, notarize, and staple it. If something goes wrong, you will see it in the log.
