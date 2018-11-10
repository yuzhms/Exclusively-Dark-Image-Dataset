import datetime
import os
from PIL import Image
import json
import shutil

# flag turn on to split and copy image
SPILT = False

CLASSID = {
    'Bicycle': 1, 'Boat': 2, 'Bottle': 3, 'Bus': 4, 'Car': 5, 'Cat': 6,
    'Chair': 7, 'Cup': 8, 'Dog': 9, 'Motorbike': 10, 'People': 11, 'Table': 12
}
LIGHTID = {
    'Low': 1, 'Ambient': 2, 'Object': 3, 'Single': 4, 'Weak': 5,
    'Strong': 6, 'Screen': 7, 'Window': 8, 'Shadow': 9, 'Twilight': 10
}
id2cls = {v: k for k, v in CLASSID.items()}

class ExDark():
    def __init__(self, datapath):
        self.info = {
            "year": 2018,
            "version": "1.0",
            "description": "ExDark Dataset convert to coco format",
            "contributor": "yuzhms",
            "url": "",
            "date_create": datetime.datetime.today().isoformat(" ")
        }
        self.licenses = [{
            'id': 1,
            'name': 'GPL-3.0',
            'url': 'https://github.com/cs-chan/Exclusively-Dark-Image-Dataset/blob/master/LICENSE'
        }]
        self.type = 'instances'
        self.categories = []
        self.meta_data = {}

        self._datapath = datapath
        self.__global_id = 1

        self.__read_list()
        self.__create_categories()

        for name, meta in self.meta_data.items():
            images, annotaions = self.__get_image_annotation_pair(meta, name)
            json_data = {
                'info': self.info,
                'images': images,
                'license': self.licenses,
                'annotations': annotaions,
                'categories': self.categories,
                'type': self.type
            }
            with open(os.path.join(self._datapath, 'ExDark_' + name + '.json'), 'w') as jsonfile:
                json.dump(json_data, jsonfile, sort_keys=True, indent=4)
                pass
    def __read_list(self):
        """
        list sample:
        Name | Class | Light | In/Out | Train/Val/Test
        2015_00001.png 1 2 1 1
        detail: https://github.com/cs-chan/Exclusively-Dark-Image-Dataset/tree/master/Groundtruth
        """
        filename = os.path.join(self._datapath, 'imageclasslist.txt')
        with open(filename) as f:
            data = f.readlines()[1:]
        trainset = []
        testset = []
        valset = []
        for idx, line in enumerate(data):
            subdata = line.strip().split()
            _data_dic = {'id': idx, 'file_name': subdata[0], 'Class': int(subdata[1]), 'Light': int(subdata[2]), 'In/Out': int(subdata[3])}
            _data_type = int(subdata[-1])
            if _data_type == 1:
                trainset.append(_data_dic)
            elif _data_type == 2:
                valset.append(_data_dic)
            else:
                testset.append(_data_dic)
        self.meta_data = {
            'train': trainset,
            'val': valset,
            'test': testset
        }
    def __get_image_annotation_pair(self, image_set, name):
        '''
        create image and object detection annotation
        annotation sample:
        CLASSNAME x y w h unused
        Motorbike 306 177 151 119 0 0 0 0 0 0 0
        '''
        images = []
        annotations = []
        for item in image_set:
            imgpath = os.path.join(self._datapath, 'Images', id2cls[item['Class']], item['file_name'])
            annotpath = os.path.join(self._datapath, 'Annotations', id2cls[item['Class']], item['file_name'] + '.txt')
            image_size = Image.open(imgpath).size
            image = {
                'id': item['id'],
                'width': image_size[0],
                'height': image_size[1],
                'file_name': item['file_name'],
                'license': 1,
                'flickr_url': '',
                'coco_url': '',
                'data_captured': '2018'
            }
            images.append(image)
            with open(annotpath) as f:
                data = f.readlines()[1:]
                for line in data:
                    subdata = line.split()
                    annotation = {
                        'id': self.__global_id,
                        'image_id': item['id'],
                        'category_id': CLASSID[subdata[0]],
                        'segmentation': [],
                        'area': int(subdata[3]) * int(subdata[4]),
                        'bbox': [int(subdata[1]), int(subdata[2]), int(subdata[3]), int(subdata[4])],
                        'iscrowd': 0
                    }
                    self.__global_id += 1
                    annotations.append(annotation)
            if SPILT:
                dirname = os.path.join(self._datapath, 'exdark', 'exdark_'+ name)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                shutil.copyfile(imgpath, os.path.join(dirname, item['file_name']))
        return images, annotations
            
    def __create_categories(self):
        for k, v in CLASSID.items():
            self.categories.append({'id': v, 'name': k, 'supercategory': k})

if __name__ == '__main__':
    ExDark('/home/yuzh/data/ExDark')