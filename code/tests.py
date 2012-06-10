import unittest

from pipeline import *
from decompress import Decompressor

from pylab import *
from analysis import *

class TestAnalysis(unittest.TestCase):
    def test_reconerror(self):
        self.assertEqual(recon_error(np.array([1,1,1]),np.array([1,1,1]))[0],1.0)
        rerr = recon_error(np.array([1.,0.5,1.]),np.array([1.,0.9,1.]))
        assertTrue(rerr < 1)
        assertTrue(rerr > 0)


def get_compress_input():
    input = {} 
    input['hosts'] = []
    for i in range(1, 65):
        input['hosts'].append('cloud%d'%(i))

    input['start'] = '2011/11/22-15:00:00'
    input['end'] = '2011/11/24-23:45:00'

    input['metrics'] = ['iostat.disk.read_requests',
                        'iostat.disk.write_requests']
    return input

class TestCompression(unittest.TestCase):
    def setUp(self):
        cfg = getconfig()
        self.tmpdir = cfg["tmpdir"][3:]
        self.pipe = get_default_pipeline()
        self.pipe.append_stage(CompressionStage(self.tmpdir))
        self.pipe.set_skipstages(["KalmanStage","DrawStage"])
        self.pipe.get_stages("SpiritStage")[0].ispca = True

    def test_docompress(self):
        output = self.pipe.run(get_compress_input())
        target = os.path.join(self.tmpdir,"compressed.npz")
        self.assertTrue(os.path.exists(target),
            "No compression output file")

        decomp = Decompressor(target)
        recon = decomp.decompress()

        for tsn in xrange(recon.shape[0]):
            err = recon_error(output["data"][tsn][-1], recon[tsn,:])
            self.assertTrue(err[0] > 0.7, "Expected stream reconstruction accuracy > 0.7")

            #to examine reconstruction versus original:
            examine = False
            if examine and tsn == 6:
               plot(output["data"][tsn][-1],'r')
               plot(recon[tsn,:],'b')
               show()

    def tearDown(self):
        pass

if __name__ == '__main__':
    #to run individual tests:
    #python -m unittest tests.<classname>
    unittest.main()