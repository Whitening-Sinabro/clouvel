# Pytest configuration for Clouvel tests

import os

# Disable Rich UI during tests to get predictable plain text output
os.environ["CLOUVEL_NO_RICH"] = "1"
