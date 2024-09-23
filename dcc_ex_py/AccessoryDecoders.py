from typing import Any
from .Helpers import ActiveState


class Accessories:
    def __init__(self, controller: Any) -> None:
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

    def set_accessory_decoder(self, linear_address: int, state: ActiveState) -> None:
        self.controller.send_command(f"<a {linear_address} {state}>")

    def set_accessory_decoder_subaddress(self, address: int, subaddress: int, state: ActiveState) -> None:
        self.controller.send_command(f"<a {address} {subaddress} {state}>")
