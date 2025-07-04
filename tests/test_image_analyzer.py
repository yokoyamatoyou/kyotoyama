import sys
import os
from unittest import mock
import numpy as np

# Patch heavy modules before import
sys.modules['ants'] = mock.Mock()
sys.modules['antspynet'] = mock.Mock()
sys.modules['antspynet.utilities'] = mock.Mock()

sys.path.insert(0, os.path.abspath('mvp-medical-app'))
from modules import image_analyzer


def test_analyze_image_calls_brain_extraction(tmp_path):
    data = b'123'
    with mock.patch.object(image_analyzer, 'ants') as ants_mock, \
         mock.patch.object(image_analyzer, 'brain_extraction') as brain_extraction_mock, \
         mock.patch.object(image_analyzer.ants, 'threshold_image') as threshold_mock:
        ants_mock.image_read.return_value = 'image'
        brain_extraction_mock.return_value = 'prob'
        threshold_mock.return_value = 'mask'
        result = image_analyzer.analyze_image(data)
        assert result['original_image'] == 'image'
        assert result['probability_mask'] == 'prob'
        assert result['segmentation_mask'] == 'mask'
        brain_extraction_mock.assert_called_once_with('image', modality='t1')


def test_save_overlay_png_uses_pil(tmp_path):
    overlay_img = mock.Mock()
    with mock.patch.object(image_analyzer, 'create_overlay_image', return_value=overlay_img) as create_mock:
        out = tmp_path / 'ov.png'
        image_analyzer.save_overlay_png('img', 'mask', out)
        create_mock.assert_called_once_with('img', 'mask', (255, 0, 0), 0.3)
        overlay_img.save.assert_called_once_with(out, format='PNG')


def test_overlay_png_bytes_returns_bytes():
    overlay_img = mock.Mock()
    with mock.patch.object(image_analyzer, 'create_overlay_image', return_value=overlay_img) as create_mock:
        overlay_img.save.side_effect = lambda buf, format=None: buf.write(b'data')
        result = image_analyzer.overlay_png_bytes('img', 'mask')
        create_mock.assert_called_once_with('img', 'mask', (255, 0, 0), 0.3)
        assert result == b'data'


def test_mask_patient_info_zeroes_top():
    img = mock.Mock()
    arr = np.ones((10, 10))
    img.numpy.return_value = arr
    img.origin = 'o'
    img.spacing = 's'
    img.direction = 'd'
    with mock.patch.object(image_analyzer.ants, "from_numpy", return_value="new") as fn:
        result = image_analyzer.mask_patient_info(img, 0.2)
        modified = fn.call_args[0][0]
    assert np.all(modified[:2] == 0)
    assert np.all(modified[2:] == 1)
    fn.assert_called_once()
    assert result == 'new'
