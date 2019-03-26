#!/bin/env python
# ============================================================================ #
#                   Copyright (c) 2012 by Linksys-Cisco Systems, Inc.          #
#                                  All Rights reserved                         #
# ============================================================================ #
# FILE NAME  :
#     jnapSpecParser
# DESCRIPTION:
#     A tool to generate the JNAP descriptors from JNAP documentation
# AUTHOR:
#     Kelvin You
# CREATION DATE:
#     22/Feb/2012
# Python verson
#     Python 3+
# ============================================================================ #

import os, sys, getopt, glob, re, logging
from lxml import etree
from collections import OrderedDict
logger = logging.getLogger('jnap-doc-compiler')

def valueToTclValue(value):
    """
    >>> valueToTclValue('abcd')
    'abcd'

    >>> valueToTclValue('ab cd')
    '{ab cd}'

    >>> valueToTclValue(['ab', 'cd'])
    '{ab cd}'

    >>> valueToTclValue(['ab', 'c d'])
    '{ab {c d}}'

    >>> valueToTclValue(['ab'])
    'ab'

    >>> valueToTclValue(['ab', '{abc:1}'])
    '{ab {{abc:1}}}'

    >>> valueToTclValue('abc[1234]efg')
    'abc\\\\[1234\\\\]efg'

    >>> valueToTclValue(['a b'])
    '{{a b}}'

    >>> valueToTclValue([])
    '{}'

    >>> valueToTclValue("")
    '{}'

    >>> valueToTclValue("abc{defg")
    'abc\\\\{defg'

    >>> valueToTclValue(["abc{defg", "12345"])
    '{abc\\\\{defg 12345}'

    >>> valueToTclValue('{"a":1, "b":2, "c":[1,2,3,4], "d":{1:2,4:5}}')
    '{{"a":1, "b":2, "c":[1,2,3,4], "d":{1:2,4:5}}}'

    >>> valueToTclValue(["abc{dda ads", "b", "c"])
    '{abc\\\\{dda\\\\ ads b c}'

    >>> valueToTclValue(["abcd}da ads", "b", "c"])
    '{abcd\\\\}da\\\\ ads b c}'

    >>> valueToTclValue(["abc{d}da ads", "b", "c"])
    '{{abc{d}da ads} b c}'

    >>> valueToTclValue(["abcd}d{a ads", "b", "c"])
    '{abcd\\\\}d\\\\{a\\\\ ads b c}'

    >>> print(valueToTclValue(["abc{d}d{a ads", "b", "c"]))
    {abc\{d\}d\{a\ ads b c}

    >>> print(valueToTclValue(["abcd\\nefg", "b", "c"]))
    {{abcd
    efg} b c}

    >>> print(valueToTclValue(["abc{d}d{a ads", 1, True]))
    {abc\{d\}d\{a\ ads 1 true}

    >>> print(valueToTclValue({'a':1, 'b':2, 'c':3, 'd':True}))
    {a 1 c 3 b 2 d true}

    >>> from collections import OrderedDict
    >>> print(valueToTclValue(OrderedDict([('a',1), ('b',2), ('c',3),('d',True)])))
    {a 1 b 2 c 3 d true}

    >>> print(valueToTclValue([('a',1), ('b',2), ('c',3),('d',True)]))
    {{a 1} {b 2} {c 3} {d true}}
    """

    if isinstance(value, list) or isinstance(value, tuple):
        tclValue = []
        for subval in value:
            tclValue.append(valueToTclValue(subval))

        if len(tclValue) == 1 and tclValue[0][0] != '{':
            return tclValue[0]
        else:
            return '{%s}' % (' '.join(tclValue))
    elif isinstance(value, dict):
        vallist = []
        for p in value.items():
            vallist.extend(p)
        return valueToTclValue(vallist)
    else:
        stack = 0
        hasblank = 0

        if isinstance(value, bool):
            value = str(value).lower()
        else:
            value = str(value)

        for c in value:
            if c == '{': stack += 1
            elif c == '}': stack -= 1
            elif c in '\t\n\r ': hasblank = 1
            if stack < 0: break

        if stack < 0 or stack > 0:
            # { and } is unbalance, the string should be escaped
            return re.sub(r'[\s\{\}"]', r'\\\g<0>', value)

        if not value or hasblank or value[0] == '{':
            return '{%s}' % value
        else:
            # treat all quard brace as tcl string
            value = value.replace('[', '\[').replace(']', '\]')
            return value

