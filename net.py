import socket
import pickle


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.100.8"
        self.port = 8888
        self.addr = (self.server, self.port)
        self.player = self.connect()

    def getP(self):
        return self.player

    def send_pickle(self, data):
        try:
            self.client.send(pickle.dumps(data))
            #return self.client.recv(4096).decode() # Can sometime Return nothing
        except:
            pass

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            print('Client Disconnected')

    def get(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(1024).decode()
        except:
            return 'no-data'

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(2048))
        except:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(8192))
