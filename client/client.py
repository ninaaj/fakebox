"""
    Christina Trotter
	5/27/19
	Python 3.6.2
"""
import pickle as pickle, datetime, os, socket, sys, traceback

HOST, PORT = 'localhost', 6000
ACK,DEL,UPD,UPL = b'ACK',b'DEL',b'UPD',b'UPL'
OWD = os.getcwd()
PATH = OWD + '/files/'
BORD = "\n---------------------------------------------------\n"
DBBR = BORD + '{}' + BORD
MENU = DBBR.format('MAIN MENU') + '[U]pload a file\n[D]elete a file\n[Q]uit\nCHOICE: '
INVL = '\n\nInvalid Input\nPlease enter U/u, D/d, or Q/q'
CON = 'Are you sure you want to delete {}?\n[Y]es\n[N]o\nANSWER: '
ERR = "\nCould not {} {} since it doesn't seem to exist"
REP = 'Sorry, {} already exists in the fakebox\nWould you like to replace it?\n[Y]es\n[N]o\nANSWER: '
DELE, QUIT, UPLD = ['D','d'], ['Q','q'], ['U','u']
CHS = [DELE,QUIT,UPLD]
YES, NO = ['Y','y'], ['N','n']
ANS = [YES,NO]
FIL = '{}\t{} bytes\t{}'

class Client:
    def __init__(self, host, port):
        self.files = self.load_files()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.start()

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

    def start(self):

        print(DBBR.format('\t~THE ALMOST DROPBOX~'))

        self.sock.connect((HOST, PORT))

        print('..SYNCHRONIZATION IN-PROGRESS..')

        self.synch()

        res = self.sock.recv(1024) #13

        print('..SYNCHRONIZATION COMPLETE..')
        ch = ''
        while ch not in QUIT:
            self.show_files()
            os.chdir(OWD)
            ch = input(MENU)
            if not any(ch in c for c in CHS):
                print(INVL)
            elif ch in UPLD:
                print(DBBR.format('UPLOAD'))
                name = input('Please enter a filename: ')
                if any(name in f for f in self.files):
                    an = input(REP.format(name))
                    while not any(an in a for a in ANS):
                        an = input(REP.format(name))
                    if an in YES:
                        self.replace_file(name, ERR)
                else:
                    if not os.path.isfile(name):
                        print(ERR.format('upload',name))
                        continue
                    self.upload_file(name)
            elif ch in DELE:
                print(DBBR.format('DELETE'))
                name = input('Please enter a filename: ')
                os.chdir(PATH[:-1])
                if not os.path.isfile(name):
                    print(ERR.format('delete',name))
                    continue
                an = input(CON.format(name))
                while not any(an in a for a in ANS):
                    an = input(CON.format(name))
                if an in YES:
                    self.delete_file(name)
                else:
                    print('\nDELETION CANCELED..\n')

        self.update_log()
        print('\nGOODBYE')
        self.sock.close()


    def delete_file(self, name):
        if any(name in f for f in self.files):

            x = [x for x in self.files if name in x][0]

            y = self.files.index(x)

            del self.files[y]

            self.sock.sendall(DEL) #14
            res = self.sock.recv(1024) #15
            self.sock.sendall(name.encode('utf-8')) #16
            res = self.sock.recv(1024) #17

            os.remove(PATH + name)

            print('\nDELETION COMPLETE..')

    def replace_file(self, name, ERR):
        os.chdir(PATH[:-1])
        if os.path.isfile(name):
            self.delete_file(name)
        else:
            print(ERR.format('replace',name))
        os.chdir(OWD)
        if os.path.isfile(name):
            self.upload_file(name)
        else:
            print(ERR.format('upload',name))

    def upload_file(self, name):
        self.sock.sendall(UPL) #14

        res = self.sock.recv(1024) #15

        new_file = open(name, 'rb')

        new_file = new_file.read()

        cur = open(PATH + name,'wb+')

        cur.write(new_file)

        cur.close()

        size = len(new_file)

        os.chdir(PATH[:-1])

        time = os.path.getmtime(name)

        entry = [name, size, time]

        self.files.append(entry)

        e_data = pickle.dumps(entry, -1)

        self.sock.sendall(e_data) #16

        res = self.sock.recv(1024) #17

        self.sock.sendall(new_file) #18

        res = self.sock.recv(1024) #19

        print('\nUPLOAD COMPLETE..')

    def delete_files(self, d_files):
        for d in d_files:
            if any(d[0] in f for f in self.files):
                print('found file to be deleted')
                x = [x for x in self.files if d[0] in x][0]
                y = self.files.index(x)
                del self.files[y]
                os.remove(PATH + d[0])
            return

    def get_files(self, g_files):
        for g in g_files:
            if any(g[0] in f for f in self.files):
                x = [x for x in self.files if g[0] in x][0]
                y = self.files.index(x)
                del self.files[y]

            self.files.append([g[0],int(g[1]),float(g[2])])

            cur = open(PATH + g[0],'wb+')
            m_bytes = int(g[1])

            b = self.sock.recv(1024) #11

            cur.write(b)

            t_bytes = len(b)

            while(t_bytes < m_bytes):
                b = self.sock.recv(1024) #11
                cur.write(b)
                t_bytes = t_bytes + len(b)

            cur.close()

            self.sock.sendall(ACK) #12

    def send_files(self, s_files):
        for f in s_files:
            cur = open(PATH + f[0], 'rb')
            cur = cur.read()
            self.sock.sendall(cur) #6
            res = self.sock.recv(1024) #7

    def synch(self):
        c_files = pickle.dumps(self.files, -1)

        self.sock.sendall(c_files) #1

        self.sock.recv(1024) #2

        self.sock.sendall(ACK) #3

        d_data = self.sock.recv(1024) #4a

        self.sock.sendall(ACK) #5a

        g_data = self.sock.recv(1024) #4

        self.sock.sendall(ACK) #5

        d_files = pickle.loads(d_data)

        self.delete_files(d_files)

        g_files = pickle.loads(g_data)

        self.send_files(g_files)

        self.sock.sendall(ACK) #8

        s_data = self.sock.recv(1024) #9

        self.sock.sendall(ACK) #10

        s_files = pickle.loads(s_data)

        self.get_files(s_files)

    def show_files(self):
        print(DBBR.format('FILES') + 'NAME\tSIZE\t\tLAST MODIFIED')
        for f in self.files:
            ts = datetime.datetime.fromtimestamp(int(round(float(f[2]))))
            print(FIL.format(f[0],f[1],ts))

    def update_log(self):
        self.sock.sendall(UPD) #14
        name = 'file.log'
        log = open(name, 'w+')
        for f in self.files:
            s = f[0] + ' ' + str(f[1]) + ' ' + str(f[2]) + '\n'
            log.write(s)
        log.close

if __name__ == '__main__':
    print(HOST, PORT)
    try:
        client = Client(HOST, PORT)
    except Exception as e:
        print(str(e))
        _, _, tb = sys.exc_info()
        print(traceback.format_list(traceback.extract_tb(tb)[-1:])[-1])