# ------------------------------------------------------------------------------
# JNAP Service Descriptor
# ------------------------------------------------------------------------------
#{
#    '<service-name>': {
#        'name': 'action name space',
#        'desc': 'description for this service'
#        'actions': {
#            '<name>' : {
#                'name': 'the full name of this action'
#                'desc': 'descrption for this action'
#                'input': {
#                    '<param-name>': {
#                        'type': 'bool/int/string/<struct-name>/<enum-name>',
#                        'array': 'True or False',
#                        'optional': 'False or True',
#                        'desc': 'description for this param'
#                    }
#                },
#                'output': {
#                    '<param-name>': {
#                        'type': 'bool/int/string/<struct-name>/<enum-name>',
#                        'array': 'True or False',
#                        'optional': 'False or True',
#                        'desc': 'description for this param'
#                    }
#                },
#                'result': {
#                    'success': {
#                        '<value>': 'description for this value',
#                     },
#                    'errors': {
#                        '<value>': 'description for this value',
#                     },
#                }
#            },
#        },
#        'structs': {
#            '<struct-name>': {
#                '<member-name>': {
#                    'type': 'bool/int/string/<struct-name>/<enum-name>',
#                    'array': 'True or False',
#                    'optional': 'False/True',
#                    'desc': 'description for this member'
#                },
#            },
#        },
#        'enums': {
#            '<enum-name>': {
#                'value' : 'description for the enum value'
#            },
#        }
#    },
#}


def handleService(root):
    service = OrderedDict([
        ('name', ''),
        ('desc', ''),
        ('action-list', [])
    ])

    startNode = root.getparent()

    # parse the fullname
    nameEl = startNode.xpath('./following-sibling::div[@class="fullname"]')[0]
    service.update({'name': nameEl.text,  'desc': nameEl.tail.strip()})

    # parse the attached actions
    actionEls = startNode.xpath('./following-sibling::ul[1]/li/a')
    service['action-list'] = [el.text for el in actionEls]

    return service

stringify = etree.XPath("string()")
def handleAction(root):
    #action = {'input':None, 'output':None,  'result':None }
    action = OrderedDict()
    usedtype = set()

    actionName = root.text
    startNode = root.getparent()
    # parse the fullname
    nameEl = startNode.xpath('./following-sibling::div[@class="fullname"]')[0]
    action['name'] = nameEl.text
    action['desc'] = nameEl.tail.strip()

    # parse the input/output table
    for cls in ['input',  'output']:
        paramEl = startNode.xpath('./following-sibling::*[a[@name="action_%s.%s"]]' % (cls, actionName))[0]
        paramTable = paramEl.getnext()
        if paramTable.tag == 'table':
            action[cls] = OrderedDict()
            for trEl in paramTable.findall('./tr')[1:]:
                param = trEl[0].text.strip()
                type = stringify(trEl[1]).strip()
                if type.endswith('[]'):
                    array = True
                    type = type[:-2]
                else:
                    array = False

                usedtype.add(type)

                optional = True if trEl[2].text.strip() == 'yes' else False
                desc = stringify(trEl[3]).strip()
                action[cls][param] = OrderedDict([
                   ('type', type),
                   ('array', array),
                   ('optional', optional),
                   ('desc', desc)
                ])
            startNode = paramTable
        else:
            startNode = paramEl

    # parse the result enumerates
    resultEl = startNode.xpath('./following-sibling::*[a[@name="enum.%sResult"]]' % actionName)[0]
    resultTable = resultEl.getnext().getnext()
    if resultTable.tag == 'table':
        result = {'success':OrderedDict(),  'errors':OrderedDict()}
        for trEl in resultTable.findall('./tr')[1:]:
            value = trEl[0].text.strip()
            desc = stringify(trEl[1]).strip()
            if value in ['OK']:
                result['success'][value] = desc
            else:
                result['errors'][value] = desc

        action['result'] = result

    return (action, usedtype)


def handleStruct(root):
    struct = OrderedDict()
    usedtype = set()

    structName = root.text
    structEl = root.getparent().xpath('./following-sibling::*[a[@name="struct_members.%s"]]' % (structName))[0]
    memberTable = structEl.getnext()
    if memberTable.tag == 'table':
        for trEl in memberTable.findall('./tr')[1:]:
            member = trEl[0].text.strip()
            type = stringify(trEl[1]).strip()
            if type.endswith('[]'):
                array = True
                type = type[:-2]
            else:
                array = False

            usedtype.add(type)

            optional = True if trEl[2].text.strip() == 'yes' else False
            desc = stringify(trEl[3]).strip()
            struct[member] = OrderedDict([
               ('type', type),
               ('array', array),
               ('optional', optional),
               ('desc', desc)
            ])

    return (struct, usedtype)

