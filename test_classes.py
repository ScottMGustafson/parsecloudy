import unittest
from parse_cloudy_output import *

input_dict = {
    "column": [17.2,15.4,13.4],
    "ionization": [1.1,2.2,33.3],    
    "ionization_e": [0.5,1.2,2.3],
    "temp": [4.3,4.3,4.3],
    "temp_e": [3.2,32.,3.2]
}

class TestElement(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_equal(self):
        inst = Element('H',**input_dict)
        other = Element('H',**input_dict)
        self.assertEqual(inst,other,'Equality not held')
        self.assertNotEqual(inst, Element('He',**input_dict),'wrongly equal')

class TestObsData(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_equal(self):
        model=Element('H',**input_dict)
        obs = ObsData('H',0,column=[16.,17.,17.5])
        msg="model and obs not equal:\n\nmodel = %s \nobs = %s"%(str(model),str(obs))
        self.assertEqual(model,obs,msg)
        obs = ObsData('H',0,column=[12.2,13.,13.2])
        self.assertNotEqual(model,obs,'model and obs wrongly equal')
    def test_join(self):
        obs = ObsData('H',0,column=[16.,17.,17.5])
        other=ObsData('H',1,column=[15.,16.,16.5])
        obs.join(other)
        for item in list(input_dict.keys()):
            self.assertEqual(getattr(obs,item)[1],getattr(other,item)[1])

class TestModel(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

class TestFns(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_getind(self):
        fstream = ['hi', 'there', 'find', '', '\n', 'me'] 
        self.assertEqual(get_ind(fstream,'me'), 5)



