import sys
import os
from unittest import mock

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
