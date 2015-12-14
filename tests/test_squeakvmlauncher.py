import pytest
import squeakvmlauncher
import os
import subprocess

TEST_CONFIG_FILE = '_testconfig.txt'
# edit these to valid paths in your environment
SPUR_IMAGE_6521 = r'C:\Squeak\Programmiersprachen.spurimage'
NON_SPUR_IMAGE_6505 = r'C:\Squeak\Gramadav08.image'

@pytest.yield_fixture(autouse=True)
def use_testconfig_file(monkeypatch):
    import configparser
    remove_test_config_file()
    monkeypatch.setattr(squeakvmlauncher, 'CONFIG_FILE', TEST_CONFIG_FILE)
    monkeypatch.setattr(squeakvmlauncher, 'config_parser', configparser.RawConfigParser())
    yield None
    remove_test_config_file()

def remove_test_config_file():
    try:
        os.remove(TEST_CONFIG_FILE)
    except FileNotFoundError:
        pass

@pytest.fixture
def subprocess_call_stub(monkeypatch):
    class CallStub:
        def __init__(self):
            self.cmdline = None
        def __call__(self, *args):
            self.cmdline = args[0]
    call_stub = CallStub()
    monkeypatch.setattr(subprocess, 'call', call_stub)
    return call_stub

def test_launch_from_gui(subprocess_call_stub, monkeypatch):
    monkeypatch.setattr(squeakvmlauncher, 'choose_with_gui', lambda v: r'squeakfromgui.exe')
    squeakvmlauncher.launch_squeak(SPUR_IMAGE_6521)
    assert subprocess_call_stub.cmdline == ["squeakfromgui.exe", SPUR_IMAGE_6521]

def test_launch_from_config(subprocess_call_stub):
    with open(TEST_CONFIG_FILE, 'w') as f:
        f.write("""[VMs]
6521 = squeakfromconfig.exe
""")
    squeakvmlauncher.launch_squeak(SPUR_IMAGE_6521)
    assert subprocess_call_stub.cmdline == ["squeakfromconfig.exe", SPUR_IMAGE_6521]

def test_magic_reading():
    with open(SPUR_IMAGE_6521, 'rb') as f:
        assert squeakvmlauncher.read_magic_version_number(f) == 6521
    with open(NON_SPUR_IMAGE_6505, 'rb') as f:
        assert squeakvmlauncher.read_magic_version_number(f) == 6505

def _test_interactive_chooser(subprocess_call_stub):
    squeakvmlauncher.launch_squeak(SPUR_IMAGE_6521)

def test_config_lookup_and_store(monkeypatch):
    monkeypatch.setattr(squeakvmlauncher, 'choose_with_gui', lambda v: 'squeakfromgui.exe')
    assert squeakvmlauncher.vm_executable_for_version(6521) == 'squeakfromgui.exe'
    with open(TEST_CONFIG_FILE, 'r') as f:
        assert f.read() == """[VMs]
6521 = squeakfromgui.exe

"""
    given_file_contents = """[VMs]
6521 = squeakinconfigfile.exe
"""
    with open(TEST_CONFIG_FILE, 'w') as f:
        f.write(given_file_contents)
    assert squeakvmlauncher.vm_executable_for_version(6521) == 'squeakinconfigfile.exe'
    with open(TEST_CONFIG_FILE, 'r') as f:
        assert f.read() == given_file_contents, 'File was modified'
    assert squeakvmlauncher.vm_executable_for_version(6505) == 'squeakfromgui.exe'
