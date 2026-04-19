from pydantic import (
    BaseModel,
    ConfigDict,
)


class RoleBase(BaseModel):
    title: str


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    title: str | None = None


class RoleResponse(RoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
