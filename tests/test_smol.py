import os
import Smol
import unittest
import tempfile

class smolTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, Smol.app.config['DATABASE'] = tempfile.mkstemp()
        Smol.app.testing = True
        self.app = Smol.app.test_client()
        with Smol.app.app_context():
            Smol.Smol.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(Smol.app.config['DATABASE'])

    def shorten(self, original):
        return self.app.post('/shorten', data=dict(
                original = original
            ), follow_redirects=True)

    def test_shorten(self):
        rv = self.shorten('https://github.com/')
        assert 

if __name__ == '__main__':
    unittest.main()