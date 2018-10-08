import sys

from framework.objects import sayonika_instance

sayonika_instance.debug = (len(sys.argv) > 1 and
                           sys.argv[1] == "--debug")
sayonika_instance.gather("routes")
sayonika_instance.run()