def handleEnumerate(root):
    enum = OrderedDict()

    enumName = root.text
    enumEl = root.getparent().xpath('./following-sibling::*[a[@name="enum_values.%s"]]' % (enumName))[0]
    valueTable = enumEl.getnext()
    if valueTable.tag == 'table':
        for trEl in valueTable.findall('./tr')[1:]:
            if not trEl[0].text: continue
            value = trEl[0].text.strip()
            desc = stringify(trEl[1]).strip()
            enum[value] = desc

    return enum

# structs: structure definition for current doc file(not service)
# typelist: both input and output
def getStructNames(structs, typelist):
    structNames = set()
    find = False
    for name, (struct, usedtype) in structs.items():
        if name in typelist:
            structNames.add(name)
            typelist.remove(name)
            typelist |= usedtype
            find = True

    if find:
        return (structNames | getStructNames(structs, typelist))

    return structNames

# enums: enumerates definition for current doc file(not service)
# typelist: both input and output
def getEnumNames(enums, typelist):
    enumNames = set()
    for type in typelist:
        if type in enums:
            enumNames.add(type)
    return enumNames


def parseHtmlDoc(serviceHtml):
    services = {}
    actions = OrderedDict()
    structs = OrderedDict()
    enums = OrderedDict()

    #serviceName = os.path.basename(serviceHtml).rsplit('.',  1)[0]
    logger.debug('parsing -> %s' % serviceHtml)
    parser = etree.HTMLParser()
    docTree = etree.parse(serviceHtml, parser)
    root = docTree.getroot()

    # search the content table
    contentEl = root.find('./body/div[@class="contents"]/ol')
    for el in contentEl:
        category = el[0].text
        if category == 'Services':
            serviceCategory = el
            for serviceEl in serviceCategory.iterfind('.//li'):
                serviceAnchor = serviceEl[0].get('href')[1:]
                serviceRoot = root.find('.//a[@name="%s"]' % serviceAnchor)
                service = handleService(serviceRoot)

                if service['name']:
                    serviceName = service['name'].rsplit('/', 1)[1].lower()
                    services[serviceName] = service

        elif category == 'Actions':
            # -- parse the action part
            actionCategory = el
            for actionEl in actionCategory.iterfind('.//li'):
                actionName = actionEl[0].text
                actionAnchor = actionEl[0].get('href')
                actionRoot = root.find('.//a[@name="%s"]' % actionAnchor[1:])
                actions.update({actionName: handleAction(actionRoot)})

        elif category == 'Structures':
            # -- parse the structures part
            structCategory = el
            for structEl in structCategory.iterfind('.//li'):
                structName = structEl[0].text
                structAnchor = structEl[0].get('href')
                structRoot = root.find('.//a[@name="%s"]' % structAnchor[1:])
                structs.update({structName: handleStruct(structRoot)})

        elif category == 'Enumerations':
            # -- parse the enumerates part
            enumCategory = el
            for enumEl in enumCategory.iterfind('.//li'):
                enumName = enumEl[0].text
                enumAnchor = enumEl[0].get('href')
                enumRoot = root.find('.//a[@name="%s"]' % enumAnchor[1:])
                enums.update({enumName: handleEnumerate(enumRoot)})

    if not services:
        logger.warning(
            "'{}' not contain any service, skipped"
            .format(os.path.basename(serviceHtml))
        )
        return {}

    # compose service content
    for service in services.values():
        if not service['action-list']:
            logger.warning('service {0} does not contain any action'.format(service['name']))
            continue

        service['actions'] = OrderedDict()
        service['type-list'] = set()

        # get the actions for current service
        for actionName in service['action-list']:
            if actionName in actions:
                action, usedtype = actions[actionName]
                service['actions'].update({actionName: action})
                service['type-list'] |= usedtype
            else:
                logger.warning('not find the definition for action {0}'.format(actionName))

        # get the structs for current service
        typelist = service['type-list']
        structNames = getStructNames(structs, typelist)
        if structNames:
            service['structs'] = OrderedDict()
            for structName in structNames:
                struct = structs[structName][0]
                service['structs'].update({structName: struct})

        # get the enumerates for current service
        enumNames = getEnumNames(enums, typelist)
        if enumNames:
            service['enums'] = OrderedDict()
            for enumName in enumNames:
                enum = enums[enumName]
                service['enums'].update({enumName: enum})

        del service['type-list']
        del service['action-list']

    return services


