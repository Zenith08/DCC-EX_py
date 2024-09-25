from dcc_ex_py.DCCEX import DCCEX

class MockDCCEX(DCCEX):
    def __init__(self, ip: str, port: int) -> None:
        super().__init__(ip, port)
        #: The most recent command received by this mock object.
        self.last_command_received: str = ""

    def _init_sockets(self, ip: str, port: int) -> None:
        print(f"Would have created DCC-EX with ip: {ip} and port {port}.")
    
    def send_command(self, command: str) -> None:
        self.last_command_received = command
