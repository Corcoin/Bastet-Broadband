import requests
import time
import socket
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock

DDNS_SERVER = "http://192.168.1.229:5000"  # Replace with the actual server IP
HOSTNAME = socket.gethostname()  # Use the device's hostname for identification

class DDNSUpdaterApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.label = Label(text="Bastet Broadband DDNS Updater", font_size=24)
        self.layout.add_widget(self.label)

        self.status_label = Label(text="", font_size=14)
        self.layout.add_widget(self.status_label)

        self.start_button = Button(text="Start Updating", on_press=self.start_updating)
        self.layout.add_widget(self.start_button)

        self.stop_button = Button(text="Stop Updating", on_press=self.stop_updating, disabled=True)
        self.layout.add_widget(self.stop_button)

        self.updating = False
        self.thread = None

        return self.layout

    def get_external_ip(self):
        """Function to get the current external IP address."""
        try:
            response = requests.get('https://api.ipify.org?format=json')
            return response.json().get('ip')
        except Exception as e:
            self.update_status(f"Error getting external IP: {e}")
            return None

    def update_ddns(self, ip):
        """Function to update the DDNS server with the current IP address."""
        try:
            data = {'hostname': HOSTNAME, 'ip': ip}
            response = requests.post(f"{DDNS_SERVER}/update", json=data)
            if response.status_code == 200:
                self.update_status(f"IP updated successfully to {ip}")
            else:
                self.update_status(f"Failed to update IP: {response.status_code}")
        except Exception as e:
            self.update_status(f"Error updating DDNS server: {e}")

    def update_status(self, message):
        """Update the status label in the GUI."""
        self.status_label.text = message

    def update_loop(self, dt):
        """Loop to check for IP updates."""
        if self.updating:
            current_ip = self.get_external_ip()
            if current_ip:
                if not hasattr(self, 'last_ip') or current_ip != self.last_ip:
                    self.update_ddns(current_ip)
                    self.last_ip = current_ip
            Clock.schedule_once(self.update_loop, 300)  # Check every 5 minutes

    def start_updating(self, instance):
        """Start the updating process."""
        self.updating = True
        self.update_status("Updating started...")
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.update_loop(0)  # Start the update loop

    def stop_updating(self, instance):
        """Stop the updating process."""
        self.updating = False
        self.update_status("Updating stopped.")
        self.start_button.disabled = False
        self.stop_button.disabled = True

if __name__ == "__main__":
    DDNSUpdaterApp().run()
