"""A module containing the Accessories helper class."""
from typing import Any
from .Helpers import ActiveState


class Accessories:
    """Wraps control of DCC-EX accessory decoder control.
    Accessory Decoders are those that are connected to the track but do not control locomotives. Their addressing scheme and commands are different than locomotives.
    """

    def __init__(self, controller: Any) -> None:
        """Instantiated by the DCCEX Instance

        :param controller: The DCCEX object that this instance controls.
        """
        from .DCCEX import DCCEX
        self.controller: DCCEX = controller

    def set_accessory_decoder(self, linear_address: int, state: ActiveState) -> None:
        """Sets an accessory decoder to be ON or OFF based on a given Linear Address. See DCCEX Documentation for more.

        :param linear_address: The linear address of the accessory decoder + channel combination to set.
        :param state: Whether to set the decoder to be ON or OFF.
        """
        self.controller.send_command(f"<a {linear_address} {state}>")

    def set_accessory_decoder_subaddress(self, address: int, subaddress: int, state: ActiveState) -> None:
        """Sets an accessory decoder to be ON or OFF based on a given Address and Subaddress. See DCCEX Documentation for more.

        :param address: The non-linear address of the accessory decoder + channel combination to set.
        :param subaddress: For accessory decoders with multiple functions, subaddress chooses the function within the decoder.
        :param state: Whether to set the decoder to be ON or OFF.
        """
        self.controller.send_command(f"<a {address} {subaddress} {state}>")
