import socket
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import scrolledtext

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Server")

        self.text_area = scrolledtext.ScrolledText(root, state='disabled')
        self.text_area.grid(row=0, column=0, columnspan=2)

        self.message_entry = tk.Entry(root)
        self.message_entry.grid(row=1, column=0)

        self.send_button = tk.Button(root, text="Send Message", command=self.send_message)
        self.send_button.grid(row=1, column=1)

        self.file_button = tk.Button(root, text="Send File", command=self.send_file)
        self.file_button.grid(row=2, column=0, columnspan=2)

        self.start_server()

    def start_server(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('localhost', 65432))
        self.server.listen(1)
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, "Server started, waiting for client...\n")
        self.text_area.config(state='disabled')
        threading.Thread(target=self.accept_client, daemon=True).start()

    def accept_client(self):
        self.client, addr = self.server.accept()
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, f"Connected to {addr}\n")
        self.text_area.config(state='disabled')
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self):
        message = self.message_entry.get()
        if message:
            full_message = f"MSG:{message}"  # Prepend 'MSG:' to indicate a message
            self.client.sendall(full_message.encode('utf-8'))
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, f"You: {message}\n")
            self.text_area.config(state='disabled')
            self.message_entry.delete(0, tk.END)

    def send_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                full_message = b"FILE:" + file_data  # Prepend 'FILE:' to indicate a file
                self.client.sendall(full_message)
                self.text_area.config(state='normal')
                self.text_area.insert(tk.END, f"File sent: {file_path}\n")
                self.text_area.config(state='disabled')
    
    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(1024)
                if data:
                    if data.startswith(b"MSG:"):
                        message = data[4:].decode('utf-8')
                        self.text_area.config(state='normal')
                        self.text_area.insert(tk.END, f"Client: {message}\n")
                        self.text_area.config(state='disabled')
                    elif data.startswith(b"FILE:"):
                        file_data = data[5:]
                        self.text_area.config(state='normal')
                        self.text_area.insert(tk.END, "File received from client\n")
                        self.text_area.config(state='disabled')
                        # Handle the received file data
                        file_name = "received_file.txt"
                        with open(file_name, 'wb') as file:
                            file.write(file_data)
                        if file_name.endswith('.txt'):
                            with open(file_name, 'r') as file:
                                file_contents = file.read()
                                self.text_area.config(state='normal')
                                self.text_area.insert(tk.END, "\n")
                                self.text_area.insert(tk.END, f"File contents:\n{file_contents}\n")
                                self.text_area.insert(tk.END, "\n")
                                self.text_area.config(state='disabled')
                                self.text_area.see(tk.END)  # Scroll to the end of the text area
            except ConnectionResetError:
                break

root = tk.Tk()
app = ServerApp(root)
root.mainloop()
