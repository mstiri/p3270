# A Python library to access IBM hosts

<p align="center"> 
    <a href="https://travis-ci.org/mstiri/p3270">
        <img 
            src="https://travis-ci.org/mstiri/p3270.svg?branch=master"
            alt="build status">
    </a>
    <a href='https://coveralls.io/github/mstiri/p3270?branch=master'>
        <img 
            src="https://coveralls.io/repos/github/mstiri/p3270/badge.svg?branch=master"
            alt="coverage">
    </a>

</p>


## Description
A Python library that provides an interface to communicate with IBM hosts: send commands and text, receive output (screens). The library provides the means to do what a human can do using a 3270 emulator. 

The library is highly customizable and is built with simplicity in mind. 
It is written in Python 3, runs on Linux and Unix-like Operating Systems, and relies on the `s3270` utility. So it is required to have the `s3270` installed on your system and available on your PATH.

The library allows you to open a telnet connection to an IBM host, and execute a set of instructions as you specified them in your python program.


## Installation
A simple pip command brings the library to your environment: 

```pip install p3270```

__NB__: Make sure that you're using the python3 version of the pip command. 


## Usage 
Import the client class from the library:
```python 
from p3270 import P3270Client
```

Create a client object specifying a configuration file:
```python 
my_client = P3270Client(configFile='my-config.cfg')
```

It is also possible to create a client object with the config options stated in the code.
```python 
my_client = P3270Client(hostName='192.168.100.25', path='c:\\wc3270\\', codePage='cp277')
```

If the s3270 program is downloaded as a .zip file or otherwise fails to be added to the path when installed, it is possible to state the path when creating the P3270Client.

Connect the client, and you're good to go:
```python
if not my_client.connect():
    print('Connection failed !')
    exit(1)

# Start sending your commands to the host ...
```

### Configuration file:
The configuration file is used to set a bunch of parameters about the client and host interaction. The file has the following format:

```<parameter> = <value>```

Lines starting with a '#' are considered as comments and therefore ignored.
For now the parameters are:
- __hostname__: The name or IP address of the host to connect to. Default is `localhost`. 
- __port__: The port (on the host) to which the client should connect. Default is `23`.
- __model__: Terminal model name. The possible values are:
`3278-n` and `3279-n` (`n` is the model number and can take the value: 2, 3, 4 or 5). The _base model_ 3278 is a green on black 3270 display, whereas 3279 base model is a color 3270 display. _Model numbers_ are used to specify the screen definition (rows and columns) as follows:

Model number | Columns | Rows
---|---|---
2  |80 |24
3  |80 |32
4  |80 |43
5|132|27
Default is `3279-2`.

- __traceFile__: The file to which communication traces will be directed. If not set traces will not be generated.
- __LUName__: LU name to use for connection to the host. If it is not set, connection is done with no LU name. 
- __enableTLS__: Enable or not TLS connection to remote hosts(yes or np). Default is no. 
- __verifyCert__: Verify or not the certificate of the remote host (yes or no). Default is yes.
- __codePage__: The EBCDIC character set to use for communication with the host. 
Supported code pages depens on your `s3270` version. The list can be obtained by running the following command on your shell:
```sh 
# s3270 -v
```
Default is `cp037`.

An example of configuration file would be:
```sh
# Target hostname 
hostname = 192.168.100.25
# Port
port = 10023
# Model Name: Default 3279-2
model = 3279-2
# TraceFile
traceFile = client.trace
# LU name to use
#LUName = LUPY0001
# EBCDIC character set to use for the host
codePage = cp037
# The file where all the screens should be saved
screensDir = /home/me/projects/python/mainframe/screens/
```

One configuration file can be shared by multiple clients. 


### Library methods:

Once the client object (P3270Client class) is created, the following methods can be used to interact with the host.
* `connect()`:
    * __Description__: Connect the client to the host
    * __Arguments__: none
* `disconnect()` 
    * __Description__: Disconenct the client from the host 
    * __Arguments__: none
* `endSession()` 
    * __Description__: End the client session 
    * __Arguments__: none
* `sendEnter()`
    * __Description__: Send the Enter key to host 
    * __Arguments__: none
* `sendPF(n)`
    * __Description__: Send a PF (Program Function AID) key 
    * __Arguments__: <br>
        __n__ (_int_): PF key number.<br>
        The number should be in the range 1..24
* `sendPA(n)` 
    * __Description__: Send a PA (Program Attention AID) key 
    * __Arguments__: __n__ (_int_): PA key number.<br>The number should be in the range 1..3
* `sendBackSpace()` 
    * __Description__: Send Back space to the host ()
    * __Arguments__: none
* `sendBackTab()` 
    * __Description__: Send back Tab to the host  (go to start of previous input field) 
    * __Arguments__: none
* `sendHome()` 
    * __Description__: Send Home key to the host 
    * __Arguments__: none
* `sendTab()` 
    * __Description__: Send Tab key to the host 
    * __Arguments__: none
* `sendKeys(keys)` 
    * __Description__: Emulates pressing keys to the host 
        * __Arguments__: <br>
        __keys__ (_string_): The keys to emulate to the host
* `clearScreen()` 
    * __Description__: Clear the screen 
    * __Arguments__: none
