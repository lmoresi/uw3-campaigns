"""Run pytest under the campaign runner (rank cap, supervision, logs):
driver = this file, args = pytest arguments. Exit code is pytest's."""
import sys

import pytest

sys.exit(pytest.main(sys.argv[1:]))
