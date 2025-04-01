import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import psutil
from scapy.all import ARP, Ether, srp, sniff, IP
import socket
import time
from threading import Thread
import logging
import csv
import queue
import json

# Configure logging
logging.basicConfig(filename='network_monitor.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variables
device_list = []
blocked_ips = []
known_devices = {}
log_queue = queue.Queue()
refresh_rate = 30000  # Default refresh rate in milliseconds
interface_to_monitor = None  # Selected network interface
network_range = '192.168.1.0/24'  # Default network range
device_mac_prefixes = {
    "Router": ["00:1A:2B", "00:1C:3D"],
    "Printer": ["00:1E:4F"],
    "Computer": ["00:1F:5A"],
}

# Function to get available network interfaces
def get_network_interfaces():
    return [iface for iface in psutil.net_if_addrs().keys() if psutil.net_if_stats()[iface].isup]

# Function to get connected devices using ARP
def get_connected_devices():
    global device_list
    device_list.clear()
    seen_ips = set()
    
    try:
        for interface in get_network_interfaces():
            if interface == interface_to_monitor or interface_to_monitor is None:
                arp = ARP(pdst=network_range)
                ether = Ether(dst='ff:ff:ff:ff:ff:ff')
                packet = ether / arp
                result = srp(packet, timeout=2, verbose=False)[0]

                for sent, received in result:
                    if received.psrc not in seen_ips:
                        seen_ips.add(received.psrc)
                        device_info = {
                            'ip': received.psrc,
                            'mac': received.hwsrc,
                            'interface': interface,
                            'status': 'Online',
                            'type': identify_device_type(received.hwsrc),
                            'hostname': get_hostname(received.psrc),
                            'last_seen': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            'connection_type': "Ethernet" if interface.startswith("eth") else "Wi-Fi"
                        }
                        device_list.append(device_info)
                        logging.info(f"Device found: {device_info}")
                        check_device_authentication(received.hwsrc)

                log_message(f"Total devices detected: {len(device_list)}")
    except Exception as e:
        logging.error(f"Error getting connected devices: {e}")
        show_notification(f"Error getting connected devices: {e}")

def identify_device_type(mac):
    for device_type, prefixes in device_mac_prefixes.items():
        if any(mac.startswith(prefix) for prefix in prefixes):
            return device_type
    return "Unknown Device"

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Unknown"

def check_device_authentication(mac):
    if mac not in known_devices:
        log_message(f"Warning: Unknown device detected: {mac}")
        show_notification(f"Unknown device detected: {mac}")

def update_device_list():
    while True:
        get_connected_devices()
        refresh_device_list()
        time.sleep(refresh_rate / 1000)  # Convert milliseconds to seconds

def refresh_device_list():
    for row in tree.get_children():
        tree.delete(row)

    for device in device_list:
        tree.insert("", "end", values=(device['ip'], device['mac'], device['hostname'], device['type'], device['status'], device['last_seen'], device['connection_type']))

def log_message(message):
    log_queue.put(message)

def process_log_queue():
    while not log_queue.empty():
        message = log_queue.get()
        log_area.insert(tk.END, message + "\n")
        log_area.see(tk.END)
    root.after(100, process_log_queue)

def export_log():
    with open("network_monitor_log.txt", "w") as f:
        f.write(log_area.get("1.0", tk.END))
    log_message("Log exported to network_monitor_log.txt")

def export_device_list(format='csv'):
    filename = f"device_list.{format}"
    with open(filename, "w", newline='') as f:
        if format == 'csv':
            writer = csv.writer(f)
            writer.writerow(["IP Address", "MAC Address", "Hostname", "Device Type", "Status", "Last Seen", "Connection Type"])
            for device in device_list:
                writer.writerow([device['ip'], device['mac'], device['hostname'], device['type'], device['status'], device['last_seen'], device['connection_type']])
        elif format == 'json':
            json.dump(device_list, f, indent=4)
    log_message(f"Device list exported to {filename}")

def add_known_device():
    mac = simpledialog.askstring("Input", "Enter MAC Address of the known device:")
    device_type = simpledialog.askstring("Input", "Enter Device Type:")
    if mac and device_type:
        known_devices[mac] = device_type
        log_message(f"Added known device: {mac} - {device_type}")

def block_ip():
    selected_item = tree.selection()
    if selected_item:
        ip_to_block = tree.item(selected_item)['values'][0]
        if ip_to_block not in blocked_ips:
            blocked_ips.append(ip_to_block)
            log_message(f"Blocked IP: {ip_to_block}")
            refresh_device_list()

def unblock_ip():
    selected_item = tree.selection()
    if selected_item:
        ip_to_unblock = tree.item(selected_item)['values'][0]
        if ip_to_unblock in blocked_ips:
            blocked_ips.remove(ip_to_unblock)
            log_message(f"Unblocked IP: {ip_to_unblock}")
            refresh_device_list()

def load_known_devices():
    try:
        with open("known_devices.json", "r") as f:
            global known_devices
            known_devices = json.load(f)
            log_message("Known devices loaded from configuration file.")
    except Exception as e:
        log_message(f"Error loading known devices: {e}")

def start_packet_sniffer():
    def packet_callback(packet):
        packet_info = f"Packet captured: {packet.summary()}"
        logging.info(packet_info)
        log_message(packet_info)

        if packet.haslayer(Ether):
            eth_layer = packet.getlayer(Ether)
            log_message(f"Ethernet Frame: {eth_layer.src} -> {eth_layer.dst}")

        if packet.haslayer(IP):
            ip_layer = packet.getlayer(IP)
            log_message(f"IP Packet: {ip_layer.src} -> {ip_layer.dst}")

    sniff(prn=packet_callback, store=0)

def show_device_details(device):
    details = f"IP: {device['ip']}\nMAC: {device['mac']}\nHostname: {device['hostname']}\nType: {device['type']}\nStatus: {device['status']}\nLast Seen: {device['last_seen']}\nConnection Type: {device['connection_type']}"
    detail_window = tk.Toplevel(root)
    detail_window.title("Device Details")
    detail_window.geometry("400x300")
    detail_label = tk.Label(detail_window, text=details, justify=tk.LEFT)
    detail_label.pack(pady=10)

def open_packet_sniffer():
    sniffer_window = tk.Toplevel(root)
    sniffer_window.title("Packet Sniffer")
    sniffer_window.geometry("600x400")

    start_button = tk.Button(sniffer_window, text="Start Sniffing", command=lambda: Thread(target=start_packet_sniffer, daemon=True).start())
    start_button.pack(pady=10)

    log_area_sniffer = tk.Text(sniffer_window, height=15, bg="#1E1E1E", fg="#FFFFFF", font=("Courier New", 10))
    log_area_sniffer.pack(pady=10, fill=tk.BOTH, expand=True)

    def update_sniffer_log():
        while not log_queue.empty():
            message = log_queue.get()
            log_area_sniffer.insert(tk.END, message + "\n")
            log_area_sniffer.see(tk.END)
        sniffer_window.after(100, update_sniffer_log)

    update_sniffer_log()

def search_device():
    search_term = simpledialog.askstring("Search", "Enter IP or MAC Address:")
    for row in tree.get_children():
        tree.delete(row)

    for device in device_list:
        if search_term in device['ip'] or search_term in device['mac']:
            tree.insert("", "end", values=(device['ip'], device['mac'], device['hostname'], device['type'], device['status'], device['last_seen'], device['connection_type']))

def save_user_preferences():
    preferences = {
        "refresh_rate": refresh_rate,
        "known_devices": known_devices,
        "interface_to_monitor": interface_to_monitor,
        "network_range": network_range
    }
    with open("user_preferences.json", "w") as f:
        json.dump(preferences, f, indent=4)
    log_message("User preferences saved.")

def load_user_preferences():
    try:
        with open("user_preferences.json", "r") as f:
            preferences = json.load(f)
            global refresh_rate, known_devices, interface_to_monitor, network_range
            refresh_rate = preferences.get("refresh_rate", 5000)
            known_devices = preferences.get("known_devices", {})
            interface_to_monitor = preferences.get("interface_to_monitor", None)
            network_range = preferences.get("network_range", '192.168.1.0/24')
            log_message("User preferences loaded.")
    except Exception as e:
        log_message(f"Error loading user preferences: {e}")

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x250")

    # Refresh Rate
    refresh_rate_label = tk.Label(settings_window, text="Refresh Rate (ms):")
    refresh_rate_label.pack(pady=5)
    refresh_rate_entry = tk.Entry(settings_window)
    refresh_rate_entry.insert(0, str(refresh_rate))
    refresh_rate_entry.pack(pady=5)

    # Network Interface
    interface_label = tk.Label(settings_window, text="Network Interface:")
    interface_label.pack(pady=5)
    interface_combobox = ttk.Combobox(settings_window, values=get_network_interfaces())
    interface_combobox.set(interface_to_monitor if interface_to_monitor else "Select Interface")
    interface_combobox.pack(pady=5)

    # Network Range
    network_range_label = tk.Label(settings_window, text="Network Range (e.g., 192.168.1.0/24):")
    network_range_label.pack(pady=5)
    network_range_entry = tk.Entry(settings_window)
    network_range_entry.insert(0, network_range)
    network_range_entry.pack(pady=5)

    def save_settings():
        global refresh_rate, interface_to_monitor, network_range
        try:
            refresh_rate = int(refresh_rate_entry.get())
            interface_to_monitor = interface_combobox.get()
            network_range = network_range_entry.get()
            save_user_preferences()
            log_message("Settings saved.")
            settings_window.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the refresh rate.")

    save_button = tk.Button(settings_window, text="Save", command=save_settings)
    save_button.pack(pady=10)

def show_notification(message):
    notification_window = tk.Toplevel(root)
    notification_window.title("Notification")
    notification_window.geometry("300x100")
    notification_label = tk.Label(notification_window, text=message, wraplength=250)
    notification_label.pack(pady=20)
    ok_button = tk.Button(notification_window, text="OK", command=notification_window.destroy)
    ok_button.pack(pady=5)

# Create the main application window
root = tk.Tk()
root.title("Network Device Monitor")
root.geometry("800x600")
root.configure(bg="#2E2E2E")

# Create a title label
title_label = tk.Label(root, text="Network Device Monitor", font=("Helvetica", 16), bg="#2E2E2E", fg="#FFFFFF")
title_label.pack(pady=10)

# Create a frame for the device list
frame = tk.Frame(root, bg="#2E2E2E")
frame.pack(pady=20, fill=tk.BOTH, expand=True)

# Create a treeview for displaying devices
columns = ("IP Address", "MAC Address", "Hostname", "Device Type", "Status", "Last Seen", "Connection Type")
tree = ttk.Treeview(frame, columns=columns, show='headings', height=20)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
scrollbar.pack(side=tk.RIGHT, fill='y')
tree.configure(yscrollcommand=scrollbar.set)

# Define headings
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=100)

