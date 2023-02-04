# import asyncio

from app.models.base import BaseModel
from app.models.sybildetection1.base import SybilModel
# from app.models.briq import DATA_PATH, DATA_PATH_L2

# from app.models.indexer import Indexer
from app.models.sybildetection1 import DATA_PATH

import json


class MainController:

    @staticmethod
    def init(address):
        # indexer = Indexer()
        # asyncio.run(indexer.run())

        model = SybilModel.from_json(DATA_PATH)
        result = model.run(address)
        with open('result.json', 'w') as fout:
            json.dump(result, fout, indent=2)
        return result
