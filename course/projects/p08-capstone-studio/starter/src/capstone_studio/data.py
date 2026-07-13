from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, TypeAdapter


def load_model[ModelT: BaseModel](path: str | Path, model: type[ModelT]) -> ModelT:
    return model.model_validate_json(Path(path).read_text())


def load_model_list[ModelT: BaseModel](
    path: str | Path, model: type[ModelT]
) -> list[ModelT]:
    return TypeAdapter(list[model]).validate_json(  # type: ignore[valid-type]
        Path(path).read_text()
    )
