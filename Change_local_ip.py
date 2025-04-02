import psutil
import subprocess
import random
import socket
import re

def get_network_info():
    """Get the network interfaces and their IP addresses."""
    interfaces = psutil.net_if_addrs()
    network_info = {}
    for interface, addrs in interfaces.items():
        for addr in addrs:
            if addr.family == socket.AF_INET:  # Only interested in IPv4 addresses
                network_info[interface] = addr.address
    return network_info

def get_active_ips():
    """Get a list of active IP addresses on the local network."""
    active_ips = set()
    try:
        # Use the arp command to get a list of active IPs
        output = subprocess.check_output(['arp', '-a']).decode()
        # Extract IP addresses from the output
        ip_pattern = re.compile(r'\((.*?)\)')
        for match in ip_pattern.findall(output):
            active_ips.add(match)
    except Exception as e:
        print(f"Error retrieving active IPs: {e}")
    return active_ips

def generate_random_ip(subnet, active_ips):
    """Generate a random IP address in the given subnet that is not in use."""
    subnet_parts = subnet.split('.')
    while True:
        random_ip = f"{subnet_parts[0]}.{subnet_parts[1]}.{subnet_parts[2]}.{random.randint(1, 254)}"
        if random_ip not in active_ips:
            return random_ip

def change_ip(interface, new_ip, subnet_mask):
    """Change the IP address of the specified interface."""
    try:
        # Bring the interface down
        subprocess.run(f'sudo ip link set {interface} down', shell=True, check=True)
        # Change the IP address
        subprocess.run(f'sudo ip addr add {new_ip}/{subnet_mask} dev {interface}', shell=True, check=True)
        # Bring the interface up
        subprocess.run(f'sudo ip link set {interface} up', shell=True, check=True)
        return new_ip
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to change IP: {e}")
        return None

def main():
    """Main function to run the IP changer."""
    network_info = get_network_info()
    
    if not network_info:
        print("No network interfaces found.")
        return

    print("Available network interfaces and their current IP addresses:")
    for interface, ip in network_info.items():
        print(f"{interface}: {ip}")

    selected_interface = input("Enter the interface you want to change the IP for: ")

    if selected_interface in network_info:
        current_ip = network_info[selected_interface]
        print(f"Current IP Address: {current_ip}")  # Print current IP to terminal
        subnet = '.'.join(current_ip.split('.')[:-1])  # Get the subnet

        # Get active IPs on the network
        active_ips = get_active_ips()
        print("Active IPs on the network:")
        for ip in active_ips:
            print(ip)

        # Ask user if they want to spoof an IP or generate a random one
        choice = input("Do you want to (1) spoof an IP or (2) generate a random IP? (Enter 1 or 2): ")

        if choice == '1':
            new_ip = input("Enter the IP address you want to spoof: ")
            if new_ip in active_ips:
                print("The IP address is already in use. Please choose another one.")
                return
        elif choice == '2':
            new_ip = generate_random_ip(subnet, active_ips)
        else:
            print("Invalid choice.")
            return

        new_ip = change_ip(selected_interface, new_ip, "24")  # Assuming a /24 subnet
        if new_ip:
            print(f"New IP Address: {new_ip}")  # Print new IP to terminal
    else:
        print("Invalid interface selected.")

if __name__ == "__main__":
    main()

