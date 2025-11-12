from typing import List

from pydantic import BaseModel


class RentCategoryItem(BaseModel):
    title: str
    slug: str
    url_path: str | None = None
    display_order: int


class RentCategoryGroupResponse(BaseModel):
    group_title: str
    display_order: int
    items: List[RentCategoryItem]


class RentCategoriesResponse(BaseModel):
    city: str
    groups: List[RentCategoryGroupResponse]


