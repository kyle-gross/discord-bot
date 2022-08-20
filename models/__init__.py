#!/usr/bin/env python3
import os

storage = os.getenv('TYPE_STORAGE')

if storage == 'db':
    from models.engine.db_storage import DBStorage
    storage = DBStorage()
    storage.reload()
else:
    from models.engine.file_storage import FileStorage
    storage = FileStorage()
    storage.reload()
