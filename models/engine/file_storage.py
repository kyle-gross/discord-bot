#!/usr/bin/env python3
import json


class FileStorage:
    __file_path = 'storage.json'
    __objects = {}

    def all(self, cls=None) -> dict:
        """Returns dict of models currently in storage"""
        if cls:
            dict = {}
            for k in self.__objects.keys():
                if cls.__name__ in k:
                    dict[k] = self.__objects[k]
            return dict
        else:
            return FileStorage.__objects

    def new(self, obj):
        """Adds a new object to storage dictionary"""
        new = type(obj).__name__ + '.' + obj.id
        FileStorage.__objects[new] = obj
        # self.all().update(obj.to_dict())

    def save(self):
        """Saves storage dict to file"""
        with open(FileStorage.__file_path, 'w') as f:
            temp = {k: v.to_dict() for k, v in FileStorage.__objects.items()}
            # for k, v in FileStorage.__objects.items():
            #     temp[k] = v.to_dict()
            json.dump(temp, f)

    def delete(self, obj=None):
        """Deletes obj from __objects"""
        if obj == None:
            return
        for k in FileStorage.__objects.keys():
            if obj.id in k:
                del FileStorage.__objects[k]
                return

    def close(self):
        """Deserialize JSON file to objects"""
        self.reload()
    
    def reload(self):
        """Loads storage dict from file"""
        from models.artifact import Artifact
        from models.base import BaseModel
        from models.def_call import DefCall
        from models.guild import Guild

        classes = {
            'BaseModel': BaseModel, 'Guild': Guild, 'Artifact': Artifact, 'DefCall': DefCall
        }
        try:
            temp = {}
            with open(FileStorage.__file_path) as f:
                temp = json.load(f)
            for k, v in temp.items():
                new_obj_type = k.split('.')[0]
                new_obj = classes[new_obj_type]
                FileStorage.__objects[k] = new_obj(**v)
        except FileNotFoundError:
            pass
