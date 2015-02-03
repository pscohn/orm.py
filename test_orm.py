import unittest
import orm

class UtilTests(unittest.TestCase):
    def test_camel_to_under(self):
        t = 'TestClassName'
        r = 'test_class_name'
        self.assertEqual(r, orm.camel_to_underscores(t))
    def test_under_to_under(self):
        t = 'test_class_name'
        self.assertEqual(t, orm.camel_to_underscores(t))
    
if __name__ == "__main__": unittest.main()
