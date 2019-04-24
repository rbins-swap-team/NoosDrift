from noosDrift.settings import *

# STATIC_ROOT is only tolerated to generate the content of static directory
# otherwise comment it
STATIC_ROOT = STATIC_DIR

if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)
