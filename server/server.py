"""
    Christina Trotter
	5/27/19
	Python 3.6.2
"""
import pickle as pickle, datetime, os, socketserver, sys, traceback, time

HOST, PORT = '0.0.0.0', 6000
ACK,DEL,UPD,UPL = b'ACK',b'DEL',b'UPD',b'UPL'
OWD = os.getcwd()
PATH = OWD + '/files/'
BORD = '\n---------------------------------------------------\n'
DBBR = BORD + '{}' + BORD
FIL = '{}\t{} bytes\t{}'

class Server(socketserver.BaseRequestHandler):
    def handle(self):

        print('..CONNECTED TO CLIENT..')

        print('..SYNCHRONIZATION IN-PROGRESS..')

        self.synch()

        self.request.sendall(ACK) #13

        print('..SYNCHRONIZATION COMPLETE..')

        self.show_files()

        res = self.request.recv(1024) #14

        while res != UPD:
            self.request.sendall(ACK) #15
            if res == UPL:
                self.upload_file()
            elif res == DEL:
                self.delete_file()
            self.show_files()
            res = self.request.recv(1024) #14

        self.update_log()

        print('\n..CLIENT ENDED CONNECTION..')

    def setup(self):
        self.files = self.load_files()

    def load_files(self):
        name,files = 'file.log',[]

        log = open(name, 'r+')
        log = log.read()
        log = log.split('\n')
        for l in log:
            if(len(l) == 0):
                continue
            files.append(l.split(' '))
        return files

    def delete_file(self):
        n = self.request.recv(1024) #16
        n = n.decode('utf-8')
        self.request.sendall(ACK) #17
        if any(n in f for f in self.files):
            x = [x for x in self.files if n in x][0]
            y = self.files.index(x)
            del self.files[y]
            os.remove(PATH + n)
            print('\n..DELETION COMPLETE..')

    def upload_file(self):
        e_data = self.request.recv(1024) #16
        
        self.request.sendall(ACK) #17

        entry = pickle.loads(e_data)
        self.files.append(entry)

        cur = open(PATH + entry[0],'wb+')

        m_bytes = entry[1]

        b = self.request.recv(1024) #18

        cur.write(b)

        t_bytes = len(b)

        while(t_bytes < m_bytes):
            b = self.request.recv(1024) #18
            cur.write(b)
            t_bytes = t_bytes + len(b)

        cur.close()

        self.request.sendall(ACK) #19
        print('\n..UPLOAD COMPLETE..')

    def get_files(self, g_files):
        for g in g_files:
            if any(g[0] in f for f in self.files):
                x = [x for x in self.files if g[0] in x][0]
                y = self.files.index(x)
                del self.files[y]

            self.files.append([g[0],int(g[1]),float(g[2])])

            cur = open(PATH + g[0],'wb+')

            m_bytes = int(g[1])

            b = self.request.recv(1024) #6
            cur.write(b)
            t_bytes = len(b)

            while(t_bytes < m_bytes):
                b = self.request.recv(1024) #6
                cur.write(b)
                t_bytes = t_bytes + len(b)

            cur.close()

            self.request.sendall(ACK) #7

    def send_files(self, s_files):
        for f in s_files:
            cur = open(PATH + f[0],'rb')
            b = cur.read()
            self.request.sendall(b) #11
            cur.close()
            self.request.recv(1024) #12

    def synch_files(self, c_files):
        d_files, g_files, s_files = [],[],[]
        if len(self.files) != 0:
            for f in self.files:
                if any(f[0] in c for c in c_files):
                    x = [x for x in c_files if f[0] in x][0]
                    y = c_files.index(x)
                    if(c_files[y][2] > f[2]):
                        g_files.append(c_files[y])
                        self.files.remove(f)
                        self.files.append(c_files[y])
                    elif(c_files[y][2] < f[2]):
                        s_files.append(f)
                else:
                    s_files.append(f)
            for c in c_files:
                if not any(c[0] in f for f in self.files):
                    d_files.append(c)
        else:
            d_files = c_files
        return d_files, g_files, s_files

    def synch(self):
        c_data = self.request.recv(1024) #1

        self.request.sendall(ACK) #2

        self.request.recv(1024) #3

        c_files = pickle.loads(c_data)

        d_files, g_files, s_files = self.synch_files(c_files)

        d_data = pickle.dumps(d_files, -1)

        g_data = pickle.dumps(g_files, -1)

        s_data = pickle.dumps(s_files, -1)

        self.request.sendall(d_data) #4a

        res = self.request.recv(1024) #5a

        self.request.sendall(g_data) #4

        res = self.request.recv(1024) #5

        self.get_files(g_files)

        res = self.request.recv(1024) #8

        self.request.sendall(s_data) #9

        res = self.request.recv(1024) #10

        self.send_files(s_files)

    def show_files(self):
        print(DBBR.format('FILES') + 'NAME\tSIZE\t\tLAST MODIFIED')
        for f in self.files:
            ts = datetime.datetime.fromtimestamp(int(round(float(f[2]))))
            print(FIL.format(f[0],f[1],ts))

    def update_log(self):
        name = 'file.log'
        log = open(name, 'w+')
        for f in self.files:
            s = f[0] + ' ' + str(f[1]) + ' ' + str(f[2]) + '\n'
            log.write(s)
        log.close

if __name__ == '__main__':
    try:
        print('..SERVER SERVING..')
        server = socketserver.TCPServer((HOST, PORT), Server)
        server.serve_forever()

    except Exception as e:
        print(str(e))
        _, _, tb = sys.exc_info()
        print(traceback.format_list(traceback.extract_tb(tb)[-1:])[-1])