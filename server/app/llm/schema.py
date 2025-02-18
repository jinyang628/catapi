from pydantic import BaseModel, Field
from strenum import StrEnum


class Size(StrEnum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class SearchCatTool(BaseModel):
    """Search for cats based on specific criteria"""

    breed: str = Field(description="The breed of cat to search for")
    temperament: str = Field(description="The desired temperament of the cat")
    size: Size = Field(description="The size of the cat")
