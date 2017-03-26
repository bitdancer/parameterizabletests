import unittest

from parameterizabletests import parameterizable, parameters, C


class TestParaterizableTests(unittest.TestCase):

    def runTest(self, testcase, testname):
        res = unittest.TestResult()
        testcase(methodName=testname).run(res)
        self.assertEqual(1, res.testsRun)
        self.assertEqual([], res.failures)
        self.assertEqual([], res.errors)
        self.assertTrue(res.wasSuccessful())

    def test_normal_tests_run(self):
        res = []
        @parameterizable
        class Test(unittest.TestCase):
            def test_normal_tests_run(self):
                res.append(1)
            @parameters()
            def test_foo(self):
                raise Exception("This should not be run in this test")
        self.runTest(Test, 'test_normal_tests_run')

    def test_parameterizable(self):
        @parameterizable
        class Test(unittest.TestCase):
            @parameters()
            def test_foo(self):
                raise Exception("This should not be run in this test")
        with self.assertRaises(ValueError):
            Test(methodName='test_foo').run()

    def test_single_arg_parameters(self):
        res = []
        @parameterizable
        class Test(unittest.TestCase):
            @parameters(C(1), C(2))
            def test_foo(self, arg):
                res.append(arg)
        self.runTest(Test, 'test_foo_1')
        self.assertEqual([1], res)
        self.runTest(Test, 'test_foo_2')
        self.assertEqual([1, 2], res)
        with self.assertRaises(ValueError):
            Test(methodName='test_foo_3').run()

    def test_multiple_arg_parameters(self):
        res = []
        @parameterizable
        class Test(unittest.TestCase):
            @parameters(C(1, 7), C(2, 3))
            def test_foo(self, *args):
                res.append(args)
        self.runTest(Test, 'test_foo_1_7')
        self.assertEqual([(1, 7)], res)
        self.runTest(Test, 'test_foo_2_3')
        self.assertEqual([(1, 7), (2, 3)], res)

    def test_list_of_Cs(self):
        res = []
        @parameterizable
        class Test(unittest.TestCase):
            @parameters(C(1, b=7), C(2, c=3), C(a=1, b=2, c=3), C(4, 5, 6))
            def test_foo(self, a, b=100, c=200):
                res.append((a, b, c))
        self.runTest(Test, 'test_foo_1__b_7')
        self.runTest(Test, 'test_foo_2__c_3')
        self.runTest(Test, 'test_foo_4_5_6')
        self.assertEqual([(1, 7, 200), (2, 100, 3), (4, 5, 6)], res)
        # XXX This will not pass consistently on 3.3-3.5, so don't run it.
        #self.runTest(Test, 'test_foo_a_1__b_2__c_3')
        #self.assertEqual([(1, 7, 200), (2, 100, 3), (4, 5, 6), (1, 2, 3)], res)

    def test_keyword_parameters(self):
        res = []
        @parameterizable
        class Test(unittest.TestCase):
            @parameters(foo=C(a=1, b=2), bar=C(b=7))
            def test_foo(self, a=None, b=None):
                res.append((a, b))
        self.runTest(Test, 'test_foo_foo')
        self.runTest(Test, 'test_foo_bar')
        self.assertEqual([(1, 2), (None, 7)], res)

    def test_dict_parameters_as_single_arg(self):
        res = []
        @parameterizable
        class Test(unittest.TestCase):
            @parameters(dict(foo=C(a=1, b=2), bar=C(b=7)))
            def test_foo(self, a=None, b=None):
                res.append((a, b))
        self.runTest(Test, 'test_foo_foo')
        self.runTest(Test, 'test_foo_bar')
        self.assertEqual([(1, 2), (None, 7)], res)

    def test__include_key(self):
        res = []
        @parameterizable
        class Test(unittest.TestCase):
            @parameters(a=C(1, 7), b=C(2, 8), _include_key=True)
            def test_bar(self, *args):
                res.append(args)
        self.runTest(Test, 'test_bar_a')
        self.runTest(Test, 'test_bar_b')
        self.assertEqual([('a', 1, 7), ('b', 2, 8)], res)

    def test_mixed_positionals_and_keywords(self):
        res = []
        @parameterizable
        class Test(unittest.TestCase):
            @parameters(C(1), b=C(1, k=3))
            def test_bar(self, z, k=None):
                res.append((z, k))
        self.runTest(Test, 'test_bar_1')
        self.runTest(Test, 'test_bar_b')
        self.assertEqual([(1, None), (1, 3)], res)

    def test_invalid_setting_raises(self):
        with self.assertRaises(TypeError):
            @parameterizable
            class Test(unittest.TestCase):
                @parameters(a=1, b=2, _nosuch_setting=True)
                def test_bar(self, *args):
                    pass

    def test_duplicate_test_names_raises(self):
        with self.assertRaises(NameError):
            @parameterizable
            class Test(unittest.TestCase):
                # Both of these would be named 'test_a'
                @parameters(C('a'), a=C(1))
                def test_bar(self, *args):
                    pass


if __name__=='__main__':
    unittest.main()