# Create a log area at the bottom
log_area = tk.Text(root, height=10, bg="#1E1E1E", fg="#FFFFFF", font=("Courier New", 10))
log_area.pack(pady=10, fill=tk.BOTH, expand=True)

# Create buttons for exporting logs and adding known devices
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Button definitions
buttons = [
    ("Export Log", export_log),
    ("Export Device List (CSV)", lambda: export_device_list('csv')),
    ("Export Device List (JSON)", lambda: export_device_list('json')),
    ("Add Known Device", add_known_device),
    ("Block IP", block_ip),
    ("Unblock IP", unblock_ip),
    ("Load Known Devices", load_known_devices),
    ("Search Device", search_device),
    ("Open Packet Sniffer", open_packet_sniffer),
    ("Settings", open_settings)
]

for (text, command) in buttons:
    button = tk.Button(button_frame, text=text, command=command)
    button.pack(side=tk.LEFT, padx=5)

# Bind double-click event to show device details
tree.bind("<Double-1>", lambda event: show_device_details(tree.item(tree.selection())['values']))

# Load user preferences
load_user_preferences()

# Start the device monitoring in a separate thread
Thread(target=update_device_list, daemon=True).start()

# Start processing the log queue
process_log_queue()

# Start the GUI main loop
try:
    root.mainloop()
except Exception as e:
    logging.error(f"Application error: {e}")
    show_notification(f"An error occurred: {e}")

# Save user preferences on exit
save_user_preferences()
