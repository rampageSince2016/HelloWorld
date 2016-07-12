from unittest import TestCase

import EnglishWord as ew

class T_English(TestCase):
    def test_console_command(self):
        ew.loopInput()
