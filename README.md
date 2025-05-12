# python-mongoDB-json-schema

An example of using mongo-jsonschema to reverse engineer a MongoDB collection

## References
* [Mongo-jsonSchema](https://pypi.org/project/mongo-jsonschema/#description)

## Tools Used

| Tool       |  Version |
|:-----------|---------:|
| Python     |   3.13.3 |
| jsonschema |   4.23.0 |
| loguru     |    0.7.3 |
| Motor      |    3.7.0 |
| Pydantic   |   2.11.3 |
| Pymongo    |   4.12.0 |
| PyODMongo  |    1.5.1 |
| VSCode     |  1.100.0 |
| PyCharm    | 2025.1.1 |

## Change History

## Change History

| Date       | Description          |
|:-----------|:---------------------|
| 2025-04    | initial creation     |
| 2025-05-02 | add requirements.txt |

## Example
In my particular case, I have a collection called products.

When setting up my ```.env``` file to point to that collection within my MongoDB Atlas URI,
this program will emit the following json:
```text
schema_dictionary:
    $schema: str = 'http://json-schema.org/schema#
    type: str = 'object'
    properties : dictionary
      _id: string
      category: string
      id_visible: integer
      image: string
      name: string
     price: integer
    required: list
      _id : str
      _category : str
      id_visible : str
      image : str
      name : str
      price: str
```

Example output:
```python
from typing import ClassVar

from pyodmongo import DbModel


class Products(DbModel):
    """Database: store, collection: Products"""
    name: str
    price: int
    category: str
    image: str
    id_visible: int
    _collection: ClassVar = 'Products'
```
