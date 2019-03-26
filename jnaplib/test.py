# run test with command: 
# $ cd <parent folder of jnaplib>
# $ python -m jnaplib.test -v
import jnaplib
import unittest, logging
logger = logging.getLogger('jnaplib')

formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s', datefmt="%H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


JSONRequest = '{"isNATEnabled": true, "isDynamicRoutingEnabled": false, "entries": [{"name": "route1", "settings": {"interface": "LAN", "networkPrefixLength": 24, "gateway": "192.168.1.20", "destinationLAN": "172.16.20.0"}}, {"name": "route2", "settings": {"interface": "LAN", "networkPrefixLength": 24, "gateway": "192.168.1.21", "destinationLAN": "172.16.21.0"}}]}'
JSONResponse = '''{
    "result" : "OK",
    "output" : {
        "maxDescriptionLength": 32,
        "maxRules": 10,
        "rules": [{
            "isEnabled": true,
            "externalPort": 8000,
            "protocol": "Both",
            "internalServerIPAddress": "192.168.1.100",
            "internalPort": 9000,
            "description": "single port forwarding 1"
        }, {
            "isEnabled": false,
            "externalPort": 2000,
            "protocol": "TCP",
            "internalServerIPAddress": "192.168.1.200",
            "internalPort": 1000,
            "description": "single port forwarding 2"
        }]
    }
}'''

JSONResponse_ERROR = '''{
    "result" : "OK",
    "output" : {
        "maxDescriptionLength": 32,
        "maxRules": 10,
        "rules": [{
            "isEnabled": true,
            "externalPort": 8000,
            "protocol": "Both",
            "internalServerIPAddress": "192.168.1.100",
            "internalPort": 9000,
            "description": "single port forwarding 1"
        }, {
            "isEnabled": false,
            "externalPort": "2000",
            "protocol": "TCP",
            "internalServerIPAddress": "192.168.1.201",
            "internalPort": 1000,
            "description": "single port forwarding 2"
        }]
    }
}'''

ForwardingRules = []
rule = dict(
    isEnabled = True,
    externalPort = 8000,
    protocol = "TCP",
    internalServerIPAddress = "192.168.1.200",
    internalPort = 4000,
    description = "rule1"
)
ForwardingRules.append(rule)
rule = dict(
    isEnabled = True,
    externalPort = 8001,
    protocol = "TCP",
    internalServerIPAddress = "192.168.1.201",
    internalPort = 4000,
    description = "rule2"
)
ForwardingRules.append(rule)

