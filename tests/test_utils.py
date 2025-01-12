import pytest
from fastapi.utils import (
    is_body_allowed_for_status_code,
    create_model_field,
    create_cloned_field,
    deep_dict_update,
)
from fastapi._compat import BaseConfig, Undefined, ModelField, PYDANTIC_V2
from pydantic.fields import FieldInfo
from pydantic import BaseModel, create_model


def test_is_body_allowed_for_status_code():
    # Test cases where body is allowed
    assert is_body_allowed_for_status_code(None) is True
    assert is_body_allowed_for_status_code("default") is True
    assert is_body_allowed_for_status_code("2XX") is True
    assert is_body_allowed_for_status_code(200) is True
    assert is_body_allowed_for_status_code(201) is True

    # Test cases where body is not allowed
    assert is_body_allowed_for_status_code(204) is False
    assert is_body_allowed_for_status_code(205) is False
    assert is_body_allowed_for_status_code(304) is False
    assert is_body_allowed_for_status_code(100) is False

    # Test invalid input
    with pytest.raises(ValueError):
        is_body_allowed_for_status_code("invalid")


def test_deep_dict_update():
    main_dict = {"a": {"b": 1}, "c": [1, 2], "d": 4}
    update_dict = {"a": {"b": 2, "e": 3}, "c": [3, 4], "f": 5}
    deep_dict_update(main_dict, update_dict)
    assert main_dict == {"a": {"b": 2, "e": 3}, "c": [1, 2, 3, 4], "d": 4, "f": 5}

    # Test with non-dict values
    main_dict = {"a": 1}
    update_dict = {"a": {"b": 2}}
    deep_dict_update(main_dict, update_dict)
    assert main_dict == {"a": {"b": 2}}

    # Test with empty update_dict
    main_dict = {"a": {"b": 1}}
    update_dict = {}
    deep_dict_update(main_dict, update_dict)
    assert main_dict == {"a": {"b": 1}}


def test_create_model_field():
    if PYDANTIC_V2:
        field = create_model_field(
            name="test_field",
            type_=str,
            default="default_value",
            required=True,
            field_info=FieldInfo(annotation=str, default="default_value"),
        )
        assert field.field_info.default == "default_value"
        assert field.field_info.annotation == str
    else:
        field = create_model_field(
            name="test_field",
            type_=str,
            default="default_value",
            required=True,
            model_config=BaseConfig,
            field_info=FieldInfo(),
        )
        assert field.required is True

    assert field.name == "test_field"
    assert field.default == "default_value"


def test_create_cloned_field():
    class TestModel(BaseModel):
        field1: int
        field2: str

    if PYDANTIC_V2:
        original_field = create_model_field(
            name="test_field",
            type_=TestModel,
            field_info=FieldInfo(annotation=TestModel),
        )
    else:
        original_field = create_model_field(
            name="test_field",
            type_=TestModel,
            model_config=BaseConfig,
            field_info=FieldInfo(),
        )

    cloned_field = create_cloned_field(original_field)
    assert cloned_field.name == original_field.name
    assert cloned_field.field_info.annotation == original_field.field_info.annotation
