import socket
import tqdm
import os

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096  # Sends 4096 bytes each time step

class Transfer:
    @staticmethod
    def establish_connection(host, port, is_sender):
        s = socket.socket()
        if is_sender:
            try:
                print("[*] Waiting for the receiver to connect...")
                s.bind((host, port))
                s.listen(5)  # Allows up to 5 connections
                client_socket, address = s.accept()
                print(f"[+] Connected to {address}.")
                return client_socket
            except Exception as e:
                print(f"Error establishing connection: {e}")
                return None
        else:  # Receiver connects to the sender
            try:
                print(f"[+] Connecting to {host}:{port}...")
                s.connect((host, port))
                print("[+] Connected.")
                return s
            except Exception as e:
                print(f"Error connecting to {host}:{port}: {e}")
                return None

    @staticmethod
    def send_file(s, filename):
        try:
            filesize = os.path.getsize(filename)
            s.send(f"{filename}{SEPARATOR}{filesize}".encode())
            
            # Starts sending the file
            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            
            with open(filename, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    s.sendall(bytes_read)
                    progress.update(len(bytes_read))
            
            print("[+] File sent successfully.")
        except Exception as e:
            print(f"Error sending file: {e}")

    @staticmethod
    def receive_file(s):
        try:
            received = s.recv(BUFFER_SIZE).decode()
            filename, filesize = received.split(SEPARATOR)
            
            filesize = int(filesize)

            save_directory = input("Enter the directory where you want to save the file: ")

            # Constructs full save path using the original filename from sender
            save_path = os.path.join(save_directory, os.path.basename(filename))

            # Ensures the directory exists or create it
            os.makedirs(save_directory, exist_ok=True)

            with open(save_path, "wb") as f:
                progress = tqdm.tqdm(range(filesize), f"Receiving {os.path.basename(filename)}", unit="B", unit_scale=True, unit_divisor=1024)

                total_received = 0
                while total_received < filesize:
                    bytes_read = s.recv(BUFFER_SIZE)
                    if not bytes_read:
                        break
                    f.write(bytes_read)
                    total_received += len(bytes_read)
                    progress.update(len(bytes_read))
            
            print("[+] File received successfully.")
        except Exception as e:
            print(f"Error receiving file: {e}")

def main():
    my_transfer = Transfer()
    
    while True:  
        mode = input("Do you want to send or receive a file? (send/receive/quit): ").strip().lower()
        
        if mode == "receive":
            host = input("Enter the sender's local IP address (e.g., 192.168.x.x): ")  # Sender's local IP
            port = int(input("Enter the port number on which you want to receive: "))  # Port to listen on
            
            s = my_transfer.establish_connection(host, port, is_sender=False)
            if not s:
                continue  # Retry connection if failed

            while True:  # Loop for multiple file receptions
                my_transfer.receive_file(s)

                more_files = input("Do you want to receive another file? (yes/no): ").strip().lower()
                if more_files != 'yes':
                    break
        
        elif mode == "send":
            host = input("Enter your own local IP address (e.g., 192.168.x.x): ")  # Sender's own local IP
            port = int(input("Enter your desired port number: "))  # Port to connect from
            
            s = my_transfer.establish_connection(host, port, is_sender=True)
            if not s:
                continue  # Retry connection if failed

            while True:  # Loop for multiple file sends
                filename = input("Enter the path of the file to send: ")
                
                my_transfer.send_file(s, filename)

                more_files = input("Do you want to send another file? (yes/no): ").strip().lower()
                if more_files != 'yes':
                    break
        
        elif mode == "quit":
            print("Exiting the program.")
            break
        
        else:
            print("Invalid option. Please enter 'send', 'receive', or 'quit'.")

    if 's' in locals():
        s.close()  # Close the socket after finishing all transfers

if __name__ == "__main__":
    main()
