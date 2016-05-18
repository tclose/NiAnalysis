import os.path
import shutil
from neuroanalysis.diffusion import DiffusionDataset
from neuroanalysis.archive import LocalArchive
if __name__ == '__main__':
    from utils import DummyTestCase as TestCase  # @UnusedImport
else:
    from unittest import TestCase  # @Reimport


ARCHIVE_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '_data', 'test_archive'))
WORK_PATH = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '_data', 'work', 'diffusion'))


class TestDiffusion(TestCase):

    NODDI_PROJECT = 'noddi-test'
    NODDI_SUBJECT = 'PILOT1'
    NODDI_SESSION = 'SESSION1'

    def setUp(self):
        shutil.rmtree(WORK_PATH, ignore_errors=True)
        os.makedirs(WORK_PATH)
        self.dataset = DiffusionDataset(
            project_id=self.NODDI_PROJECT, archive=LocalArchive(ARCHIVE_PATH),
            scan_names={'forward_rpe.mif': 'r-l_noddi_b0_6',
                        'reverse_rpe.mif': 'pre_l-r_noddi_b0_6',
                        'diffusion.mif': 'r-l_noddi_b700_30_directions'})

    def tearDown(self):
        shutil.rmtree(WORK_PATH, ignore_errors=True)

    def test_preprocess(self):
        self.dataset.preprocess_pipeline().run()


if __name__ == '__main__':
    tester = TestDiffusion()
    tester.setUp()
    tester.test_preprocess()
