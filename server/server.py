from .serverproxy import ServerProxy
from .ipc import IPC
from .router import Router
from config.configmanager import ConfigManager
from typing import List
from queue import Queue
from .test import AbstractTest
from copy import copy
from concurrent.futures import ThreadPoolExecutor


class Server(ServerProxy):
    """" The great runtime server for all tests and more.
    This static class with class methods will be usually run as daemon on the main server.
    It is used to control the other routers, flash the firmwares and execute such as evaluate the tests.
    The web server and cli instances are connecting with this class
    and using his inherit public methods of ServerProxy.
    """""
    DEBUG = False
    VLAN = True
    CONFIG_PATH = "../config"
    _ipc_server = IPC()

    # runtime vars
    _routers = []
    _reports = Queue()
    # TODO reichen Threads aus? oder müssen es Prozesse sein wegen VLAN?
    executor = None

    @classmethod
    def start(cls, debug_mode: bool = False, config_path: str = CONFIG_PATH, vlan_activate: bool=True) -> None:
        """
        Starts the runtime server with all components
        :param debug_mode: Sets the log and print level
        :param config_path: Path to an alternative config directory
        :param vlan_activate: Activates/Deactivates VLANs
        """
        cls.DEBUG = debug_mode

        cls.CONFIG_PATH = config_path

        cls.VLAN = vlan_activate

        cls.__load_configuration()

        if cls.VLAN:
            from util.router_info import RouterInfo
            RouterInfo.update(cls.get_routers())

        print("Runtime Server started")

        cls.executor = ThreadPoolExecutor(max_workers=len(cls._routers))

        cls._ipc_server.start_ipc_server(cls, True)  # serves forever - works like a while(true)

        # at this point all code will be ignored

    @classmethod
    def __load_configuration(cls):
        # (re)load the configuration only then no tests are running
        assert len(cls.get_running_tests) == 0
        cls._routers = ConfigManager.get_router_auto_list()
        assert len(cls._routers) != 0
        assert len(cls._reports) == 0

    @classmethod
    def stop(cls) -> None:
        """
        Stops the server, all running tests and closes all connections.
        """
        cls._ipc_server.shutdown()
        pass

    @classmethod
    def get_router_by_id(cls, router_id: int) -> Router:
        for router in cls._routers:
            if router.get_id() == router_id:
                return router

    @classmethod
    def get_test_by_name(cls, test_name: str) -> AbstractTest:
        # TODO test verwaltung
        pass

    @classmethod
    def start_test(cls, router_id: int, test_name: str) -> bool:
        """Start an specific test on an router
        :param router_id: The id of the router on which the test will run
        :param test_name: The name of the test to execute
        :return: True if start was successful
        """
        router = cls.get_router_by_id(router_id)
        return cls.__start_test(router, test_name)

    @classmethod
    def __start_test(cls, router: Router, test: AbstractTest) -> bool:
        if router.running_tests is None:
            if test is None:
                if len(router.waiting_tests) != 0:
                    test = router.waiting_tests.get()
                else:
                    test = copy.deepcopy(cls.get_test_by_name(test))
                router.running_tests = test
                task = cls.executor.submit(cls.__execute_test, test, router)
                task.add_done_callback(cls.__start_test, router, None)
                test.thread = task
                return True
        else:
            router.waiting_tests.put(test)
            return False

    @classmethod
    def __execute_test(cls, test: AbstractTest, router: Router):
        test.prepare(router)
        result = test.run()
        cls._reports.put(result)
        router.running_tests = None

    @classmethod
    def get_routers(cls) -> List[Router]:
        """
        :return: List of known routers. List is a copy of the original list.
        """

        # check if list is still valid
        for router in cls._routers:
            assert isinstance(router, Router)

        return cls._routers.copy()

    @classmethod
    def get_running_tests(cls) -> List[AbstractTest]:
        """
        :return: List of running test on the test server. List is a copy of the original list.
        """
        # TODO exist now in router
        return cls._runningTests.copy()

    @classmethod
    def get_reports(cls) -> []:
        """
        :return: List of reports
        """
        return cls._reports

    @classmethod
    def get_tests(cls) -> List[AbstractTest]:
        """
        :return: List of available tests on the server
        """
        # TODO get available test from config
        pass

    @classmethod
    def get_firmwares(cls) -> []:
        """
        :return: List of known firmwares
        """
        # TODO vllt vom config?
        pass