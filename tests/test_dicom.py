import sys
import os

sys.path.insert(0, os.path.abspath('mvp-medical-app'))
from modules import dicom
import pydicom
from pydicom.dataset import FileDataset, FileMetaDataset


def _make_dataset(patient_name: str) -> FileDataset:
    meta = FileMetaDataset()
    ds = FileDataset('test', {}, file_meta=meta, preamble=b'\0' * 128)
    ds.is_little_endian = True
    ds.is_implicit_VR = True
    ds.PatientName = patient_name
    return ds


def test_load_and_save_series(tmp_path):
    src = tmp_path / 'src'
    src.mkdir()
    ds = _make_dataset('Alice')
    ds.save_as(src / '1.dcm')

    loaded = dicom.load_series(src)
    assert len(loaded) == 1
    assert loaded[0].PatientName == 'Alice'

    dest = tmp_path / 'dest'
    dicom.save_series(dest, loaded)
    saved = list(dest.glob('*.dcm'))
    assert len(saved) == 1
    new_ds = pydicom.dcmread(saved[0])
    assert new_ds.PatientName == 'Alice'