def parseJnapSpecFromHTMLDocs(htmlPath):
    if not os.path.isdir(htmlPath):
        logger.debug("'%s' is not a existent directory" % htmlPath)
        return None

    ServiceDataBase = {}

    for serviceHtml in glob.iglob(os.path.join(htmlPath, '*.html')):
        services = parseHtmlDoc(serviceHtml)
        ServiceDataBase.update(services)

    return ServiceDataBase


# ------------------------------------------------------------------------------
# Tcl JNAP Service Descriptor
# ------------------------------------------------------------------------------
# DefineJnapService <service-name> {
#    title 'service title'
#    desc 'description for this service'
#    name 'service full name'
#    actions {
#        <name>  {
#            name 'action full name'
#            input {
#                <param-name> {
#                    type 'bool/int/string/<struct-name>',
#                    array 'true or false',
#                    optional 'false or true',
#                    desc 'description for this param'
#                }
#            }
#            output {
#                <param-name> {
#                    type 'bool/int/string/<struct-name>'
#                    array 'True or False'
#                    optional 'False or True'
#                    desc 'description for this param'
#                }
#            }
#            result {
#                success {
#                    <value> 'description for this value'
#                }
#                errors {
#                    <value> 'description for this value'
#                }
#            }
#        }
#    }
#    structs {
#        <struct-name> {
#            <member-name> {
#                type 'bool/int/string/<struct-name>'
#                array 'True or False'
#                optional 'False/True'
#                desc 'description for this member'
#            }
#        }
#    }
#    enums {
#        <enum-name> {
#            value  'description for the enum value'
#        }
#    }
#}
def outputToTclDescriptors(serviceDB,  destPath):
    for servName, service in serviceDB.items():
        outfile = os.path.join(destPath, servName + '.tcl')
        with open(outfile, 'w', encoding='utf8', errors='replace') as fd:
            fd.write("""# ============================================================================ #\n""" +
                     """#               Copyright (c) 2012 by Linksys-Cisco Systems, Inc.              #\n""" +
                     """#                              All Rights reserved                             #\n""" +
                     """# ---------------------------------------------------------------------------- #\n""" +
                     """#                 THIS FILE IS AUTO-GENERATED. DON'T MODIFY IT                 #\n""" +
                     """# ============================================================================ #\n\n""" )

            fd.write('DefineJnapService "%s" {\n' % servName)

            logger.debug('writing -> %s' % outfile)
            for prop in ('name', 'desc'):
                value = service.get(prop,'')
                fd.write('\t%s %s\n' % (prop,  valueToTclValue(value)) )

            if 'actions' in service:
                actions = service['actions']
                fd.write('\tactions {\n')
                for name,  action in actions.items():
                    fd.write('\t\t%s {\n' % name)
                    if 'name' in action:
                        fd.write('\t\t\tname %s\n' % valueToTclValue(action['name']))
                    if 'desc' in action:
                        fd.write('\t\t\tdesc %s\n' % valueToTclValue(action['desc']))
                    if 'input' in action:
                        fd.write('\t\t\tinput {\n')
                        for param, info in action['input'].items():
                            fd.write('\t\t\t\t%s {\n' % param)
                            for prop in ('type',  'array',  'optional',  'desc'):
                                fd.write('\t\t\t\t\t%s %s\n' % (prop, valueToTclValue(info[prop])))
                            fd.write('\t\t\t\t}\n')
                        fd.write('\t\t\t}\n')

                    if 'output' in action:
                        fd.write('\t\t\toutput {\n')
                        for param, info in action['output'].items():
                            fd.write('\t\t\t\t%s {\n' % param)
                            for prop in ('type',  'array',  'optional',  'desc'):
                                fd.write('\t\t\t\t\t%s %s\n' % (prop, valueToTclValue(info[prop])))
                            fd.write('\t\t\t\t}\n')
                        fd.write('\t\t\t}\n')

                    if 'result' in action:
                        fd.write('\t\t\tresult {\n')
                        for cls in ('success', 'errors'):
                            fd.write('\t\t\t\t%s {\n' % cls)
                            for value, desc in action['result'][cls].items():
                                fd.write('\t\t\t\t\t%s %s\n' % (value, valueToTclValue(desc)))
                            fd.write('\t\t\t\t}\n')
                        fd.write('\t\t\t}\n')
                    fd.write('\t\t}\n')

                fd.write('\t}\n')

            if 'structs' in service:
                structs = service['structs']
                fd.write('\tstructs {\n')
                for name, struct in structs.items():
                    fd.write('\t\t%s {\n' % name)
                    for member, info in struct.items():
                        fd.write('\t\t\t%s {\n' % member)
                        for prop in ('type',  'array',  'optional',  'desc'):
                            fd.write('\t\t\t\t%s %s\n' % (prop, valueToTclValue(info[prop])))
                        fd.write('\t\t\t}\n')
                    fd.write('\t\t}\n')
                fd.write('\t}\n')

            if 'enums' in service:
                enums = service['enums']
                fd.write('\tenums {\n')
                for name, enum in enums.items():
                    fd.write('\t\t%s {\n' % name)
                    for value, desc in enum.items():
                        fd.write('\t\t\t%s %s\n' % (valueToTclValue(value), valueToTclValue(desc)))
                    fd.write('\t\t}\n')
                fd.write('\t}\n')

            fd.write('}\n')



