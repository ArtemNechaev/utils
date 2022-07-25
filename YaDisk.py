import requests
import os


class YaDisk():
    URL = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, token):
        self.headers = {'Content-Type': 'application/json',
                        'Accept': 'application/json', 'Authorization': f'OAuth {token}'}

    def create_folder(self, path):
        res = requests.put(f'{self.URL}?path={path}', headers=self.headers)

    def listdir(self, path):
        res = requests.get(
            f'{self.URL}?path={path}&fields=_embedded.items.name,_embedded.items.type, _embedded.items.file', headers=self.headers).json()
        return res

    def upload_file(self, source_path, target_path, replace=False):

        res = requests.get(
            f'{self.URL}/upload?path={target_path}&overwrite={replace}', headers=self.headers).json()
        with open(source_path, 'rb') as f:
            try:
                requests.put(res['href'], files={'file': f})
            except KeyError:
                print(res)

    def download_file(self, source_path, target_path):
        res = requests.get(
            f'{self.URL}/download?path={source_path}', headers=self.headers).json()
        try:
            res = requests.get(res['href'])
            open(target_path.strip('/'), 'wb').write(res.content)
        except KeyError:
            print(res)


    def upload_dir(self, source_dir, target_dir, replace=False, recursion = True):
        self.create_folder(target_dir)
        items = os.listdir(source_dir.strip('/'))
        for item in items:
            source_path = source_dir.strip('/') + '/' + item
            target_path = target_dir.strip('/') + '/' + item

            if os.path.isdir(source_path):
                if not recursion:
                    continue
                self.upload_dir(source_path, target_path, replace)
            else:
                self.upload_file(source_path, target_path, replace)

    def download_dir(self, source_dir, target_dir, recursion = True):
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)
        items = self.listdir(source_dir)['_embedded']['items']
        for item in items:

            source_path = source_dir.strip('/') + '/' + item['name']
            target_path = target_dir.strip('/') + '/' + item['name']

            if item['type'] == 'dir':
                if not recursion:
                    continue
                self.download_dir(source_path, target_path)
            elif item['type'] == 'file':
                res = requests.get(item['file'])
                open(target_path.strip('/'), 'wb').write(res.content)
