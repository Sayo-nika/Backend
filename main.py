# Stdlib
import sys

# Sayonika Internals
from framework.objects import sayonika_instance, SETTINGS

sayonika_instance.debug = (len(sys.argv) > 1 and
                           sys.argv[1] == "--debug")
sayonika_instance.gather("routes")
sayonika_instance.run(SETTINGS["SERVER_BIND"], int(SETTINGS["SERVER_PORT"]))
