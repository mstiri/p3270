from io import BytesIO, StringIO
import sys
import unittest
from unittest.mock import Mock, patch
from p3270 import P3270Client, S3270, InvalidConfiguration


class TestP3270Client(unittest.TestCase):

    def setUp(self):
        self.invalidConnectResponse = BytesIO(b'data: Connect to localhost, port 58001: Connection refused\n'
                                              + b'L U U N N 2 24 80 0 0 0x0 -\n'
                                              + b'error')
        self.validResponse = BytesIO(b'U F U C(localhost) I 2 24 80 8 2 0x0 0.000\n'
                                     + b'ok')
        self.invalidResponse = BytesIO(b'\n'
                                       + b'')
        self.disconnectedResponse = BytesIO(b'data: Unknown action: NoOpCommand\n'
                                            + b'L U U N N 2 24 80 0 0 0x0 -\n'
                                            + b'error')
        self.popenPatcher = patch('subprocess.Popen')
        self.popenMock = self.popenPatcher.start()
        self.client1 = P3270Client(configFile="p3270_ok.cfg")
        self.client3 = P3270Client(configFile="p3270_tls_ok.cfg")
        with open('screen.data', 'r') as fData:
            self.screenData = fData.read().encode()
        with open('screen.txt', 'r') as fText:
            self.screenText = '*' * 80 + '\n'
            self.screenText += fText.read()
            self.screenText += '*' * 80 + '\n'
        self.validResponseWithData = BytesIO(self.screenData
                                             + b'U F U C(localhost) I 2 24 80 8 2 0x0 0.000\n'
                                             + b'ok')

    def tearDown(self):
        self.popenPatcher.stop()

    def checkStdin(self, cmd):
        self.popenMock.return_value.stdin.write.assert_called_once_with(cmd)

    def resetMock(self):
        self.popenMock.reset_mock()
        self.popenMock.return_value.stdout = self.validResponse

    def test_creation(self):
        self.assertTrue(self.client1.conf.isValid())
        with self.assertRaises(InvalidConfiguration):
            self.client2 = P3270Client(configFile="p3270_ko.cfg")

    def test_connect_ok(self):
        cmd = b'Connect(B:LU01QSWJ@localhost)\n'
        self.resetMock()
        assert self.client1.connect()
        self.checkStdin(cmd)

    def test_tls_connect_ok(self):
        cmd_tls = b'Connect(L:LU01QSWJ@localhost)\n'
        self.resetMock()
        assert self.client3.connect()
        self.checkStdin(cmd_tls)

    def test_connect_ko(self):
        # Unsuccessful connection request 
        self.popenMock.reset_mock()
        self.popenMock.return_value.stdout = self.invalidConnectResponse
        assert not self.client1.connect()
        # The following test fails on python 3.5 as in :
        #     https://github.com/rm-hull/luma.oled/issues/55
        # Anyway I am covering tests on writes on stdin in other cases
        # self.popenMock.return_value.stdin.write.assert_called_once()

    def test_disconnect(self):
        cmd = b'Disconnect\n'
        self.resetMock()
        assert self.client1.disconnect()
        self.checkStdin(cmd)

    def test_endSession(self):
        # End session quits the scripts. So there is no stdout to check
        cmd = b'Quit\n'
        self.popenMock.reset_mock()
        self.client1.endSession()
        self.checkStdin(cmd)

    def test_sendEnter(self):
        cmd = b'Enter\n'
        self.resetMock()
        assert self.client1.sendEnter()
        self.checkStdin(cmd)

    def test_sendPF(self):
        cmd = b'PF(7)\n'
        self.resetMock()
        assert self.client1.sendPF(7)
        self.checkStdin(cmd)
        self.popenMock.reset_mock()
        assert not self.client1.sendPF(37)
        assert not self.client1.sendPF('q')
        assert not self.client1.sendPF(-3)
        self.popenMock.return_value.stdin.write.assert_not_called()

    def test_sendPA(self):
        cmd = b'PA(3)\n'
        self.resetMock()
        assert self.client1.sendPA(3)
        self.checkStdin(cmd)
        self.popenMock.reset_mock()
        assert not self.client1.sendPA(5)
        assert not self.client1.sendPA('b')
        assert not self.client1.sendPA(-3)
        self.popenMock.return_value.stdin.write.assert_not_called()

    def test_sendBackSpace(self):
        cmd = b'BackSpace\n'
        self.resetMock()
        assert self.client1.sendBackSpace()
        self.checkStdin(cmd)

    def test_sendBackTab(self):
        cmd = b'BackTab\n'
        self.resetMock()
        assert self.client1.sendBackTab()
        self.checkStdin(cmd)

    def test_sendTab(self):
        cmd = b'Tab\n'
        self.resetMock()
        assert self.client1.sendTab()
        self.checkStdin(cmd)

    def test_clearScreen(self):
        cmd = b'Clear\n'
        self.resetMock()
        assert self.client1.clearScreen()
        self.checkStdin(cmd)

    def test_delChar(self):
        cmd = b'Delete\n'
        self.resetMock()
        assert self.client1.delChar()
        self.checkStdin(cmd)

    def test_delField(self):
        cmd = b'DeleteField\n'
        self.resetMock()
        assert self.client1.delField()
        self.checkStdin(cmd)

    def test_eraseChar(self):
        cmd = b'Erase\n'
        self.resetMock()
        assert self.client1.eraseChar()
        self.checkStdin(cmd)

    def test_moveCursorDown(self):
        cmd = b'Down\n'
        self.resetMock()
        assert self.client1.moveCursorDown()
        self.checkStdin(cmd)

    def test_moveCursorUp(self):
        cmd = b'Up\n'
        self.resetMock()
        assert self.client1.moveCursorUp()
        self.checkStdin(cmd)

    def test_moveCursorLeft(self):
        cmd = b'Left\n'
        self.resetMock()
        assert self.client1.moveCursorLeft()
        self.checkStdin(cmd)

    def test_moveCursorRight(self):
        cmd = b'Right\n'
        self.resetMock()
        assert self.client1.moveCursorRight()
        self.checkStdin(cmd)

    def test_moveTo(self):
        cmd = b'MoveCursor(4, 19)\n'
        self.resetMock()
        assert self.client1.moveTo(5, 20)
        self.checkStdin(cmd)

    def test_moveToNegative(self):
        # Do not worry, a negative value is considered as '0' by s3270
        cmd = b'MoveCursor(-11, -11)\n'
        self.resetMock()
        assert self.client1.moveTo(-10, -10)
        self.checkStdin(cmd)

    def test_moveToFirstInputField(self):
        cmd = b'Home\n'
        self.resetMock()
        assert self.client1.moveToFirstInputField()
        self.checkStdin(cmd)

    def test_sendText(self):
        cmd = b'String("CEMT I TASK")\n'
        self.resetMock()
        assert self.client1.sendText('CEMT I TASK')
        self.checkStdin(cmd)

    def test_saveScreenHTML(self):
        screens_dir = self.client1.conf.screensDir
        cmd = b'PrintText(html, {}/myscreen.html)\n'.decode().format(screens_dir).encode()
        self.resetMock()
        assert self.client1.saveScreen('myscreen.html')
        self.checkStdin(cmd)

    def test_saveScreenRTF(self):
        screens_dir = self.client1.conf.screensDir
        cmd = b'PrintText(rtf, {}/myscreen.rtf)\n'.decode().format(screens_dir).encode()
        self.resetMock()
        assert self.client1.saveScreen('myscreen.rtf', 'rtf')
        self.checkStdin(cmd)

    def test_saveScrennPDF(self):
        assert not self.client1.saveScreen('myscreen.pdf', 'pdf')

    def test_isConnected(self):
        self.resetMock()
        cmd = b'NoOpCommand\n'
        assert self.client1.isConnected()
        self.checkStdin(cmd)

    def test_isConnectedWhileNotConnected(self):
        self.popenMock.reset_mock()
        self.popenMock.return_value.stdout = self.disconnectedResponse
        cmd = b'NoOpCommand\n'
        assert not self.client1.isConnected()
        self.checkStdin(cmd)
        assert self.client1.s3270.buffer == 'Unknown action: NoOpCommand'

    def test_statusMessage(self):
        self.resetMock()
        self.client1.sendEnter()
        statusMessage = self.client1.s3270.statusMsg
        assert statusMessage.isValid()
        assert statusMessage.keyboardState() == 'Unlocked'
        assert statusMessage.screenFormatting() == 'Formatted'
        assert statusMessage.fieldProtection() == 'Unprotected'
        assert statusMessage.connectionState()
        assert statusMessage.emulatorMode() == '3270'
        assert statusMessage.modelNumber() == '2'
        assert statusMessage.screenDefinition() == (24, 80)
        assert statusMessage.cursorPosition() == (9, 3)
        assert statusMessage.windowId() == '0x0'
        assert statusMessage.execTime() == '0.000'

    def test_printScreen(self):
        cmd = b'PrintText(string)\n'
        self.popenMock.reset_mock()
        self.popenMock.return_value.stdout = self.validResponseWithData
        with patch('sys.stdout', new_callable=StringIO) as fakeStdout:
            self.client1.printScreen()
            self.checkStdin(cmd)
            self.assertEqual(fakeStdout.getvalue(), self.screenText)

    def test_invalidStatusMessage(self):
        self.popenMock.reset_mock()
        self.popenMock.return_value.stdout = self.invalidResponse
        self.client1.isConnected()
        statusMessage = self.client1.s3270.statusMsg
        assert not statusMessage.isValid()
        assert statusMessage.keyboardState() == None
        assert statusMessage.screenFormatting() == None
        assert statusMessage.fieldProtection() == None
        assert statusMessage.connectionState() == None
        assert statusMessage.emulatorMode() == None
        assert statusMessage.modelNumber() == None
        assert statusMessage.screenDefinition() == None
        assert statusMessage.cursorPosition() == None
        assert statusMessage.windowId() == None
        assert statusMessage.execTime() == None


if __name__ == '__main__':
    unittest.main()
