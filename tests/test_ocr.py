import os
import sys
import importlib.util
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'projetos'/'02-ocr-document-intelligence'))
_module_path = Path(__file__).resolve().parents[1] / 'projetos' / '02-ocr-document-intelligence' / 'app.py'
_spec = importlib.util.spec_from_file_location('ocr_app_under_test', _module_path)
ocr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ocr)

class TestOCR(unittest.TestCase):
    def setUp(self):self.c=ocr.app.test_client()
    def sample(self):
        img=Image.new('RGB',(40,30),'white')
        content=BytesIO();img.save(content,format='PNG');content.seek(0)
        return content
    def test_demo(self):
        with patch.dict(os.environ,{'APP_MODE':'demo'}):
            r=self.c.post('/api/analyze',data={'image':(self.sample(),'sample.png')})
        self.assertEqual(r.status_code,200)
        self.assertTrue(r.get_json()['demo'])
        self.assertIn('SIMULAÇÃO',r.get_json()['notice'])
    def test_bad_file(self):
        r=self.c.post('/api/analyze',data={'image':(BytesIO(b'not an image'),'sample.png')})
        self.assertEqual(r.status_code,415)
    def test_missing_image(self):
        self.assertEqual(self.c.post('/api/analyze').status_code,400)

if __name__=='__main__':unittest.main()