# ------------------------------------------------------------------------------
# JSON JNAP Service Descriptor
# ------------------------------------------------------------------------------
# {
#     'title': 'service title',
#     'desc': 'description for this service',
#     'name': 'service full name',
#     'actions': {
#         '<name>':  {
#             'name' 'action full name',
#             'input': {
#                 '<param-name>': {
#                     'type': 'bool/int/string/<struct-name>',
#                     'array': 'true or false',
#                     'optional': 'false or true',
#                     'desc': 'description for this param'
#                 }
#             },
#             'output' {
#                 '<param-name>' {
#                     'type': 'bool/int/string/<struct-name>',
#                     'array': 'True or False',
#                     'optional': 'False or True',
#                     'desc': 'description for this param'
#                 }
#             },
#             'result' {
#                 'success' {
#                     '<value>': 'description for this value'
#                 },
#                 'errors' {
#                     '<value>': 'description for this value'
#                 }
#             }
#         },
#     },
#     'structs' {
#         '<struct-name>' {
#             '<member-name>' {
#                 'type': 'bool/int/string/<struct-name>',
#                 'array': 'True or False',
#                 'optional': 'False/True',
#                 'desc': 'description for this member'
#             }
#         }
#     },
#     'enums': {
#         '<enum-name>': {
#             'value':  'description for the enum value'
#         }
#     }
#}

def outputToJSONDescriptors(serviceDB,  destPath):
    import json
    for servName, service in serviceDB.items():
        outfile = os.path.join(destPath, servName + '.json')

        logger.debug('writing -> %s' % outfile)
        with open(outfile, 'w', encoding='utf8', errors='replace') as fd:
            json.dump(service, fd, indent=4)


# The default dumpped YAML format doesn't have good look. Will improve it in the future
def outputToYAMLDescriptors(serviceDB,  destPath):
    from yaml import dump
    try:
        from yaml import CDumper as Dumper
    except ImportError:
        from yaml import Dumper

    for servName, service in serviceDB.items():
        outfile = os.path.join(destPath, servName + '.yaml')

        logger.debug('writing -> %s' % outfile)
        with open(outfile, 'w', encoding='utf8', errors='replace') as fd:
            output = dump(service, Dumper=Dumper)
            fd.write(output)


if __name__ == "__main__":

    def show_usage ():
        print('JnapDoc2Descriptor [OPTIONS] <Path-Of-HTML-Spec>- Generate JNAP descriptor for other language')
        print('OPTIONS:')
        print('-f, --format:    Format of output descriptor [tcl, json]')
        print('-o, --output:    Specifies the output folder')
        print('-p, --pack:      Generat descriptors in all the formats and pack them into jnap-descriptors.cz')

    format = output = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'f:o:', ['format=', 'output='])
        for o, a in opts:
            if o in ('-f', '--format'):
                format = a
            elif o in ('-o', '--output'):
                output = a
            else:
                show_usage()
                sys.exit(-1)
    except Exception as why:
        print('error: ', why)
        show_usage()
        sys.exit(-1)

    if not format:
        print('error: option "-format" must be specified')
        sys.exit(-1)

    if not args:
        print('error: please specify the path of HTML JNAP documentation')
        sys.exit(-1)

    if not output:
        output = os.path.abspath(os.curdir)

    logging.basicConfig(
        format='%(asctime)s | %(name)s | %(message)s',
        datefmt="%M:%S"
    )
    logging.getLogger('jnap-doc-compiler').setLevel(logging.DEBUG)

    serviceDB = parseJnapSpecFromHTMLDocs(args[0])

    formatHandler = {
        'tcl': outputToTclDescriptors,
        'json': outputToJSONDescriptors,
        'yaml': outputToYAMLDescriptors,
    }

    handler = formatHandler.get(format,  None)
    if handler:
        handler(serviceDB, output)
    else:
        print('error: output format "%s" is not supported' % format )




