import unittest
from pygef.gef import ParseGEF


class RobertsonTest(unittest.TestCase):

    def setUp(self):
        self.gef = ParseGEF(string="""#GEFID= 1, 1, 0
                                    #FILEOWNER= Wagen 2
                                    #FILEDATE= 2004, 1, 14
                                    #PROJECTID= CPT, 146203
                                    #COLUMN= 3
                                    #COLUMNINFO= 1, m, Sondeerlengte, 1
                                    #COLUMNINFO= 2, MPa, Conuswaarde, 2
                                    #COLUMNINFO= 3, MPa, Wrijvingsweerstand, 3                                    
                                    #XYID= 31000, 132127.181, 458102.351, 0.000, 0.000
                                    #ZID= 31000, 1.3, 0.0
                                    #MEASUREMENTTEXT= 4, 030919, Conusnummer
                                    #MEASUREMENTTEXT= 6, NEN 5140, Norm
                                    #MEASUREMENTTEXT= 9, MV, fixed horizontal level
                                    #MEASUREMENTVAR= 20, 0.000000, MPa, Nulpunt conus voor sondering
                                    #MEASUREMENTVAR= 22, 0.000000, MPa, Nulpunt kleef voor sondering
                                    #MEASUREMENTVAR= 30, 0.000000, deg, Nulpunt helling voor sondering
                                    #PROCEDURECODE= GEF-CPT-Report, 1, 0, 0, -
                                    #TESTID= 4
                                    #PROJECTNAME= Uitbreiding Rijksweg 2
                                    #OS= DOS
                                    #EOH=
                                    0.0000e+000 0.0000e+000 0.0000e+000 
                                    1.0200e+000 7.1000e-001 4.6500e-002 
                                    1.0400e+000 7.3000e-001 4.2750e-002 
                                    1.0600e+000 6.9000e-001 3.9000e-002 
                                    1.0800e+000 6.1000e-001 3.6500e-002 
                                    1.1200e+000 6.5000e-001 4.5500e-002                                    
                                    """)


