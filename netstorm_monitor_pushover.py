from scapy.all import sniff, UDP, IP, IPv6
from scapy.layers.dns import DNS
import threading
from win10toast import ToastNotifier
from datetime import datetime
import csv
import requests  # Import for Pushover

# Initialize the notifier
toaster = ToastNotifier()

# Pushover API credentials
pushover_user_key = 'your user key'  # Replace with your Pushover user key
pushover_api_token = 'your api token'  # Replace with your Pushover API token

# Function to send a Pushover notification
def send_pushover_notification(title, message):
    url = 'https://api.pushover.net/1/messages.json'
    payload = {
        'token': pushover_api_token,
        'user': pushover_user_key,
        'title': title,
        'message': message
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send Pushover notification: {response.text}")

# Function to log data to a CSV file
def log_to_csv(timestamp, ipv4_count, ipv6_count, total_count):
    with open('network_monitor_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, ipv4_count, ipv6_count, total_count])

def notify_user(title, message, duration=10):
    # Display a notification
    toaster.show_toast(title, message, duration=duration, threaded=True)

# Define the capture function
def capture_mdns_packets(interface, threshold, capture_duration):
    packet_count = {'ipv4': 0, 'ipv6': 0}

    def packet_callback(packet):
        # Check for mDNS over IPv4
        if IP in packet and UDP in packet and packet[UDP].dport == 5353:
            packet_count['ipv4'] += 1
        # Check for mDNS over IPv6
        elif IPv6 in packet and UDP in packet and packet[UDP].dport == 5353:
            packet_count['ipv6'] += 1

    # Start packet sniffing
    sniff(iface=interface, prn=packet_callback, timeout=capture_duration, store=0)

    # Calculate total packets
    total_mdns_packets = packet_count['ipv4'] + packet_count['ipv6']
    
    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Print the packet count to the console
    print(f"{timestamp} - Total mDNS packets in the last {capture_duration} seconds: {total_mdns_packets}")

    # Log the data to a CSV file
    log_to_csv(timestamp, packet_count['ipv4'], packet_count['ipv6'], total_mdns_packets)

    if total_mdns_packets > threshold:
        alert_message = f"High mDNS traffic detected: {total_mdns_packets} packets in the last {capture_duration} seconds over threshold {threshold}!"
        print("Alert: " + alert_message)
        notify_user("Network Alert", f"{timestamp} - {alert_message}")
        send_pushover_notification("Network Alert", f"{timestamp} - {alert_message}")

# Parameters
network_interface = 'Intel GB Bottom or Left Card Port House Network'  # Replace with your network interface name
capture_duration = 10  # Duration to capture in seconds
threshold = 75  # Example threshold for packet count

# Create CSV file and write headers if it doesn't exist
csv_file = 'network_monitor_log.csv'
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'IPv4 Count', 'IPv6 Count', 'Total Count'])

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
