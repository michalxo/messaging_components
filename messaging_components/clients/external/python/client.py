from autologging import logged, traced
from iqa_common.executor import Executor
from messaging_abstract.component.client import ClientExternal, Node
import messaging_components.protocols as protocols


@logged
@traced
class ClientPython(ClientExternal):
    """Python Proton client (base abstract class)."""

    supported_protocols = [protocols.Amqp10()]
    implementation = 'Python Proton client'
    version = '1.0.1'

    def __init__(self, name: str, node: Node, executor: Executor):
        super(ClientPython, self).__init__(name, node, executor)
