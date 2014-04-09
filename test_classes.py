import unittest
from parse_cloudy_output import *
from core import *

input_dict = {
    "column": [17.2,15.4,13.4],
    "ionization": [1.1,2.2,33.3],    
    "ionization_e": [0.5,1.2,2.3],
    "temp": [4.3,4.3,4.3],
    "temp_e": [3.2,32.,3.2]
}

class TestElement(unittest.TestCase):
    def setUp(self):
        self.inst = Element('H',**input_dict)
    def tearDown(self):
        pass
    def test_equal(self):
        other = Element('H',**input_dict)
        self.assertEqual(self.inst,other,'Equality not held')
        self.assertNotEqual(self.inst, Element('He',**input_dict),'wrongly equal')

class TestObsData(unittest.TestCase):
    def setUp(self):
        self.model=Element('H',**input_dict)
        self.obs = ObsData('H',0,column=[16.,17.,17.5])
    def tearDown(self):
        pass
    def test_correctFormatting(self):
        for item in input_dict.keys():
            val = getattr(self.obs,item)
            self.assertEqual(len(val),ions[self.obs.name])
            for it in val:
                self.assertEqual(len(it),3)
    def test_update(self):
        old = self.obs.ionization[0]
        self.obs._update(0,'ionization',[-1.,-2.,-3.])
        new = self.obs.ionization[0]
        self.assertTrue(old!=new,str(self.obs.ionization[0]))
    def test_equal(self):
        msg="model and obs not equal:\n\nmodel = %s \nobs = %s"%(str(self.model),str(self.obs))
        self.assertEqual(self.model,self.obs,msg)
        obs2 = ObsData('H',0,column=[12.2,13.,13.2])
        self.assertNotEqual(self.model,obs2,'model and obs wrongly equal')
    def test_join(self):
        other=ObsData('H',1,temp=[5.,5.1,-30.000])
        self.obs.join(other)
        for item in list(input_dict.keys()):
            self.assertEqual(getattr(self.obs,item)[1],getattr(other,item)[1])
    def test_append(self):
        self.obs.append(0,temp=[4.,4.5,5.])
        self.obs.append(1,column=[1.,2.,3.])
        self.assertEqual(self.obs.column[0],[16.,17.,17.5])
        self.assertEqual(self.obs.temp[0],[4.,4.5,5.])
        self.assertEqual(self.obs.column[1],[1.,2.,3.])
        self.obs.append(1,b=15.0)
        self.assertTrue(self.obs.temp[1]!=defaults)

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



