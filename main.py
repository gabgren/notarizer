import os
import zipfile
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.metrics import sp, dp

label = None
log = None
keychain_profile = ""
keychain_profile_save = os.path.join(os.path.expanduser("~"), ".cache", "notarizer_saved_profile")

def zip_directory(folder_path, output_filename):
    parent_dir = os.path.dirname(folder_path)
    basename = os.path.basename(folder_path)
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        os.chdir(parent_dir)        
        for foldername, subfolders, filenames in os.walk(basename):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zipf.write(file_path)
                
class DropTarget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.size = (300, 300)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        Window.bind(on_drop_file=self._on_drop_file)

    def _on_drop_file(self, window, file_path, x, y):
        file_path = file_path.decode('utf-8')
        print("File dropped: " + file_path)
        if os.path.exists(file_path):
            self.zip_file(file_path)

    def zip_file(self, file_path):
        global label
        with open(keychain_profile_save, "w") as f:
            f.write(keychain_profile.text)
        label.text = "Zipping..."
        zipped_path = file_path + ".zip"
        # remove zip if it already exists
        if os.path.exists(zipped_path):
            os.remove(zipped_path)
        # zip the app
        zip_directory(file_path, zipped_path)
        print(f"Zipped {file_path} to {zipped_path}")
        self.notarize_file(zipped_path)
    
    def notarize_file(self, file_path):
        global label, log
        label.text = "Notarizing..."
        command = f"xcrun notarytool submit --keychain-profile {keychain_profile.text} --wait \"{file_path}\""
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, text=True)

        valid = True  # Assume the process is valid to start
        submission_id = None  # To capture the ID
        result = ""  # To capture the result
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # Print line in real-time
            if "id:" in line:
                submission_id = line.split("id:")[1].strip()  # Extract and store the ID
            if "status: Invalid" in line:
                valid = False  # Update the validity flag if "status: Invalid" is found
            result += line + "\n"

        process.stdout.close()
        return_code = process.wait()

        if return_code != 0:
            label.text = "Notarization failed"
            log.text = result
            log.opacity = 1
        elif not valid:
            command = f"xcrun notarytool log {submission_id} --keychain-profile {keychain_profile.text}"
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True).strip()
            label.text = "Notarization failed"
            log.text = result
            log.opacity = 1
        else:
            print(f"Notarization was successful! Submission ID: {submission_id}")
            self.staple_file(file_path)

    def staple_file(self, file_path):
        global label, log
        label.text = "Stapling..."
        file_path = file_path.replace(".zip", "")
        command = f"xcrun stapler staple \"{file_path}\""
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True).strip()
        label.text = "Result:"
        log.text = result
        log.opacity = 1
        


class MyApp(App):
    def build(self):
        global label, keychain_profile, log
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        label = Label(text="Drag and drop a file here to zip it!")
        layout.add_widget(label)
                
        layout.add_widget(Widget(size_hint=(1, None), height=40))
        
        hbox = BoxLayout(orientation='horizontal', spacing=10, padding=10, size_hint_y=None, height=dp(40))
        hbox.add_widget(Label(text="Keychain profile:", size_hint=(None, 1), width=250))
        
        # look in user's cache dir if they have a keychain profile saved
        # if they do, use that as the default value
        keychain_profile_name = "default"
        if os.path.exists(keychain_profile_save):
            with open(keychain_profile_save, "r") as f:
                keychain_profile_name = f.read()
        keychain_profile = TextInput(text=keychain_profile_name)
        hbox.add_widget(keychain_profile)
        
        layout.add_widget(hbox)
        
        log = TextInput(text="", readonly=True, opacity=0)
        layout.add_widget(log)

        drop_target = DropTarget()
        layout.add_widget(drop_target)

        return layout


if __name__ == '__main__':
    MyApp().run()
