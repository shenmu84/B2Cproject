from django.urls import converters
class UsernameConverter(converters.StringConverter):
    regex='[a-zA-Z0-9_-]{5,20}'
    def to_python(self,value):
        return value