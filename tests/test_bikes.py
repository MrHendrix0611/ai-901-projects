import os
import sys
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'projetos'/'01-ecopredictor'))
_module_path = Path(__file__).resolve().parents[1] / 'projetos' / '01-ecopredictor' / 'app.py'
_spec = importlib.util.spec_from_file_location('bike_app_under_test', _module_path)
bike = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bike)

class TestBike(unittest.TestCase):
    def setUp(self):
        self.c=bike.app.test_client()
        self.fields={
          'dia':'14','mes':'10','ano':'2012','estacao':'4','feriado':'0',
          'dia_semana':'0','dia_util':'0','situacao_climatica':'1',
          'temperatura':'0.5','sensacao_termica':'0.5','umidade':'0.55','velocidade_vento':'0.18'
        }
    def test_demo(self):
        with patch.dict(os.environ,{'APP_MODE':'demo'}):
            response=self.c.post('/predict',data=self.fields)
        self.assertEqual(response.status_code,200)
        payload=response.get_json()
        self.assertTrue(payload['demo'])
        self.assertIsInstance(payload['Results'][0],float)
        self.assertIn('SIMULAÇÃO',payload['notice'])
    def test_validation(self):
        response=self.c.post('/predict',data={'dia':'999'})
        self.assertEqual(response.status_code,400)
    def test_azure_missing_config(self):
        with patch.dict(os.environ,{'APP_MODE':'azure','AZURE_ML_ENDPOINT':'','AZURE_ML_KEY':''}):
            response=self.c.post('/predict',data=self.fields)
        self.assertEqual(response.status_code,503)
    def test_normalize(self):
        self.assertEqual(bike.normalize_prediction({'Results':[132.3]}),132.3)
        self.assertEqual(bike.normalize_prediction([{'alugueis':80}]),80)

if __name__=='__main__':unittest.main()
