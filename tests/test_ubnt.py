import unittest
import util.ubnt


class MyTestCase(unittest.TestCase):
    def test_create_power_strip(self):
        global ps
        ps = util.ubnt.Ubnt("vlanpowerstrip", 20, "192.168.1.20", 24, "ubnt", "ubnt", 6)
        assert isinstance(ps, util.ubnt.Ubnt)

        assert ps.ip == "192.168.1.20"
        assert ps.usr_name == "ubnt"
        assert ps.usr_password == "ubnt"
        assert ps.ip_mask == 24
        assert ps.vlan_iface_name == "vlanpowerstrip"
        assert ps.vlan_iface_id == 20
        assert ps.n_ports == 6

    def test_power(self):
        ps.up(1)
        assert ps.port_status(1) == 1
        ps.down(5)
        assert ps.port_status(5) == 0

if __name__ == '__main__':
    unittest.main()
