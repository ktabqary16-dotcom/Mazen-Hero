#!/bin/bash
echo -e "\033[36m═══════════════════════════════════════════════════════════\033[0m"
echo -e "\033[36m     Mazen ZAP Pro – Installation Script\033[0m"
echo -e "\033[36m═══════════════════════════════════════════════════════════\033[0m"

# تحديث الحزم وتثبيت المتطلبات
sudo apt update -y
sudo apt install -y python3 python3-pip nmap hydra metasploit-framework zaproxy php wget curl

# تثبيت مكتبات بايثون
pip3 install -r requirements.txt

# إنشاء المجلدات
mkdir -p wordlists output logs reports payloads sessions config

# إنشاء قوائم كلمات المرور
echo -e "admin\nroot\n123456\npassword" > wordlists/fast.txt
echo -e "admin\nroot\nuser\ntest" > wordlists/users.txt

# منح الصلاحيات
chmod +x mzap.py

echo -e "\033[32m✅ Installation complete!\033[0m"
echo -e "\033[33m🚀 Run: python3 mzap.py\033[0m"
