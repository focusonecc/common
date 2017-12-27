# -*- encoding: utf-8 -*-

def validate_required_fields(json_data, required_fields=None):
    """
    验证必要的字段在json数据中是否存在
    """
    required_fields = required_fields or []
    for field in required_fields:
        if field not in json_data:
            return False
    return True