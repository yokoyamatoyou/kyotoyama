import sys
import os
from unittest import mock

sys.modules['openai'] = mock.Mock()
sys.modules['PIL'] = mock.Mock()
sys.modules['PIL.Image'] = mock.Mock()
sys.modules['PIL'].Image = mock.Mock()

sys.path.insert(0, os.path.abspath('mvp-medical-app'))
from modules import ocr


def test_extract_burned_in_text_calls_api():
    client_mock = ocr.openai.OpenAI.return_value
    completion_mock = client_mock.chat.completions.create
    completion_mock.return_value.choices = [mock.Mock(message=mock.Mock(content='TXT'))]

    img_mock = mock.Mock()
    img_mock.numpy.return_value = mock.Mock(astype=lambda t: [])

    with mock.patch.object(ocr, 'mask_patient_info', return_value=img_mock):
        result = ocr.extract_burned_in_text(img_mock, 'k')

    ocr.openai.OpenAI.assert_called_once_with(api_key='k')
    completion_mock.assert_called_once()
    assert result == 'TXT'
