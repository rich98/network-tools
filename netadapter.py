import platform
import os
import socket
import ctypes
import netifaces as ni

def get_friendly_name(adapter):
    MAX_ADAPTER_DESCRIPTION_LENGTH = 128
    MAX_ADAPTER_NAME_LENGTH = 256

    class IP_ADAPTER_ADDRESSES(ctypes.Structure):
        pass

    LP_IP_ADAPTER_ADDRESSES = ctypes.POINTER(IP_ADAPTER_ADDRESSES)

    class SOCKET_ADDRESS(ctypes.Structure):
        _fields_ = [
            ("lpSockaddr", ctypes.c_void_p),
            ("iSockaddrLength", ctypes.c_int),
        ]

    class IP_ADAPTER_UNICAST_ADDRESS(ctypes.Structure):
        pass

    PIP_ADAPTER_UNICAST_ADDRESS = ctypes.POINTER(IP_ADAPTER_UNICAST_ADDRESS)

    IP_ADAPTER_ADDRESSES._fields_ = [
        ("Length", ctypes.c_ulong),
        ("IfIndex", ctypes.c_ulong),
        ("Next", LP_IP_ADAPTER_ADDRESSES),
        ("AdapterName", ctypes.c_char_p),
        ("FirstUnicastAddress", PIP_ADAPTER_UNICAST_ADDRESS),
        ("FriendlyName", ctypes.c_wchar_p),
    ]

    IP_ADAPTER_UNICAST_ADDRESS._fields_ = [
        ("Length", ctypes.c_ulong),
        ("Flags", ctypes.c_ulong),
        ("Next", PIP_ADAPTER_UNICAST_ADDRESS),
        ("Address", SOCKET_ADDRESS),
        ("PrefixOrigin", ctypes.c_int),
        ("SuffixOrigin", ctypes.c_int),
        ("DadState", ctypes.c_int),
        ("ValidLifetime", ctypes.c_ulong),
        ("PreferredLifetime", ctypes.c_ulong),
        ("LeaseLifetime", ctypes.c_ulong),
        ("OnLinkPrefixLength", ctypes.c_ubyte),
    ]

    buffer_size = ctypes.c_ulong(0)
    
    # Check platform before using windll
    if platform.system() == 'Windows':
        ctypes.windll.Iphlpapi.GetAdaptersAddresses(0, 0, None, None, ctypes.byref(buffer_size))
        
        buffer = ctypes.create_string_buffer(buffer_size.value)
        addresses = ctypes.cast(buffer, LP_IP_ADAPTER_ADDRESSES)

        ctypes.windll.Iphlpapi.GetAdaptersAddresses(0, 0, None, addresses, ctypes.byref(buffer_size))

        while addresses:
            if addresses.contents.AdapterName == adapter.encode():
                return addresses.contents.FriendlyName
            addresses = addresses.contents.Next

    return "Unknown"

def list_network_adapters():
    adapters = ni.interfaces()
    print("Available network adapters:")
    for i, adapter in enumerate(adapters, start=1):
        friendly_name = get_friendly_name(adapter)
        print(f"{i}. {friendly_name} ({adapter})")
    return adapters

def get_user_input(adapters):
    while True:
        try:
            choice = input("Select the desired network adapter (1, 2, etc.) or 'q' to quit: ")
            
            if choice.lower() == 'q':
                print("Exiting the script.")
                exit()
            
            choice = int(choice)
            
            if 1 <= choice <= len(adapters):
                return adapters[choice - 1]
            else:
                print("Invalid choice. Please enter a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")

def main():
    adapters = list_network_adapters()
    selected_adapter = get_user_input(adapters)

    # Check if AF_INET is available for the selected adapter
    interface_info = ni.ifaddresses(selected_adapter).get(ni.AF_INET)
    
    if interface_info:
        interface_ip = interface_info[0]['addr']
        
        # On non-Windows platforms, AF_INET may not be applicable
        if platform.system() == 'Windows':
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            s.bind((interface_ip, 0))

        friendly_name = get_friendly_name(selected_adapter)

        print(f"Selected interface: {friendly_name} ({selected_adapter})")
        print(f"Interface IP address: {interface_ip}")
    else:
        print(f"No IPv4 address found for {selected_adapter}.")

    # Pause before continuing
    input("Press Enter to clear the screen and continue...")
    os.system('cls' if os.name == 'nt' else 'clear')
    main()

if __name__ == "__main__":
    main()




