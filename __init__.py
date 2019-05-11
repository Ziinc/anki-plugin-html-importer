import sys, os
vendor_dir = os.path.join(os.getcwd(), 'vendor')

sys.path.append(vendor_dir)
from . import src