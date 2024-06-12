from scapy.all import sniff, UDP, IP, IPv6, get_if_list, get_if_hwaddr
from scapy.layers.dns import DNS
import threading
from win10toast import ToastNotifier
import requests
import csv
from datetime import datetime

# Initialize the notifier
toaster = ToastNotifier()

# Pushover credentials
PUSHOVER_USER_KEY = 'your key here'
PUSHOVER_API_TOKEN = 'your token here'

def notify_user(title, message, duration=10):
    # Display a Windows notification
    toaster.show_toast(title, message, duration=duration, threaded=True)

def send_pushover_notification(title, message):
    data = {
        'token': PUSHOVER_API_TOKEN,
        'user': PUSHOVER_USER_KEY,
        'title': title,
        'message': message
    }
    response = requests.post('https://api.pushover.net/1/messages.json', data=data)
    if response.status_code == 200:
        print("Pushover notification sent successfully.")
    else:
        print(f"Failed to send Pushover notification: {response.status_code} - {response.text}")

# Function to display available interfaces and select one
def select_interface():
    interfaces = get_if_list()
    print("Available Network Interfaces:")
    for idx, iface in enumerate(interfaces):
        print(f"{idx}: {iface} ({get_if_hwaddr(iface)})")
    idx = int(input("Select the interface number to monitor: "))
    return interfaces[idx]

# Function to write to CSV
def log_to_csv(timestamp, total_packets, highest_src_ip, highest_count):
    with open('network_monitor_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, total_packets, highest_src_ip, highest_count])

# Define the capture function
def capture_mdns_packets(interface, threshold, capture_duration):
    packet_count = {}

    def packet_callback(packet):
        # Get source IP address
        src_ip = None
        if IP in packet and UDP in packet and packet[UDP].dport == 5353:
            src_ip = packet[IP].src
        elif IPv6 in packet and UDP in packet and packet[UDP].dport == 5353:
            src_ip = packet[IPv6].src

        if src_ip:
            # Increment packet count for the source IP
            if src_ip in packet_count:
                packet_count[src_ip] += 1
            else:
                packet_count[src_ip] = 1

    # Start packet sniffing
    sniff(iface=interface, prn=packet_callback, timeout=capture_duration, store=0)

    # Check the count against the threshold
    total_packets = sum(packet_count.values())
    print(f"Total packets in the last {capture_duration} seconds: {total_packets}")
    print(f"Packet counts by source IP: {packet_count}")

    if total_packets > threshold:
        # Find the source IP address with the highest packet count
        highest_src_ip = max(packet_count, key=packet_count.get)
        highest_count = packet_count[highest_src_ip]
        alert_message = f"High network traffic detected: {total_packets} packets in the last {capture_duration} seconds!\nHighest source IP: {highest_src_ip} with {highest_count} packets."
        print("Alert: " + alert_message)
        notify_user("Network Alert", alert_message)
        send_pushover_notification("Network Alert", alert_message)
        
        # Log the event to CSV
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_to_csv(timestamp, total_packets, highest_src_ip, highest_count)

# Parameters
network_interface = 'Intel GB Bottom or Left Card Port House Network'  # Fixed network interface
capture_duration = 10  # Duration to capture in seconds
threshold = 75  # Example threshold for packet count

# Create the CSV file and write the header if it doesn't exist
with open('network_monitor_log.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Total Packets', 'Highest Source IP', 'Packet Count'])

def monitor_network():
    while True:
        capture_mdns_packets(network_interface, threshold, capture_duration)

# Run the network monitor
monitor_thread = threading.Thread(target=monitor_network)
monitor_thread.daemon = True  # Allow the thread to be killed when the main program exits
monitor_thread.start()

try:
    while True:
        pass  # Keep the main thread running
except KeyboardInterrupt:
    print("Monitoring stopped.")
