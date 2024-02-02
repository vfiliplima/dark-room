from drf_spectacular.openapi import AutoSchema
from drf_spectacular.types import OpenApiTypes


class CustomAutoSchema(AutoSchema):
    def get_request_serializer(self):
        if self.method == "POST" and self.path.endswith("/images/"):
            return OpenApiTypes.FILE

        return super().get_request_serializer()
