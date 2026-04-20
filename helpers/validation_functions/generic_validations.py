from marshmallow import Schema, fields, validate, ValidationError, validates

def validate_positive(value):
    if value <= 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")