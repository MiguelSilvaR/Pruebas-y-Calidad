"""
Shared unittest helpers to avoid duplicated setup/cleanup code.
"""

import shutil
import tempfile
import unittest


class TempDirTestCase(unittest.TestCase):
    """
    TestCase that provides a temporary
    directory cleaned up automatically.
    """

    def setUp(self):
        """Create a temporary directory and register cleanup."""
        super().setUp()
        self.tmp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp_dir, ignore_errors=True)
