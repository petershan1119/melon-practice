from io import BytesIO

import magic
import requests


def download(url, file_name):
    response = requests.get(url)
    binary_data = response.content
    temp_file = BytesIO()
    temp_file.write(binary_data)

    temp_file.seek(0)
    mine_type = magic.from_buffer(temp_file.read(), mime=True)
    temp_file.seek(0)
    result = '{file_name}.{ext}'.format(
        file_name=file_name,
        ext=mine_type.split('/')[-1]
    )
    return result, temp_file