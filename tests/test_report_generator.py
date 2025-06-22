import sys
import os
from unittest import mock

# Patch heavy modules before import
sys.modules['google'] = mock.Mock()
sys.modules['google.generativeai'] = mock.Mock()
sys.modules['PIL'] = mock.Mock()
sys.modules['PIL.Image'] = mock.Mock()
sys.modules['PIL'].Image = mock.Mock()

sys.path.insert(0, os.path.abspath('mvp-medical-app'))
from modules import report_generator


def test_generate_structured_report_uses_api_key():
    genai_mock = report_generator.genai
    model_mock = mock.Mock()
    genai_mock.GenerationConfig.return_value = 'cfg'
    genai_mock.GenerativeModel.return_value = model_mock
    model_mock.generate_content.return_value.text = '{"is_finding_present": false}'
    report_generator.Image.fromarray.return_value = 'img'
    img_arr = mock.Mock(); img_arr.astype.return_value = []
    img = mock.Mock(); img.numpy.return_value = img_arr
    prob_arr = mock.MagicMock()
    prob_arr.__mul__.return_value = prob_arr
    prob_arr.astype.return_value = []
    prob = mock.Mock(); prob.numpy.return_value = prob_arr
    with mock.patch.object(report_generator.LesionFinding, 'model_validate_json', return_value={'ok': True}):
        result = report_generator.generate_structured_report(img, prob, 'key')
    genai_mock.configure.assert_called_once_with(api_key='key')
    assert result == {'ok': True}
