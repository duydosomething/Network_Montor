# coding=utf-8
# ---------------------------------------------------------------------------
# Author : Kelvin You
# Email  : weyou@cisco.com
# Date   : 8/21/2012
# ---------------------------------------------------------------------------
import os, io, gzip, glob, json, base64
import httplib2
import logging
logger = logging.getLogger('jnapclient')


class JnapException(Exception):
    """Exception raised by JnapClient"""
    pass


class JnapClient(object):

    """A Python implementation for JNAP client. This client fully support the
    JNAP protocol.  JNAP transaction mode is also supported.

    :param list serviceNames:
        A service list to be loaded. If not specified, all the service
        will be loaded
    :param path descriptorPlace:
        The folder which holds the JNAP descriptor files(default:jnapdefs)
    :param string descriptors:
        A dict of descriptors in JSON format. The key is service name.
        The parameter serviceNames and descriptorPlace will be ignored if
        this parameter is specified.
    Other keyword arguments are the same as the method :py:func:`configure`
    """

    DEFAULT_CONFIG = dict(
        username='',
        password='',
        timeout=30,
        allow_illegalvalue=False,
        suppress_exception=False,
        enable_compress=True,
        compress_threshold=512 * 2 ** 10
    )

    PYJNAP_TYPE_MAP = dict(
        bool=bool,
        string=unicode,
        int=int,
        DateTime=unicode,
        IPAddress=unicode,
        IPv6Address=unicode,
        MACAddress=unicode,
        UUID=unicode
    )

    __slots__ = (
        "_services", "_serviceNames", "_cacheDescriptor",
        "_actionQueue", "_http", "_cleanQueueBeforePush",
        "url", "username", "password", "timeout",
        "sslcert", "sslkeypwd",
        "allow_set_illegalvalue", "allow_get_illegalvalue",
        "suppress_exception", "enable_compress", "compress_threshold"
    )

    def __init__(self, serviceNames=None, descriptorPlace=None,
                  descriptors=None, **kwargs):
        """
        :param list serviceNames:
            A list stores the service names which this client will communicate
            with. If the description file is html document, this is a html file
            name list.
        :param string descriptorPlace:
            A directory which stores the JNAP description file in html or json
            format.
        :param string descriptors:
            A dict of descriptors in JSON format. The key is service name.
            The parameter serviceNames and descriptorPlace will be ignored if
            this parameter is specified.
        """

        self._services = {}
        self._cacheDescriptor = {}
        self._actionQueue = []
        self._cleanQueueBeforePush = True

        self.url = None
        """The JNAP service URL address (default: None)
        The service URL must be provided before using the JNAP client."""

        self.username = ''
        """User name required by the JNAP service (default: None)"""

        self.password = ''
        """Password required by the JNAP service (default: None)"""

        self.timeout = 30
        """ Maximum time in seconds that allow the JNAP connection to the
        server to take.  (default: 30)"""

        self.sslcert = None
        """The pathname of certificate file (\*.PEM) for SSL connection.
        (default: None)

        The *PEM* file must contain the private key.
        This property is required for *bi-direction* authentication. """

        self.sslkeypwd = None
        """The passphase of the encrypted private key.(default: None)

        This property is not required if the private key is plain text in
        the certificate.

        This option reserved for future. It has not been implemented.
        """

        self.allow_set_illegalvalue = False
        """Allow illegal value to be set to the parameter of JNAP request.
        (defualt: False)

        The illegal value contains:

           * Wrong data type
           * Value is not in the enumeration
           * Value is out of the range
           * Value *None*
        """

        self.allow_get_illegalvalue = False
        """Allow illegal value is in the parameter of the JNAP
        response. (defualt: False). The illegal value refers to
        :py:attr:`allow_set_illegalvalue`

        Note: The corrupted JSON document will cause a exception raise even
        this option is set to True.
        """

        self.suppress_exception = False
        """When the runtime exception happened. Return the code
        "_ErrorRuntime" instead of raising runtime exception. (defualt:
        False)

        The exception includes the following situations:

        * Connection issue
        * Malformed JSON response
        """

        self.enable_compress = True
        """Compress the JNAP request with gzip before send it.
        This option may reduce the transimission time for the large JNAP
        request. (default: True)

        This option requires the JNAP server support
        """

        self.compress_threshold = 512 * 2 ** 10
        """The JNAP request larget than this value will be compressed.
        (default: 524288/512K)

        Only available when :py:attr:`enable_compress` is True.
        """

        if descriptors is None:
            self._serviceNames = serviceNames
            if descriptorPlace is None:
                descriptorPlace = os.path.join(
                    os.path.dirname(__file__), 'jnapdefs')

            self._loadDescriptorFiles(descriptorPlace)
        else:
            self._loadDescriptors(descriptors)

        self.configure(**kwargs)

        self._http = httplib2.Http()
        self._http.follow_redirects = True
        self._http.follow_all_redirects = True

    def __del__(self):
        pass

    def __setattr__(self, name, value):
        # set the attribute to None to reset the value to default
        defaultConfig = self.DEFAULT_CONFIG

        if name in defaultConfig and value is None:
            value = defaultConfig[name]

        super(JnapClient, self).__setattr__(name, value)

    def _loadDescriptors(self, descriptors):
        for service, jsonDescriptor in descriptors.items():
            self._services[service] = json.loads(jsonDescriptor)

        self._serviceNames = list(self._services.keys())
        logger.debug("Loaded services: {0}".format(self._serviceNames))

    def _loadDescriptorFiles(self, descriptorPlace):
        self._services = {}
        if not os.path.isabs(descriptorPlace):
            descriptorPlace = os.path.join(os.getcwd(), descriptorPlace)

        if self._serviceNames is None:
            # load all the supported services
            dpt_wc = os.path.join(descriptorPlace, '*')
            for fname in glob.glob(dpt_wc):
                if fname.endswith(".html"):
                    from .doccompiler import parseHtmlDoc
                    services = parseHtmlDoc(fname)
                    self._services.update(services)

                elif fname.endswith(".json"):
                    service = os.path.basename(fname).rsplit('.', 1)[0]
                    with open(fname) as fd:
                        self._services[service] = json.load(fd)

            self._serviceNames = list(self._services.keys())
            if not self._services:
                raise JnapException(
                    "Not find any descriptor file or JNAP service in {}"
                    .format(descriptorPlace)
                )
        else:
            for service in self._serviceNames:
                service = service.lower()
                docfile = os.path.join(descriptorPlace, service + '.html')
                dptfile = os.path.join(descriptorPlace, service + '.json')

                if os.path.isfile(docfile):
                    services = parseHtmlDoc(docfile)
                    self._services.update(services)
                elif os.path.isfile(dptfile):
                    with open(dptfile) as fd:
                        self._services[service] = json.load(fd)
                else:
                    raise JnapException(
                        "Not find descriptor file for service '{0}'"
                        .format(service)
                    )
        logger.debug("Loaded services: {0}".format(self._serviceNames))

    def _getDescriptor(self, action):
        """returns (actionDpt, structsDpt, enumsDpt)
        :param string action: refer to :py:func:`getRequest`
        """
        descriptor = self._cacheDescriptor.get(action, None)
        if descriptor:
            return descriptor

        if action.find('://') != -1:
            # the action name contains name space
            actionName = action.rsplit("/", 1)[1]
            for service, serviceDpt in self._services.items():
                if 'actions' not in serviceDpt:
                    continue

                if actionName in serviceDpt['actions']:
                    actionDpt = {
                        'name': '', 'input': {}, 'output': {}, 'result': {}}

                    actionDpt.update(serviceDpt['actions'][actionName])
                    if actionDpt['name'] == action:
                        structsDpt = serviceDpt.get('structs', {})
                        enumsDpt = serviceDpt.get('enums', {})

                        self._cacheDescriptor[action] = \
                            (actionDpt, structsDpt, enumsDpt)
                        return actionDpt, structsDpt, enumsDpt
            else:
                raise JnapException(
                    "Not find the action '{0}' from services: {1}"
                    .format(action, ', '.join(self._serviceNames))
                )
        else:
            actionDpt = {'name': '', 'input': {}, 'output': {}, 'result': {}}

            # find the action name from all the services
            if action.find('.') != -1:
                # the action contains the service name
                serviceName, actionName = action.split('.')
                serviceName = serviceName.lower()

                if serviceName in self._services:
                    serviceDpt = self._services[serviceName]

                    if 'actions' in serviceDpt and \
                            actionName in serviceDpt['actions']:
                        actionDpt.update(serviceDpt['actions'][actionName])
                        structsDpt = serviceDpt.get('structs', {})
                        enumsDpt = serviceDpt.get('enums', {})

                        self._cacheDescriptor[action] = \
                            (actionDpt, structsDpt, enumsDpt)
                        return actionDpt, structsDpt, enumsDpt

                    raise JnapException(
                        "The action '{0}' doesn't defined in service '{1}'"
                        .format(actionName, serviceName)
                    )

                raise JnapException(
                    "The service '{0}' is not loaded for this client"
                    .format(serviceName)
                )
            else:
                actionName = action
                for service, serviceDpt in self._services.items():
                    if 'actions' not in serviceDpt:
                        continue

                    if actionName in serviceDpt['actions']:
                        actionDpt.update(serviceDpt['actions'][actionName])
                        structsDpt = serviceDpt.get('structs', {})
                        enumsDpt = serviceDpt.get('enums', {})

                        self._cacheDescriptor[action] = \
                            (actionDpt, structsDpt, enumsDpt)
                        return actionDpt, structsDpt, enumsDpt
                else:
                    raise JnapException(
                        "Not find the action '{0}' from services: {1}"
                        .format(action, ', '.join(self._serviceNames))
                    )

    def _checkEnumValue(self, paramValue, enumDpt, paramPath):
        if paramValue not in enumDpt:
            raise JnapException(
                "Parameter '{0}': value '{1}' is out of enumeration [{2}]"
                .format('.'.join(paramPath),
                        paramValue, ', '.join(enumDpt.keys()))
            )

    def _checkSimpleValue(self, paramValue, dataType, paramPath):
        if dataType in self.PYJNAP_TYPE_MAP:
            pytype = self.PYJNAP_TYPE_MAP[dataType]
        else:
            raise JnapException(
                "Parameter '{0}': unrecognized type name '{1}'"
                .format('.'.join(paramPath), dataType)
            )
        vtype = type(paramValue)

        if vtype != pytype:
            raise JnapException(
                "Parameter '{0}': type of value '{1}' should be {2}, "
                "but got {3}".format(
                    '.'.join(paramPath), paramValue,
                    pytype.__name__, vtype.__name__)
            )

    def _checkParameterValue(self, paramValues, paramsDpt, structsDpt,
                             enumsDpt, _paramPath=[]):
        """Check the parameter value of JNAP action"""

        for param, paramDpt in paramsDpt.items():
            paramPath = _paramPath + [param]
            value = paramValues.get(param, None)

            if value is None:
                if paramDpt['optional']:
                    # ignore the optional parameter if the value is None
                    if param in paramValues:
                        del paramValues[param]
                    continue
                else:
                    raise JnapException(
                        "Parameter '{0}' is not optional, value"
                        " is required".format(param))

            dtype = paramDpt['type']
            if paramDpt['array']:
                if type(value) in (list, tuple):
                    index = 0
                    for subValue in value:
                        subParamPath = paramPath + [str(index)]
                        if dtype in structsDpt:
                            self._checkParameterValue(
                                subValue, structsDpt[dtype], structsDpt,
                                enumsDpt, subParamPath)
                        elif dtype in enumsDpt:
                            self._checkEnumValue(
                                subValue, enumsDpt[dtype], subParamPath)
                        else:
                            self._checkSimpleValue(
                                subValue, dtype, subParamPath)
                        index += 1
                else:
                    raise JnapException(
                        "Parameter '{0}': type should be a tuple"
                        " or list, but got {1}".format(
                            '.'.join(paramPath), type(value))
                    )
            else:
                if dtype in structsDpt:
                    self._checkParameterValue(
                        value, structsDpt[dtype], structsDpt,
                        enumsDpt, paramPath)
                elif dtype in enumsDpt:
                    self._checkEnumValue(value, enumsDpt[dtype], paramPath)
                else:
                    self._checkSimpleValue(value, dtype, paramPath)

    def _sendRequest(self, action, data):
        """Send the JNAP request.

        :param string action:  full action name with namespace.
        :param string data: JSON request
        :returns: JNAP response data
        """
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-JNAP-Action': '"{0}"'.format(action),
            'Accept-Encoding': 'gzip,identity',
            'Connection': 'keep-alive',
            'Keep-Alive': '300',
            #'Connection': 'close'
        }

        if self.username or self.password:
            auth = base64.standard_b64encode("{0}:{1}".format(
                self.username, self.password).encode('utf-8')).decode('ascii')
            headers['X-JNAP-Authorization'] = 'Basic ' + auth

        if self.enable_compress and len(data) > self.compress_threshold:
            headers['Content-Encoding'] = 'gzip'
            bi = io.BytesIO()
            gf = gzip.GzipFile(fileobj=bi, compresslevel=5, mode="wb")
            gf.write(data.encode('utf-8'))
            gf.close()
            data = bi.getvalue()

        headers['Content-Length'] = str(len(data))
        self._http.timeout = self.timeout

        self._http.certificates.clear()
        if self.sslcert:
            self._http.add_certificate(self.sslcert, self.sslcert, "")

        response, soapData = self._http.request(
            self.url, method="POST", body=data, headers=headers)

        if response.status == 200:
            return soapData.decode('utf-8')
        else:
            raise JnapException(response.reason)

    def _getUsedStructNames(self, structsDpt, typeList):
        structNames = []
        findnew = False

        for name, struct in structsDpt.items():
            if name in typeList and name not in structNames:
                structNames.append(name)
                typeList.remove(name)

                for param, paramInfo in struct.items():
                    nextType = paramInfo['type']
                    if nextType not in typeList:
                        typeList.append(nextType)
                        findnew = True

        if findnew:
            structNames += self._getUsedStructNames(structsDpt, typeList)

        return structNames

    def _getUsedEnumNames(self, enumsDpt, typeList):
        enumNames = []
        for dtype in typeList:
            if dtype in enumsDpt:
                enumNames.append(dtype)

        return enumNames

    # ------------------------------------------------------------------------
    # Public Interfaces
    # ------------------------------------------------------------------------
    def configure(self, **kwargs):

        """Configure the options of JNAP client.

        :param string url:
            Refer to attribute :py:attr:`url`
        :param string username:
            Refer to attribute :py:attr:`username`
        :param string password:
            Refer to attribute :py:attr:`password`
        :param number timeout:
            Refer to attribute :py:attr:`timeout`
        :param path sslcert:
            Refer to attribute :py:attr:`sslcert`
        :param string sslkeypwd:
            Refer to attribute :py:attr:`sslkeypwd`
        :param bool allow_set_illegalvalue:
            Refer to attribute :py:attr:`allow_set_illegalvalue`
        :param bool allow_get_illegalvalue:
            Refer to attribute :py:attr:`allow_get_illegalvalue`
        :param bool suppress_exception:
            Refer to attribute :py:attr:`suppress_exception`
        :param bool enable_compress:
            Refer to attribute :py:attr:`enable_compress`
        :param bool compress_threshold:
            Refer to attribute :py:attr:`compress_threshold`

        ``Note: Set any parameter to None will cause the parameter reset to
        default value. All above configurations can be set/get from the
        instance property with the same name.``
        """
        for prop, value in kwargs.items():
            setattr(self, prop, value)

    def getConfig(self, *args):
        """Return a list that contains the value of the requested
        configurations. The argument is a name list of configurations. It's
        the same as the method :py:func:`configure`

        :returns: list of values

        Example::

            >>> timeout, username = client.getConfig('timeout', 'username')
            >>> print(timeout, username)
        """
        values = []

        for prop in args:
            values.append(getattr(self, prop))

        return values

    def makeRequest(self, action, **kwargs):
        """Get the JNAP request payload data (JSON) from Python Style
        parameters.

        :param string action:
            Action name, refer to method :py:func:`call`
        :param kwargs:
            Python Style JNAP Parameters, refer to method :py:func:`call`
        :returns:
            A tuple of (<action-name>, <request-json>). The action-name
            is the full name of the action.
        :exception:
            :py:class:`JnapException` will be raised if there is any error
             with the parameters
        """

        actdpt, structs, enums = self._getDescriptor(action)
        if not self.allow_set_illegalvalue:
            self._checkParameterValue(kwargs, actdpt['input'], structs, enums)

        try:
            jsonRequest = json.dumps(kwargs)
        except Exception as e:
            raise JnapException("Make request error: {0}".format(e))

        return actdpt['name'], jsonRequest

    def parseResponse(self, action, jsonResponse):
        """Parse and validate the data returned by JNAP server

        :param string action:
            Action name, refer to method :py:func:`call`
        :param string jsonResponse:
            The JSON document which is returned by JNAP server
        :returns: a Python object composed of a list/tuple/dict
        :exception:
            :py:class:`JnapException` will be raised if there is any error
            with the responsed parameters.
        """
        actdpt, structs, enums = self._getDescriptor(action)

        try:
            jnapResult = json.loads(jsonResponse)
        except Exception as e:
            raise JnapException("Parse response error: {0}".format(e))

        result = jnapResult.get('result', None)

        if result is None:
            raise JnapException(
                "Parse response error: not find 'result' parameter")

        if result == 'OK' and actdpt['output']:
            output = jnapResult.get('output', None)
            if  output is None:
                raise JnapException(
                    "Parse response error: not find 'output' parameter")

            if not self.allow_get_illegalvalue:
                self._checkParameterValue(output,
                                          actdpt['output'], structs, enums)

        return jnapResult

    def rawCall(self, action, jsonRequest):
        """Call JNAP action with raw JSON data

        :param string action: Refer to :py:func:`call`
        :param string jsonRequest:
            JNAP request data in the form of JSON. It can be composed by
            :py:func:`makeRequest`
        :returns:
            JNAP response represents as a JSON string. It can be convert to
            Python object with function :py:func:`parseResponse`
        :exception: Any error will cause the :py:class:`JnapException` raised
        """
        if self.url is None:
            raise JnapException("JNAP service url doesn't specified.")

        actdpt, structs, enums = self._getDescriptor(action)

        action = actdpt['name']
        logger.debug("Execute action: {0}".format(action))
        logger.debug("JNAP request:\n{0}".format(jsonRequest))

        try:
            jsonResponse = self._sendRequest(action, jsonRequest)
            logger.debug("Got response:\n{0}".format(jsonResponse))
        except Exception as e:
            logger.error("An exeption is raised: {0}".format(e))
            if self.suppress_exception:
                return json.dumps(
                    {'result': '_ErrorRuntime', 'error': str(e)})
            else:
                raise JnapException(str(e))

        return jsonResponse

    def call(self, action, **kwargs):
        """Call JNAP action with Python Style JNAP Parameters

        :param string action:
            the name of the action,  it has 3 forms:

            * action-name
            * <service-name>.action-name
            * <namespace>.action-name

        :param kwargs: Python Style JNAP Parameters:

            ============  ===========  ==========  ==========================
            JNAP           JSON        Python      Description
            ============  ===========  ==========  ==========================
            bool           true/false  bool        Boolean
            int            number      int         32-bit signed integer
            string         string      unicode     Unicode string
            datetime       string      unicode     date/time
            IPAddress      string      unicode     IPv4 address
            IPv6Address    string      unicode     IPv6 address
            MACAddress     string      unicode     MAC address
            UUID           string      unicode     UUID
            enum           string      unicode     enumeration value
            array          array       list/tuple  ordered list of values
            struct         object      dict        unordered dictionary of
                                                   name/value pairs
            ============  ===========  ==========  ==========================

            If :py:attr:`allow_get_illegalvalue` is true, a value *None* is
            assigned to an optional parameter, the parameter will be ignored.

        :returns: JNAP response represents as a Python object.
        :exception: Any error will cause the :py:class:`JnapException` raised

        Example::

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

            objResponse = client.call(
                'SetRoutingSettings',
                isNATEnabled = True,
                isDynamicRoutingEnabled = False,
                entries = [staticRoute1, staticRoute2])

        """

        _, jsonRequest = self.makeRequest(action, **kwargs)
        jsonResponse = self.rawCall(action, jsonRequest)

        try:
            resultObj = self.parseResponse(action, jsonResponse)
        except Exception as e:
            logger.error("An exeption is raised: {0}".format(e))
            if self.suppress_exception:
                return {'result': '_ErrorRuntime', 'error': str(e)}
            else:
                raise JnapException(str(e))

        return resultObj

    def transactionReset(self):
        """Set the transaction queue to empty"""
        self._actionQueue = []

    def transactionPush(self, action, **kwargs):
        """Push a action to the transaction queue

        :param string action:
            Action name, refer to method :py:func:`call`
        :param kwargs:
            Python Style JNAP Parameters, refer to method :py:func:`call`
        """
        if self._cleanQueueBeforePush:
            self._actionQueue = []
            self._cleanQueueBeforePush = False

        actionName, _ = self.makeRequest(action, **kwargs)

        self._actionQueue.append(dict(
            action=actionName,
            request=kwargs
        ))

    def transactionCall(self):
        """Call the JNAP transaction.

        Example::

            client.transactionReset()
            client.transactionPush('GetGuestNetworkSettings')
            client.transactionPush(
                'SetMACAddressCloneSettings',
                isMACAddressCloneEnabled = False)

            response = client.transactionCall()
        """
        self._cleanQueueBeforePush = True

        if self.url is None:
            raise JnapException("JNAP service url doesn't specified.")

        action = 'http://linksys.com/jnap/core/Transaction'
        logger.debug("Execute transaction: {0}".format(action))

        try:
            jsonRequest = json.dumps(self._actionQueue)
        except Exception as e:
            raise JnapException(
                "Make transaction request error: {0}".format(e))
        logger.debug("JNAP request:\n{0}".format(jsonRequest))

        try:
            jsonResponse = self._sendRequest(action, jsonRequest)
            logger.debug("Got response:\n{0}".format(jsonResponse))

            jnapResult = json.loads(jsonResponse)
            result = jnapResult.get('result', None)

            if result is None:
                raise JnapException(
                    "Parse response error: not find 'result' parameter")

            if result == 'OK':
                responses = jnapResult.get('responses', None)
                if responses is None:
                    raise JnapException(
                        "Parse response error: not find 'responses' parameter")

        except Exception as e:
            logger.error("An exeption is raised: {0}".format(e))
            if self.suppress_exception:
                return json.dumps(
                    {'result': '_ErrorRuntime', 'error': str(e)})
            else:
                raise JnapException(str(e))

        return jnapResult

    def getHelp(self, action):
        """Return the help information for a specified JNAP action

        Here is the information example::

            [Overview]
              http://cisco.com/jnap/firewall/GetPortRangeForwardingRules
              This action gets the list of port range forwarding rules
              currently set on the router.

            [Prototype]
              GetPortRangeForwardingRules() => maxDescriptionLength, maxRules,
              rules
            [Input Parameters]
              None
            [Output Parameters]
              rules  : PortRangeForwardingRule[]
                     The current list of port range forwarding rules.
              maxDescriptionLength:  int
                     The maximum length, in bytes, of the description member
                     of a port range forwarding rule.
              maxRules: int [optional]
                     The maximum number of port range forwarding rules that
                     can exist simultaneously.
            [Return Values]
              OK :  Success.
              _ErrorAbortedAction: -
            [Structures]
               struct PortRangeForwardingRule:
                 isEnabled:  bool
                     Whether the rule is enabled.
                 firstExternalPort: int
                     The first external port in the range that should be
                     forwarded. This value must be between 0 and 65535.
                 lastExternalPort: int
                     The last external port in the range that should be
                     forwarded. This value must be between 0 and 65535.
                  protocol: ....
            [Enumerates]
             ...
        """
        actdpt, structs, enums = self._getDescriptor(action)

        h = []

        h.append("[Overview]")
        h.append("  {0}".format(actdpt['name']))
        h.append("  {0}".format(actdpt['desc']))

        h.append("\n[Prototype]")
        prototype = '  {0}({1}) => '.format(action, ', '.join(actdpt['input']))
        if actdpt['output']:
            prototype += ', '.join(actdpt['output'])
        else:
            prototype += "None"
        h.append(prototype)

        typeList = []
        for cls in ['input', 'output']:
            if actdpt.get(cls, None):
                h.append("\n[{0} Parameters]".format(cls.capitalize()))

                for param, paramInfo in actdpt[cls].items():
                    dtype = paramInfo['type']
                    if paramInfo['array']:
                        dtype += "[]"

                    typeList.append(paramInfo['type'])

                    if paramInfo['optional']:
                        optstr = "[optional]"
                    else:
                        optstr = ""

                    h.append(" - {0}: {1} {2}".format(param, dtype, optstr))
                    if paramInfo['desc'] != "":
                        h.append("     {0}".format(paramInfo['desc']))

        h.append("\n[Return Values]")
        if actdpt.get('result', None):
            resultInfo = actdpt['result']
            for retcls in ['success', 'errors']:
                for value, desc in resultInfo[retcls].items():
                    if desc == "":
                        desc = "-"

                    h.append("  {0}: {1}".format(value, desc))

        else:
            h.append("  None")

        usedStructs = self._getUsedStructNames(structs, typeList)
        if usedStructs:
            h.append("\n[Struct Definition]")
            for structName in usedStructs:
                h.append("  struct {0}:".format(structName))
                for param, paramInfo in structs[structName].items():
                    dtype = paramInfo['type']
                    if paramInfo['array']:
                        dtype += "[]"

                    if paramInfo['optional']:
                        optstr = "[optional]"
                    else:
                        optstr = ""

                    h.append("    - {0}: {1} {2}".format(param, dtype, optstr))
                    if paramInfo['desc'] != "":
                        h.append("       {0}".format(paramInfo['desc']))

        usedEnums = self._getUsedEnumNames(enums, typeList)
        if usedEnums:
            h.append("\n[Enumerate Definition]")
            for enumName in usedEnums:
                h.append("  enum {0}:".format(enumName))
                for value, desc in enums[enumName].items():
                    if desc == "":
                        desc = "-"
                    h.append("    {0}: {1}".format(value, desc))

        return '\n'.join(h)
