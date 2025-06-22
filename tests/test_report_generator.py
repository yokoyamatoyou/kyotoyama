import sys
import os
from unittest import mock

# Patch heavy modules before import
sys.modules['openai'] = mock.Mock()
sys.modules['PIL'] = mock.Mock()
sys.modules['PIL.Image'] = mock.Mock()
sys.modules['PIL'].Image = mock.Mock()

sys.path.insert(0, os.path.abspath('mvp-medical-app'))
from modules import report_generator


def test_generate_structured_report_uses_api_key():
    openai_mock = report_generator.openai
    client_mock = openai_mock.OpenAI.return_value
    completion_mock = client_mock.chat.completions.create
    completion_mock.return_value.choices = [mock.Mock(message=mock.Mock(content='{"is_finding_present": false}'))]
    def fake_save(buf, format=None):
        buf.write(b'data')

    img_mock1 = mock.Mock(save=mock.Mock(side_effect=fake_save))
    img_mock2 = mock.Mock(save=mock.Mock(side_effect=fake_save))
    report_generator.Image.fromarray.side_effect = [img_mock1, img_mock2]
    img_arr = mock.Mock(); img_arr.astype.return_value = []
    img = mock.Mock(); img.numpy.return_value = img_arr
    prob_arr = mock.MagicMock()
    prob_arr.__mul__.return_value = prob_arr
    prob_arr.astype.return_value = []
    prob = mock.Mock(); prob.numpy.return_value = prob_arr
    with mock.patch.object(report_generator.LesionFinding, 'model_validate_json', return_value={'ok': True}):
        result = report_generator.generate_structured_report(img, prob, 'key')
    openai_mock.OpenAI.assert_called_once_with(api_key='key')
    completion_mock.assert_called_once()
    assert result == {'ok': True}
