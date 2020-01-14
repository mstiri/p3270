import os
import re
import subprocess
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(name)s - %(asctime)s - %(process)d: %(message)s')
fileHandler = logging.FileHandler('p3270.log')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

class InvalidConfiguration(Exception):
    pass

class S3270():
    """ S3270: represents the S3270 command and its arguments/methods
        This the interface to the 's3270' executable
    """
    numOfInstances = 0
    def __init__(self, args):
        self.args = args
        logger.debug('Calling s3270 with the following args: ', self.args)
        self.subpro = subprocess.Popen(self.args,
                                       stdout=subprocess.PIPE,
                                       stdin=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
        self.buffer = None
        self.statusMsg = None

    def do(self, cmd):
        """ Execute the command represented by the specified string
        """
        self.cmd = cmd.encode() + b'\n'
        logger.debug("Sending the Command: [{}]".format(self.cmd))
        self.subpro.stdin.write(self.cmd)
        self.subpro.stdin.flush()
        if self.cmd == b'Quit\n':
            return self.check(True)
        return self.check()

    def check(self, doNotCheck=False):
        """ Check the result of the executed command
            The output is always redirected to stdout, stderr is not used
            The first line is data if any, otherwise it returns a status message
            consisting of 12 blank-separated fields and a return message ('ok' or 'error')
            In the case of PrintText as 'string', there may be as many 'data' lines as the screen size.
            These lines are then followed by a status message and a return message.
        """
        if doNotCheck:
            return True
        data = self.subpro.stdout.readline().decode().rstrip('\n')
        if not data.startswith('data:'):
            statusMsg = data
        else:
            self.buffer = data[6:]
            data = self.subpro.stdout.readline().decode().rstrip('\n')
            if not data.startswith('data:'):
                statusMsg = data
            else:
                self.buffer += '\n' + data[6:]
                go = True
                while go:
                    data = self.subpro.stdout.readline().decode().rstrip('\n')
                    if not data.startswith('data:'):
                        go = False
                        statusMsg = data
                    else:
                        self.buffer += '\n' + data[6:]

        returnMsg = self.subpro.stdout.readline().decode().rstrip('\n')
        self.statusMsg = StatusMessage(statusMsg)
        logger.debug("Buffer data    => [{}]".format(self.buffer))
        logger.debug("Status message => [{}]".format(statusMsg))
        logger.debug("Return message => [{}]".format(returnMsg))
        if returnMsg == 'ok':
            return True
        return False

class P3270Client():
    """ P3270Client: Represents the model of a 3270 client.
        It may rely on a configuration file for further customization. If no
        configuration file is specified. Default values will be used.
    """
    numOfInstances = 0
    def __init__(self, luName=None, hostName='localhost', hostPort='23', modelName='3279-2', configFile=None, verifyCert='yes', enableTLS='no'):
        self.luName = luName
        self.hostName = hostName
        self.hostPort = hostPort
        self.modelName = modelName
        self.configFile = configFile
        self.verifyCert = verifyCert
        self.enableTLS = enableTLS
        self.conf = Config(cfgFile=self.configFile, hostName=self.hostName,
                           hostPort=self.hostPort, luName = self.luName, modelName=self.modelName)
        if self.conf.isValid():
            self.subpro = None
            self.makeArgs()
            self.s3270 = S3270(self.args)
        else:
            raise InvalidConfiguration
        self._isValid = self.conf.isValid()
        self.__class__.numOfInstances += 1

    def makeArgs(self):
        """ Construct the list of arguments to be used for interacting with s3270
        """
        self.args = ['s3270']
        if self.conf.isValid():
            self.args.append('-model')
            self.args.append(self.conf.modelName)
            self.args.append('-port')
            self.args.append(self.conf.hostPort)
            if self.conf.traceFile:
                self.args.append('-trace')
                self.args.append('-tracefile')
                self.args.append(self.conf.traceFile)
            if self.conf.verifyCert == "no":
                self.args.append('-noverifycert')

    def connect(self):
        """ Connect to the host
        """
        if self.conf.luName:
            logger.info("Connect to host [{}] with LUName: [{}]".format(self.conf.hostName, self.conf.luName))
            if self.conf.enableTLS == 'yes':
                return self.s3270.do('Connect(L:{}@{})'.format(self.conf.luName,self.conf.hostName))
            return self.s3270.do('Connect(B:{}@{})'.format(self.conf.luName,self.conf.hostName))
        else:
            logger.info("Connect to host [{}] with no LUName".format(self.conf.hostName))
            if self.conf.enableTLS == 'yes':
                return self.s3270.do('Connect(L:{})'.format(self.conf.hostName))
            return self.s3270.do('Connect(B:{})'.format(self.conf.hostName))

    def disconnect(self):
        """ Disconnect from host
        """
        logger.info("Disconnect from host ({})".format(self.hostName))
        return self.s3270.do('Disconnect')

    def endSession(self):
        """ End the emulator script
        """
        logger.info("Ending the session")
        return self.s3270.do('Quit')

    def sendEnter(self):
        """ Send Enter to host
        """
        logger.info("Sending Enter key")
        return self.s3270.do('Enter')

    def sendPF(self, n):
        """ Send a PF (Program Function) key to the remote host.
            May block waiting for a response
            n in 1..24
        """
        if isinstance(n, int) and n >= 1 and n <= 24:
            logger.info("Sending PF key {} to remote host".format(n))
            return self.s3270.do('PF({})'.format(n))
        else:
            logger.error("Specified PF key ({}) out of the range 1..24, or not int".format(n))
            return False

    def sendPA(self, n):
        """ Send a PA (Program Attention) key to the remote host.
            May block waiting for a response
            n in 1..3
        """
        if isinstance(n, int) and n >= 1 and n <= 3:
            logger.info("Sending PA key {} to remote host".format(n))
            return self.s3270.do('PA({})'.format(n))
        else:
            logger.error("Specified PA key({})out of the range 1..3, or not int".format(n))
            return False

    def sendBackSpace(self):
        """ Send ASCII BS or move cursor to the left
        """
        logger.info("Sending back space to remote host")
        return self.s3270.do('BackSpace')

    def sendBackTab(self):
        """ Send back tab (to go to the beginning previous field).
        """
        logger.info("Sending back tab to remote host")
        return self.s3270.do('BackTab')

    def sendTab(self):
        """ Send tab key (to go to the beginnig of the next field).
        """
        logger.info("Sending tab to remote host")
        return self.s3270.do('Tab')

    def clearScreen(self):
        """ Clear the screen.
            May block waiting for a response
        """
        logger.info("Clear screen")
        return self.s3270.do('Clear')

    def delChar(self):
        """ Delete character under cursor
        """
        logger.info("Deleting char")
        return self.s3270.do('Delete')

    def delField(self):
        """ Delete entire field.
        """
        logger.info("Deleting field")
        return self.s3270.do('DeleteField')

    def eraseChar(self):
        """ Erase previous character (or send ASCII BS).
        """
        logger.info("Erase character")
        return self.s3270.do('Erase')

    def moveCursorDown(self):
        """ Move cursor Down.
        """
        logger.info("Move cursor Down")
        return self.s3270.do('Down')

    def moveCursorUp(self):
        """ Move cursor Up.
        """
        logger.info("Move cursor Up")
        return self.s3270.do('Up')

    def moveCursorLeft(self):
        """ Move cursor left.
        """
        logger.info("Move cursor left")
        return self.s3270.do('Left')

    def moveCursorRight(self):
        """ Move cursor right.
        """
        logger.info("Move cursor right")
        return self.s3270.do('Right')

    def moveTo(self, row, col):
        """ Move cursor to the position specified by (row,col) pair.
        """
        # The origin is [0,0] not [1,1]
        row -= 1
        col -= 1
        logger.info("Move cursor to the position ({},{})".format(row, col))
        return self.s3270.do('MoveCursor({}, {})'.format(row, col))

    def moveToFirstInputField(self):
        """ Move cursor to the first input field.
        """
        logger.info("Move cursor to the first input field")
        return self.s3270.do('Home')

    def sendText(self, text):
        """ Send text to host.
        """
        logger.info("Send the following text: [{}]".format(text))
        return self.s3270.do('String("{}")'.format(text))

    def saveScreen(self, fileName='screen', dataType='html'):
        """ Save the current screen in the form of an HTML file.
        """
        if fileName and self.conf.screensDir:
            fileName = os.path.join(self.conf.screensDir, fileName)
        if dataType == 'html' or dataType == 'rtf':
            logger.info("Save an '{}' screen to file [{}]".format(dataType, fileName))
            return self.s3270.do('PrintText({}, {})'.format(dataType, fileName))
        else:
            logger.error("Specified data type '{}' is invalid".format(dataType))
            return False

    def getScreen(self):
        """ Get the content of the current screen as string
        """
        logger.info("Getting the screen content in text format")
        self.s3270.do('PrintText(string)')
        return self.s3270.buffer

    def printScreen(self):
        """ Print the current screen to stdout
        """
        screen = self.getScreen()
        if self.s3270.statusMsg.screenDefinition():
            rows, cols = self.s3270.statusMsg.screenDefinition()
        else:
            if self.conf.modelName == '3278-2' or self.conf.modelName == '3279-2':
                cols, rows = 80, 24
            elif self.conf.modelName == '3278-3' or self.conf.modelName == '3279-3':
                cols, rows = 80, 32
            elif self.conf.modelName == '3278-4' or self.conf.modelName == '3279-4':
                cols, rows = 80, 43
            elif self.conf.modelName == '3278-5' or self.conf.modelName == '3279-5':
                cols, rows = 132, 27
        print('*' * cols)
        print(screen)
        print('*' * cols)

    def isConnected(self):
        """ Get the connection status.
            returns 'True' if connected, 'False' otherwise
        """
        self.s3270.do('NoOpCommand')
        return self.s3270.statusMsg.connectionState()

class Config():
    """ Config represents a communication configuration.
            The object is built from a configuration file when instantiating a
            P3270Client.
            If no configuration file is specified, the following default values are used:
                hostName='localhost'
                hostPort=23
                modelName="3279-2"
    """
    _validModels = ['3278-2', '3278-3', '3278-4', '3278-5',
                    '3279-2', '3279-3', '3279-4', '3279-5']
    _sbcsCodePages = {'cp037': '(cp37, us, us-intl)',
                      'cp273': '(german)',
                      'cp275': '(brazilian)',
                      'cp277': '(norwegian)',
                      'cp278': '(finnish)',
                      'cp280': '(italian)',
                      'cp284': '(spanish)',
                      'cp285': '(uk)',
                      'cp297': '(french)',
                      'cp424': '(hebrew)',
                      'cp500': '(belgian)',
                      'cp803': '(hebrew-old)',
                      'cp870': '(polish, slovenian)',
                      'cp871': '(icelandic)',
                      'cp875': '(greek)',
                      'cp880': '(russian)',
                      'cp930': '(cp290, japanese-290, japanese-kana)',
                      'cp935': '(cp836, simplified-chinese)',
                      'cp937': '(traditional-chinese)',
                      'cp939': '(cp1027, japanese-1027, japanese-latin)',
                      'cp1026': '(turkish)',
                      'cp1047': '',
                      'cp1140': '(us-euro)',
                      'cp1141': '(german-euro)',
                      'cp1142': '(norwegian-euro)',
                      'cp1143': '(finnish-euro)',
                      'cp1144': '(italian-euro)',
                      'cp1145': '(spanish-euro)',
                      'cp1146': '(uk-euro)',
                      'cp1147': '(french-euro)',
                      'cp1148': '(belgian-euro)',
                      'cp1149': '(icelandic-euro)',
                      'cp1160': '(thai)',
                      'cp1388': '(chinese-gb18030)',
                      'apl': '',
                      'bracket': '(oldibm, bracket437)'}
    _dbcsCodePage = {'cp930': '(cp1027, cp290, japanese-1027, japanese-290, japanese-kana, japanese-latin)',
                     'cp935': '(cp936, simplified-chinese)',
                     'cp937': '(traditional-chinese)',
                     'cp1388': '(chinese-gb18030)'}
    commentPattern = re.compile("^#.*$")
    emptyLinePattern = re.compile("^ *$")
    hostPattern = re.compile("^ *hostname *=")
    portPattern = re.compile("^ *port *=")
    modelPattern = re.compile("^ *model *=")
    traceFilePattern = re.compile("^ *traceFile *=")
    luPattern = re.compile("^ *LUName *=")
    cpPattern = re.compile("^ *codePage *=")
    screensPattern = re.compile("^ *screensDir *=")
    verifyCertPattern = re.compile("^ *verifyCert *=")
    enableTLSPattern = re.compile("^ *enableTLS *=")

    def __init__(self, cfgFile=None, hostName='localhost', hostPort='23',
                 modelName='3279-2', traceFile=None, 
                 luName=None, codePage='cp037', screensDir=None, verifyCert='yes', enableTLS='no'):
        self.cfgFile = cfgFile
        self.hostName = hostName
        self.hostPort = hostPort
        self.modelName = modelName
        self.traceFile = traceFile
        self.luName = luName
        self.codePage = codePage
        self.screensDir = screensDir
        self.verifyCert = verifyCert
        self.enableTLS = enableTLS
        # List of invalid attributes
        self.invalidAttributes = []
        if self.cfgFile:
            self.readConfig()
        self.validateAttributes()
        if len(self.invalidAttributes) > 0:
            self._isValid = False
            for attr in self.invalidAttributes:
                if attr == 'modelName':
                    logger.error("The model ({}) is not a valid model".format(self.modelName))
                elif attr == 'hostPort':
                    logger.error("Host port ({}) is out of range".format(self.hostPort))
                elif attr == 'codePage':
                    logger.error("The specified code page ({}) is not valid".format(self.codePage))
                elif attr == 'screensDir':
                    logger.error("The directory ({}) does not exist".format(self.screensDir))
                elif attr == 'verifyCert':
                    logger.error("The value of the verifyCert parameter in the config file should be: yes or no")
                elif attr == 'enableTLS':
                    logger.error("The value of the enableTLS parameter in the config file should be: yes or no")
        else:
            self._isValid = True

    def readConfig(self):
        with open(self.cfgFile) as f:
            for line in f:
                line = line.replace('\n', '').replace('\r', '').replace('\t', '')
                if self.hostPattern.match(line):
                    self.hostName = line.split('=')[1].strip()
                elif self.portPattern.match(line):
                    self.hostPort = line.split('=')[1].strip()
                elif self.modelPattern.match(line):
                    self.modelName = line.split('=')[1].strip()
                elif self.traceFilePattern.match(line):
                    self.traceFile = line.split('=')[1].strip()
                elif self.luPattern.match(line):
                    self.luName = line.split('=')[1].strip()
                elif self.cpPattern.match(line):
                    self.codePage = line.split('=')[1].strip()
                elif self.screensPattern.match(line):
                    self.screensDir = line.split('=')[1].strip()
                elif self.verifyCertPattern.match(line):
                    self.verifyCert = line.split('=')[1].strip().lower()
                elif self.enableTLSPattern.match(line):
                    self.enableTLS = line.split('=')[1].strip().lower()

    def validateAttributes(self):
        """ Validate configuration attributes:
            Model name: 3278-x or 3279-x (x in 2 .. 5)
            Port: should be in the range 1..65535
            codePage: The specified code page should be valid
            screensDir: The directory should exist if specified
            verifyCert: The value should be "yes" or "no"
            enableTLS: The value should be "yes" or "no"
        """
        if self.modelName not in self._validModels:
            self.invalidAttributes.append('modelName')
        if int(self.hostPort) < 1 or int(self.hostPort) > 65535:
            self.invalidAttributes.append('hostPort')
        if self.codePage:
            if self.codePage not in self._dbcsCodePage and self.codePage not in self._sbcsCodePages:
                self.invalidAttributes.append('codePage')
        if self.screensDir:
            if not os.path.isdir(self.screensDir):
                self.invalidAttributes.append('screensDir')
        if self.verifyCert:
            if self.verifyCert not in ["yes", "no"]:
                self.invalidAttributes.append('verifyCert')
        if self.enableTLS:
            if self.enableTLS not in ["yes", "no"]:
                self.invalidAttributes.append('enableTLS')

    def isValid(self):
        return self._isValid

    def printConfig(self):
        if self.hostName:
            print("Host Name      : {}".format(self.hostName))
        if self.hostPort:
            print("Host Port      : {}".format(self.hostPort))
        if self.modelName:
            print("Terminal Model : {}".format(self.modelName))
        if self.traceFile:
            print("Trace File     : {}".format(self.traceFile))

class StatusMessage():

    def __init__(self, status):
        self.statusMessage = status
        if not len(self.statusMessage.split(' ')) == 12:
            self.statusMessage = ' ' * 12
            self._is_valid = False
        else:
            self.keyboard = self.statusMessage.split(' ')[0]
            self.screen = self.statusMessage.split(' ')[1]
            self.field = self.statusMessage.split(' ')[2]
            self.connection = self.statusMessage.split(' ')[3]
            self.emulator = self.statusMessage.split(' ')[4]
            self.model = self.statusMessage.split(' ')[5]
            self.numOfRows = self.statusMessage.split(' ')[6]
            self.numOfCols = self.statusMessage.split(' ')[7]
            self.cursorRow = self.statusMessage.split(' ')[8]
            self.cursorCol = self.statusMessage.split(' ')[9]
            self.winId = self.statusMessage.split(' ')[10]
            self.executionTime = self.statusMessage.split(' ')[11]
            self._is_valid = True

    def isValid(self):
        return self._is_valid

    def keyboardState(self):
        """ Returns a string:
            'Unlocked': Keyboard is unlocked
            'Locked': Tthe keyboard is locked waiting for a response from the host, or not connected to a host
            'Locked because of an operator error'
            Returns None object if the message is invalid
        """
        if self.isValid():
            if self.keyboard == 'U':
                return 'Unlocked'
            elif self.keyboard == 'L':
                return 'Locked'
            elif self.keyboard == 'E':
                return 'Locked because of an operator error'
        return None

    def screenFormatting(self):
        """ Returns a string:
            'Formatted'
            'Unformatted'
            Returns None object if the message is invalid
        """
        if self.isValid():
            if self.screen == 'F':
                return 'Formatted'
            elif self.screen == 'U':
                return 'Unformatted'
        return None

    def fieldProtection(self):
        """ Returns a string:
            'Protected'
            'Unprotected'
            Returns None object if the message is invalid
        """
        if self.isValid():
            if self.field == 'P':
                return 'Protected'
            elif self.field == 'U':
                return 'Unprotected'
            else:
                return 'Unknown'
        return None

    def connectionState(self):
        """ Returns a boolean
            True: if connected to host
            False: if not
            Returns None object if the message is invalid
        """
        if self.isValid():
            if self.connection.startswith('C('):
                return True
            elif self.connection == 'N':
                return False
        return None

    def emulatorMode(self):
        """ Returns a string:
            '3270':
            'NVT Line':
            'NVT Character':
            'Unnegotiated':
            'Not connected':
            Returns None object if the message is invalid
        """
        if self.isValid():
            if self.emulator == 'I':
                return '3270'
            elif self.emulator == 'L':
                return 'NVT Line'
            elif self.emulator == 'C':
                return 'NVT Character'
            elif self.emulator == 'P':
                return 'Unnegotiated'
            elif self.emulator == 'N':
                return 'Not connected'
        return None

    def modelNumber(self):
        """ Return the client model number (2..5)
            Returns None object if the message is invalid
        """
        if self.isValid():
            return self.model
        return None

    def screenDefinition(self):
        """ Returns the current screen definition (rows, cols)
            Returns None object if the message is invalid
        """
        if self.isValid():
            return (int(self.numOfRows), int(self.numOfCols))
        return None

    def cursorPosition(self):
        """ Returns the cursor position on the screen (row, col)
            Returns None object if the message is invalid
        """
        if self.isValid():
            return int(self.cursorRow) + 1, int(self.cursorCol) + 1
        return None

    def windowId(self):
        """ The X window identifier for the main x3270 window, in
            hexadecimal preceded by 0x. For s3270 and c3270, this is zero.
            In our case (s3270): it is always '0x0'
            Returns None object if the message is invalid
        """
        if self.isValid():
            if self.winId == '0x0':
                return self.winId
        return None

    def execTime(self):
        """ Returns the execution time for the last command on the host.
            If the previous command did not require a host response, this is a dash.
            Returns None object if the message is invalid
        """
        if self.isValid():
            return self.executionTime
        return None
