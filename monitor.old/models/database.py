import asyncio

from tortoise import Tortoise


async def DBinit():
    # Here we connect to a SQLite DB file.
    # also specify the app name of "models"
    # which contain models from "app.models"
    await Tortoise.init(
        db_url='mysql://root:xxxx@127.0.0.1:3306/subtest',
        modules={'models': ['models']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()


# if __name__ == '__main__':
#     asyncio.run(DBinit())
