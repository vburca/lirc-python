import sys
import subprocess
import traceback

from subprocess import call
from __future__ import print_function

class Lirc(object):
    """Parses the lircd.conf file and can send remote commands through irsend.
    """
    codes = {}

    def __init__(self, conf="/etc/lirc/lircd.conf"):
        self._parse(conf)

    def _parse(self, conf):
        """Parse the lircd.conf config file and create a dictionary.
        """
        remote_name = None
        code_section = False

        # Open the config file
        try:
            with open(conf, 'rb') as fp:
                for line in fp:
                    # Convert tabs to spaces
                    l = line.replace('\t',' ')

                    # Look for a 'begin remote' line
                    if l.strip()=='begin remote':
                        # Got the start of a remote definition
                        remote_name = None
                        code_section = False

                    elif not remote_name and l.strip().find('name')>-1:
                        # Got the name of the remote
                        remote_name = l.strip().split(' ')[-1]
                        if remote_name not in self.codes:
                            self.codes[remote_name] = {}

                    elif remote_name and l.strip()=='end remote':
                        # Got to the end of a remote definition
                        remote_name = None

                    elif remote_name and l.strip()=='begin codes':
                        code_section = True

                    elif remote_name and l.strip()=='end codes':
                        code_section = False

                    elif remote_name and code_section:
                        # Got a code key/value pair... probably
                        fields = l.strip().split(' ')
                        self.codes[remote_name][fields[0]] = fields[-1]
            fp.close()
        except EnvironmentError as e:
            print_error("{0}: {1} (Errno {2})".format(e.strerror, e.filename, e.errno))
        except:
            print_error("Unexpected error:", traceback.format_exc())
            raise


    def devices(self):
        """Return a list of devices."""
        return self.codes.keys()

    def send_once(self, device_id, message):
        """Send single call to IR LED."""
        if (device_id not in self.devices()):
            print_error("{0} is not a valid device!".format(device_id))
            return False
        if (message not in self.codes[device_id].keys()):
            print_error("{0} is not a valid code for device {1}".format(message, device_id))
            return False

        try:
            result = call(['irsend', 'SEND_ONCE', device_id, message])
            if (result != 0):
              print_error("IRSEND command did not return a successful result code for call `irsend SEND_ONCE {0} {1}!".format(device_id, message))
              return False

            return True
        except EnvironmentError as e:
            filename = e.filename if e.filename is not None else ""
            print_error("{0} {1} (Errno {2})".format(e.strerror, filename, e.errno))
            return False
        except:
            print_error("Unexpected error:", traceback.format_exc())
            return False

if __name__ == "__main__":
    lirc = Lirc()

def print_error(*errs):
  print("ERROR:", *errs, file=sys.stderr)