class JnapTestCase(unittest.TestCase):
    def setUp(self):
        self.jnap = jnaplib.JnapClient()
        self.jnap.configure(url="http://192.168.1.1/JNAP/", username="admin", password="admin")

    def tearDown(self):
        pass

    def test_makeRequest(self):
        response = self.jnap.makeRequest('SetGuestNetworkSettings',
                    isGuestNetworkEnabled = True,
                    broadcastGuestSSID = False,
                    guestSSID = 'my-guest-ssid',
                    guestPassword = 'guest-password',
                    maxSimultaneousGuests = 5)

        self.assertEqual(response, 
            ('http://cisco.com/jnap/guestnetwork/SetGuestNetworkSettings', 
             '{"broadcastGuestSSID": false, "guestSSID": "my-guest-ssid", "maxSimultaneousGuests": 5, "isGuestNetworkEnabled": true, "guestPassword": "guest-password"}'))

    def test_makeRequest_withArray(self):
        staticRoute1 = dict(
            name = 'route1',
            settings = dict(
                interface = 'LAN',
                destinationLAN = '172.16.20.0',
                networkPrefixLength = 24,
                gateway = '192.168.1.20'
            )
        )

        staticRoute2 = {
            'name': 'route2',
            'settings': {
                'interface': 'LAN',
                'destinationLAN': '172.16.21.0',
                'networkPrefixLength': 24,
                'gateway': '192.168.1.21'
            }
        }

        response = self.jnap.makeRequest(
            'SetRoutingSettings',
            isNATEnabled = True,
            isDynamicRoutingEnabled = False,
            entries = [staticRoute1, staticRoute2])

        self.assertEqual(response, 
            ('http://cisco.com/jnap/router/SetRoutingSettings', 
            '{"isNATEnabled": true, "isDynamicRoutingEnabled": false, "entries": [{"name": "route1", "settings": {"interface": "LAN", "networkPrefixLength": 24, "gateway": "192.168.1.20", "destinationLAN": "172.16.20.0"}}, {"name": "route2", "settings": {"interface": "LAN", "networkPrefixLength": 24, "gateway": "192.168.1.21", "destinationLAN": "172.16.21.0"}}]}'))       


    def test_makeRequest_withOptional(self):
        response = self.jnap.makeRequest('SetMACAddressCloneSettings',
            isMACAddressCloneEnabled = False)
        self.assertEqual(response, ('http://cisco.com/jnap/router/SetMACAddressCloneSettings', '{"isMACAddressCloneEnabled": false}'))

        response = self.jnap.makeRequest('SetMACAddressCloneSettings',
            isMACAddressCloneEnabled = False,
            macAddress = None)
        self.assertEqual(response, ('http://cisco.com/jnap/router/SetMACAddressCloneSettings', '{"isMACAddressCloneEnabled": false}'))

    def test_makeRequest_exception_1(self):
        self.assertRaises(
            jnaplib.JnapException,
            self.jnap.makeRequest,
            'SetGuestNetworkSettings',
            isGuestNetworkEnabled = True,
            broadcastGuestSSID = False,
            guestSSID = 'my-guest-ssid',
            guestPassword = 'guest-password',
            maxSimultaneousGuests = "5")

    def test_makeRequest_exception_2(self):
        self.assertRaises(
            jnaplib.JnapException,
            self.jnap.makeRequest,
            'SetGuestNetworkSettings',
            isGuestNetworkEnabled = 1,
            broadcastGuestSSID = False,
            guestSSID = 'my-guest-ssid',
            guestPassword = 'guest-password',
            maxSimultaneousGuests = 5)

    def test_makeRequest_exception_3(self):
        self.assertRaises(
            jnaplib.JnapException,
            self.jnap.makeRequest,
            'SetGuestNetworkSettings',
            isGuestNetworkEnabled = True,
            broadcastGuestSSID = False,
            guestSSID = True,
            guestPassword = 'guest-password',
            maxSimultaneousGuests = 5)

    def test_makeRequest_exception_4(self):
        self.assertRaises(
            jnaplib.JnapException,
            self.jnap.makeRequest,
            'SetGuestNetworkSettings',
            isGuestNetworkEnabled = True,
            broadcastGuestSSID = "SSID",
            guestSSID = "ssid",
            guestPassword = 'guest-password',
            maxSimultaneousGuests = 5)

    def test_makeRequest_exception_5(self):
        staticRoute1 = dict(
            name = 'route1',
            settings = dict(
                interface = 'LAN',
                destinationLAN = '172.16.20.0',
                networkPrefixLength = 24,
                gateway = '192.168.1.20'
            )
        )

        staticRoute2 = {
            'name': 'route2',
            'settings': {
                'interface': 'WAN',
                'destinationLAN': '172.16.21.0',
                'networkPrefixLength': 24,
                'gateway': '192.168.1.21'
            }
        }

        with self.assertRaises(jnaplib.JnapException) as cm:
            self.jnap.makeRequest(
                'SetRoutingSettings',
                isNATEnabled = True,
                isDynamicRoutingEnabled = False,
                entries = [staticRoute1, staticRoute2])

        self.assertEqual(str(cm.exception), "Parameter 'entries.1.settings.interface': value 'WAN' is out of enumeration [LAN, Internet]")

    def test_makeRequest_illegal(self):
        self.jnap.configure(allow_set_illegalvalue=True)
        response = self.jnap.makeRequest('SetGuestNetworkSettings',
                    isGuestNetworkEnabled = True,
                    broadcastGuestSSID = False,
                    guestSSID = 'my-guest-ssid',
                    guestPassword = 'guest-password',
                    maxSimultaneousGuests = "5")

        self.assertEqual(response, 
            ('http://cisco.com/jnap/guestnetwork/SetGuestNetworkSettings', 
             '{"broadcastGuestSSID": false, "guestSSID": "my-guest-ssid", "maxSimultaneousGuests": "5", "isGuestNetworkEnabled": true, "guestPassword": "guest-password"}'))

    def test_makeRequest_empty(self):
        response = self.jnap.makeRequest('GetGuestNetworkSettings')
        self.assertEqual(response, 
            ('http://cisco.com/jnap/guestnetwork/GetGuestNetworkSettings', '{}'))

    def test_parseResponse(self):
        obj = self.jnap.parseResponse('GetSinglePortForwardingRules', JSONResponse)
        self.assertEqual(obj['result'], 'OK')
        self.assertEqual(obj['output']['rules'][0]['internalPort'], 9000)
        self.assertEqual(obj['output']['rules'][1]['isEnabled'], False)
        self.assertEqual(len(obj['output']['rules']), 2)

    def test_parseResponse_exception_1(self):
        with self.assertRaises(jnaplib.JnapException) as cm:
            obj = self.jnap.parseResponse('GetSinglePortForwardingRules', JSONResponse_ERROR)

        self.assertEqual(str(cm.exception), "Parameter 'rules.1.externalPort': type of value '2000' should be int, but got str")

    def test_parseResponse_illegal(self):
        self.jnap.configure(allow_get_illegalvalue=True)
        obj = self.jnap.parseResponse('GetSinglePortForwardingRules', JSONResponse_ERROR)
        self.assertEqual(obj['result'], 'OK')
        self.assertEqual(obj['output']['rules'][1]['externalPort'], "2000")
        self.assertEqual(obj['output']['rules'][1]['isEnabled'], False)
        self.assertEqual(len(obj['output']['rules']), 2)

    def test_rawCall(self):
        jsonData = self.jnap.rawCall('SetRoutingSettings', JSONRequest)
        objResponse = self.jnap.parseResponse('SetRoutingSettings', jsonData)
        self.assertEqual( objResponse['result'], 'OK')

    def test_call(self):
        staticRoute1 = dict(
            name = 'route1',
            settings = dict(
                interface = 'LAN',
                destinationLAN = '172.16.20.0',
                networkPrefixLength = 24,
                gateway = '192.168.1.20'
            )
        )

        staticRoute2 = {
            'name': 'route2',
            'settings': {
                'interface': 'LAN',
                'destinationLAN': '172.16.21.0',
                'networkPrefixLength': 24,
                'gateway': '192.168.1.21'
            }
        }        

        objResponse = self.jnap.call(
            'SetRoutingSettings',                 
            isNATEnabled = True,
            isDynamicRoutingEnabled = False,
            entries = [staticRoute1, staticRoute2])

        self.assertEqual(objResponse['result'], 'OK')

    def test_call_withOptional(self):
        objResponse = self.jnap.call('SetMACAddressCloneSettings',
            isMACAddressCloneEnabled = True,
            macAddress = '00:0b:0b:0b:0b:0b')
        self.assertEqual(objResponse['result'], 'OK')

        objResponse = self.jnap.call('SetMACAddressCloneSettings',
            isMACAddressCloneEnabled = False)
        self.assertEqual(objResponse['result'], 'OK')

    def test_call_withArray(self):
        objResponse = self.jnap.call(
            'SetSinglePortForwardingRules',
            rules = ForwardingRules)
        self.assertEqual(objResponse['result'], 'OK')

    def test_call_withNamespace(self):
        objResponse = self.jnap.call(
            'http://cisco.com/jnap/firewall/SetSinglePortForwardingRules',
            rules = ForwardingRules)
        self.assertEqual(objResponse['result'], 'OK')

    def test_call_withService(self):
        objResponse = self.jnap.call(
            'firewall.SetSinglePortForwardingRules',
            rules = ForwardingRules)
        self.assertEqual(objResponse['result'], 'OK')

    def test_call_withoutInput(self):
        objResponse = self.jnap.call('GetSinglePortForwardingRules')
        self.assertEqual(objResponse['result'], 'OK')

    # server doesn't suppport now
    # def test_call_compress(self):
    #     # need check the packet
    #     self.jnap.compress_threshold = 0 # all the data will be compressed
    #     objResponse = self.jnap.call(
    #         'firewall.SetSinglePortForwardingRules',
    #         rules = ForwardingRules)
    #     self.assertEqual(objResponse['result'], 'OK')

    def test_call_illegal(self):
        objResponse = self.jnap.call('GetSinglePortForwardingRules', a=1, b=2, c="test", d=[1,2,3,4], e={'a':1, 'b':2, 'c':3})
        self.assertEqual(objResponse['result'], '_ErrorInvalidInput')

    def test_transaction(self):
        self.jnap.transactionPush('SetSinglePortForwardingRules', rules=ForwardingRules)
        self.jnap.transactionPush('GetSinglePortForwardingRules')
        self.jnap.transactionPush('SetMACAddressCloneSettings',
            isMACAddressCloneEnabled = False)
        objResponse = self.jnap.transactionCall()
        self.assertEqual(objResponse['result'], 'OK')
        self.assertEqual(objResponse['responses'][1]['output']['rules'], ForwardingRules)

    def test_transactionReset(self):
        self.jnap.transactionPush('SetSinglePortForwardingRules', rules=ForwardingRules)
        self.jnap.transactionPush('GetSinglePortForwardingRules')

        self.jnap.transactionReset()
        self.jnap.transactionPush('GetSinglePortForwardingRules')
        objResponse = self.jnap.transactionCall()
        self.assertEqual(objResponse['responses'][0]['output']['rules'], ForwardingRules)

    def test_getHelp(self):
        help = self.jnap.getHelp('SetRoutingSettings')
        # print(help)

        # help = self.jnap.getHelp('GetRoutingSettings')
        # print(help)        

if __name__ == '__main__':
    unittest.main()