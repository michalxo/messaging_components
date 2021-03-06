import re
import logging
from enum import Enum
from iqa_common.executor import Command, Execution, ExecutorAnsible, CommandAnsible, Executor
from messaging_abstract.component import Service, ServiceStatus


class ServiceSystemInit(Service):
    """
    Implementation of a systemd or initd service used to manage a Server component.
    """

    _logger = logging.getLogger(__name__)

    def __init__(self, name: str, executor: Executor):
        super().__init__(name, executor)

    class ServiceSystemState(Enum):
        STARTED = ('start', 'started')
        STOPPED = ('stop', 'stopped')
        RESTARTED = ('restart', 'restarted')
        ENABLED = ('enable', 'enabled')
        DISABLED = ('disable', 'disabled')

        def __init__(self, system_state, ansible_state):
            self.system_state = system_state
            self.ansible_state = ansible_state

    def status(self) -> ServiceStatus:
        """
        Returns the service status based on linux service.
        :return: The status of this specific service
        :rtype: ServiceStatus
        """
        # service output :
        # is running
        # is stopped

        # systemctl output:
        # (running)
        # (dead)

        # On RHEL7> service is automatically redirected to systemctl
        cmd_status = Command(['service', self.name, 'status'], stdout=True, timeout=self.TIMEOUT)
        execution = self.executor.execute(cmd_status)

        if not execution.read_stdout():
            ServiceSystemInit._logger.debug("Service: %s - Status: FAILED" % self.name)
            return ServiceStatus.FAILED

        service_output = execution.read_stdout()

        if re.search('(is running|\(running\)|Running)', service_output):
            ServiceSystemInit._logger.debug("Service: %s - Status: RUNNING" % self.name)
            return ServiceStatus.RUNNING
        elif re.search('(is stopped|\(dead\)|Stopped)', service_output):
            ServiceSystemInit._logger.debug("Service: %s - Status: STOPPED" % self.name)
            return ServiceStatus.STOPPED

        ServiceSystemInit._logger.debug("Service: %s - Status: UNKNOWN" % self.name)
        return ServiceStatus.UNKNOWN

    def start(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceSystemState.STARTED))

    def stop(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceSystemState.STOPPED))

    def restart(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceSystemState.RESTARTED))

    def enable(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceSystemState.ENABLED))

    def disable(self) -> Execution:
        return self.executor.execute(self._create_command(self.ServiceSystemState.DISABLED))

    def _create_command(self, service_state: ServiceSystemState):
        """
        Creates a Command instance based on executor type and state
        that is specific to each type of command.
        :param service_state:
        :return:
        """
        if isinstance(self.executor, ExecutorAnsible):
            state = service_state.ansible_state
            return CommandAnsible('name=%s state=%s' % (self.name, state),
                                  ansible_module='service',
                                  stdout=True,
                                  timeout=self.TIMEOUT)
        else:
            state = service_state.system_state
            return Command(['service', self.name, state], stdout=True, timeout=self.TIMEOUT)
