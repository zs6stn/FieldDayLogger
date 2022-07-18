"""library to handle cat control"""
import logging
import socket
import xmlrpc.client


class CAT:
    """CAT control rigctld or flrig"""

    def __init__(self, interface: str, host: str, port: int) -> None:
        """initializes cat"""
        self.server = None
        self.rigctrlsocket = None
        self.interface = interface.lower()
        self.host = host
        self.port = port
        if self.interface == "flrig":
            target = f"http://{host}:{port}"
            logging.info("cat_init: %s", target)
            self.server = xmlrpc.client.ServerProxy(target)
        if self.interface == "rigctld":
            self.__initialize_rigctrld()

    def __initialize_rigctrld(self):
        logging.warning("initializing rigctrld")
        try:
            self.rigctrlsocket = socket.socket()
            self.rigctrlsocket.settimeout(0.5)
            self.rigctrlsocket.connect((self.host, self.port))
        except socket.timeout as exception:
            logging.warning("Socket TimeOut %s", exception)
            if self.rigctrlsocket is not None:
                logging.warning("Closing Socket")
                self.rigctrlsocket.close()
            self.rigctrlsocket = None

        except socket.error as exception:
            logging.warning("Socket Error %s", exception)
            if self.rigctrlsocket is not None:
                logging.warning("Closing Socket")
                self.rigctrlsocket.close()
            self.rigctrlsocket = None

    def get_vfo(self) -> str:
        """Poll the radio for current vfo using the interface"""
        vfo = ""
        if self.interface == "flrig":
            vfo = self.__getvfo_flrig()
            logging.warning("%s", vfo)
        if self.interface == "rigctld":
            vfo = self.__getvfo_rigctld()
            logging.warning("%s", vfo)
            if "RPRT -" in vfo:
                vfo = ""
                self.rigctrlsocket = None
        return vfo

    def __getvfo_flrig(self) -> str:
        """Poll the radio using flrig"""
        try:
            return self.server.rig.get_vfo()
        except ConnectionRefusedError as exception:
            logging.warning("%s", exception)
        except xmlrpc.client.Fault as exception:
            logging.warning("%d, %s", exception.faultCode, exception.faultString)
        return ""

    def __getvfo_rigctld(self) -> str:
        """Returns VFO freq returned from rigctld"""
        if self.rigctrlsocket is None:
            self.__initialize_rigctrld()
        if not self.rigctrlsocket is None:
            try:
                self.rigctrlsocket.settimeout(1)
                self.rigctrlsocket.sendall(b"f\n")
                output = self.rigctrlsocket.recv(1024).decode().strip()
                self.rigctrlsocket.sendall(b"\n")
                return output
            except socket.timeout as exception:
                logging.warning("Socket TimeOut %s", exception)
                if self.rigctrlsocket is not None:
                    logging.warning("Closing Socket")
                    self.rigctrlsocket.close()
                self.rigctrlsocket = None
            except socket.error as exception:
                logging.warning("Socket Error %s", exception)
                if self.rigctrlsocket is not None:
                    logging.warning("Closing Socket")
                    self.rigctrlsocket.close()
                self.rigctrlsocket = None
            return ""

        self.__initialize_rigctrld()
        return ""

    def get_mode(self) -> str:
        """Returns the current mode filter width of the radio"""
        if self.interface == "flrig":
            return self.__getmode_flrig()
        if self.interface == "rigctld":
            return self.__getmode_rigctld()
        return ""

    def __getmode_flrig(self) -> str:
        """Returns mode via flrig"""
        try:
            return self.server.rig.get_mode()
        except ConnectionRefusedError as exception:
            logging.warning("%s", exception)
        return ""

    def __getmode_rigctld(self) -> str:
        """Returns mode via rigctld"""
        if self.rigctrlsocket is None:
            self.__initialize_rigctrld()
        if not self.rigctrlsocket is None:
            try:
                self.rigctrlsocket.settimeout(1)
                self.rigctrlsocket.sendall(b"m\n")
                output = self.rigctrlsocket.recv(1024).decode().strip().split()[0]
                self.rigctrlsocket.sendall(b"\n")
                return output
            except IndexError as exception:
                logging.warning("IndexError %s", exception)
                if self.rigctrlsocket is not None:
                    logging.warning("Closing Socket")
                    self.rigctrlsocket.close()
                self.rigctrlsocket = None
            except socket.timeout as exception:
                logging.warning("Socket TimeOut %s", exception)
                if self.rigctrlsocket is not None:
                    logging.warning("Closing Socket")
                    self.rigctrlsocket.close()
                self.rigctrlsocket = None
            except socket.error as exception:
                logging.warning("Socket Error %s", exception)
                if self.rigctrlsocket is not None:
                    logging.warning("Closing Socket")
                    self.rigctrlsocket.close()
                self.rigctrlsocket = None
        return ""

    def set_vfo(self, freq: str) -> bool:
        """Sets the radios vfo"""
        if self.interface == "flrig":
            return self.__setvfo_flrig(freq)
        if self.interface == "rigctld":
            return self.__setvfo_rigctld(freq)
        return False

    def __setvfo_flrig(self, freq: str) -> bool:
        """Sets the radios vfo"""
        try:
            return self.server.rig.set_frequency(float(freq))
        except ConnectionRefusedError as exception:
            logging.warning("%s", exception)
        return False

    def __setvfo_rigctld(self, freq: str) -> bool:
        """sets the radios vfo"""
        if self.rigctrlsocket is None:
            self.__initialize_rigctrld()
        if not self.rigctrlsocket is None:
            try:
                self.rigctrlsocket.settimeout(1)
                self.rigctrlsocket.sendall(bytes(f"F {freq}\n", "utf-8"))
                _ = self.rigctrlsocket.recv(1024).decode().strip()
                self.rigctrlsocket.sendall(b"\n")
                return True
            except socket.timeout as exception:
                self.rigctrlsocket = None
                logging.warning("Socket TimeOut %s", exception)
                return False
            except socket.error as exception:
                logging.warning("Socket Error %s", exception)
                self.rigctrlsocket = None
                return False
        return False

    def set_mode(self, mode: str) -> bool:
        """Sets the radios mode"""
        if self.interface == "flrig":
            return self.__setmode_flrig(mode)
        if self.interface == "rigctld":
            return self.__setmode_rigctld(mode)
        return False

    def __setmode_flrig(self, mode: str) -> bool:
        """Sets the radios mode"""
        try:
            return self.server.rig.set_mode(mode)
        except ConnectionRefusedError as exception:
            logging.warning("%s", exception)
        return False

    def __setmode_rigctld(self, mode: str) -> bool:
        """sets the radios mode"""
        if self.rigctrlsocket is None:
            self.__initialize_rigctrld()
        if not self.rigctrlsocket is None:
            try:
                self.rigctrlsocket.settimeout(1)
                self.rigctrlsocket.sendall(bytes(f"M {mode} 0\n", "utf-8"))
                _ = self.rigctrlsocket.recv(1024).decode().strip()
                self.rigctrlsocket.sendall(b"\n")
                return True
            except socket.timeout as exception:
                self.rigctrlsocket = None
                logging.warning("Socket TimeOut %s", exception)
                return False
            except socket.error as exception:
                logging.warning("Socket Error %s", exception)
                self.rigctrlsocket = None
                return False
        return False