* `delChar()` 
    * __Description__: Delete character next to the cursor (ASCII DEL) 
    * __Arguments__: none
* `delField()`
    * __Description__: Delete the whole field
    * __Arguments__: none
* `delWord()`
    * __Description__: Delete word under cursor
    * __Arguments__: none
* `eraseChar()`
    * __Description__: Erase character previous character (ASCII BS)
    * __Arguments__: none
* `moveCursorDown()` 
    * __Description__: Move cursor down 
    * __Arguments__: none
* `moveCursorUp()` 
    * __Description__: Move cursor up 
    * __Arguments__: none
* `moveCursorLeft()` 
    * __Description__: Move cursor left 
    * __Arguments__: none
* `moveCursorRight()` 
    * __Description__: Move cursor right 
    * __Arguments__: none
* `moveTo(row, col)` 
    * __Description__: Move cursor to a specific position
    * __Arguments__: <br>
        __row__ (_int_): Row position to which the cursor should be moved.<br>
        __col__ (_int_): Column position to which the cursor should be moved.
* `moveToFirstInputField()` 
    * __Description__: Move cursor to the first input field on the current screen 	
    * __Arguments__: none
* `sendText(text)` 
    * __Description__: Send text to the host 
    * __Arguments__: <br>
        __text__ (_string_): The string to send to the host
* `saveScreen(fileName, dataType)` 
    * __Description__: Save the current screen to a file 
    * __Arguments__: <br>
        __fileName__ (string): File name to which the screen will be saved.<br>
        If the file does not exist it is created, otherwise it is appended.<br>
        Files are saved under the specified name in the directory specified in the parameter `screensDir` of the configuration file. Default: `screen`<br> 
        __dataType__ (_string_): The data type of the captured screen. Supported data types are *html*, or *rtf*. Default: `html`
* `getScreen()`
    * __Description__: Get the actual screen as raw text 
    * __Arguments__: none
* `printScreen()` 
    * __Description__: Print the current screen to the standard output 
    * __Arguments__: none
* `isConnected()` 
    * __Description__: Get the connection status of the client 
    * __Arguments__: none
* `readTextAtPosition(row, col, length)` 
    * __Description__: Reads text at a row,col position and returns it 
    * __Arguments__: <br>
        __row__ (_int_): Row position on where to read.<br>
        __col__ (_int_): Column position on where to read.<br>
        __length__ (_int_): How many chars to read
* `readTextArea(row, col, rows, cols)` 
    * __Description__: Reads text area at a row,col position and returns it 
    * __Arguments__: <br>
        __row__ (_int_): Row position on where to read.<br>
        __col__ (_int_): Column position on where to read.<br>
        __rows__ (_int_): Number of rows to read down from the starting row.<br>
        __cols__ (_int_): Number of columns to read, right from the starting column.<br>
* `readTextAtPosition(row, col, expected_text)` 
    * __Description__: Will check at the given coordinates if the text appear or not. Returns true if the text was found, false if not. 
    * __Arguments__: <br>
        __row__ (_int_): Row position on where to read.<br>
        __col__ (_int_): Column position on where to read.<br>
        __expected_text__ (_string_): The text to look for
* `waitForField()` 
    * __Description__: Will wait for the field to be ready where the cursor is standing 
    * __Arguments__: none
* `trySendTextToField(text, row, col)` 
    * __Description__: Will try and write the given text at the given position. Once the text is written, it will check if the text is now shown at the screen at that position. Returns true if succeeded, false if not. 
    * __Arguments__: <br>
        __row__ (_int_): Row position on where to read.<br>
        __col__ (_int_): Column position on where to read.<br>
        __text__ (_string_): Text to write

All of the above methods return `True` if they succeed, and `False` otherwise. The only exceptions:
- `endSession()`, it terminates the emulation session and returns `True` in all cases.
- `readTextAtPosition`, `readTextArea`, `getScreen` all return the text they read.



### Example:

```python
from p3270 import P3270Client

# Connect and test if connection succeeded or not
if not my_client.connect():
    print('Connection failed !')
    exit(1)

# Save the home screen to a file called 'home.html'. HTML format is the default.
my_client.saveScreen(fileName='home.html')

# Send user name to the current field (user ID)
my_client.sendText('user1')

# Send TAB key to go to the next field
my_client.sendTab()

# Send the user password to the password field.
my_client.sendText('password1')

# Send Enter key to submit the current screen with field contents
my_client.sendEnter()

# Clear the screen 
my_client.clearScreen()

# Send the CICS command 'CEMT INQ TASK' to get running tasks
my_client.sendText('CEMT INQ TASK')

# Submit 
my_client.sendEnter()

# Capture the screen
my_client.saveScreen(fileName='tasks.html')

# Go back : PF3 key
my_client.sendPF(3)

# Go back again
my_client.sendPF(3)

# Disconnect from the host 
my_client.disconnect()

# End the emulation session
my_client.endSession()
```


Screens should go to the directory specified in the parameter `screensDir` specified in the configuration file.
The library generates some log messages on the file p3270.log. You can adjust th elog level by modifying it directly on the library.


## Contributing 
- Fork the project and create a new branch.
- Do some work. 
- Commit and push. 
- Open a Pull Request.


## License 
GPLv3. See the [LICENSE](LICENSE.txt) file.


