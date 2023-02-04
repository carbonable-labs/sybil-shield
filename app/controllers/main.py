# import asyncio

from app.models.base import BaseModel
from app.models.briq import DATA_PATH, DATA_PATH_L2
# from app.models.starknetid import DATA_PATH, DATA_PATH_L2
# from app.models.indexer import Indexer

import json


class MainController:

    @staticmethod
    def init(address):
        # indexer = Indexer()
        # asyncio.run(indexer.run())

        model = BaseModel.from_json(DATA_PATH, DATA_PATH_L2)
        result = model.run(address)
        with open('result.json', 'w') as fout:
            json.dump(result, fout, indent=2)
        return result
