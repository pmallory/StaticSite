import os
import generate

class TestGenerate:
    def setUp(self):
        with open('./file.html', 'w') as file:
            file.write(r'hello world!')

    def tearDown(self):
        os.remove('./file.html')

    def test_diff1(self):
        assert generate.diff('hello world!', './file.html') 
    def test_diff2(self):
        assert generate.diff('nope', './file.html') is False 
    def test_diff3(self):
        assert generate.diff('./file.html', 'txt') is False
    def test_diff4(self):
       assert generate.diff('txt', 'invalid file!') is False
