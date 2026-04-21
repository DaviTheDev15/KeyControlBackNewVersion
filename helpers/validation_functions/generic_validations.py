from marshmallow import Schema, fields, validate, ValidationError, validates
from flask_restful import fields as flaskFields

def validate_positive(value):
    if value <= 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")
    
class DateFormat(flaskFields.Raw):
    def format(self, value):
        return value.isoformat() if value else None
    
class TimeFormat(flaskFields.Raw):
    def format(self, value):
        return value.strftime("%H:%M") if value else None

class DiasReservaField(flaskFields.Raw):
    def format(self, value):
        return [d.dia_semana for d in value] 