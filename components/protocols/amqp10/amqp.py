from amom.message import Message
from amom.protocol import Protocol

"""

"""


class AMQP10(Protocol):
    """
    AMQP 1.0 Protocol implementation
    """
    def __init__(self):
        Protocol.__init__(
            self,
            message=Message(),
            transaction=NotImplementedError,
            transport=NotImplementedError,
            default_port=NotImplementedError
        )
    pass
