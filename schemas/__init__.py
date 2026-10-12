from pydantic import BaseModel, ConfigDict


class ReadModelMixin(BaseModel):
    model_config = ConfigDict(from_attributes=True)