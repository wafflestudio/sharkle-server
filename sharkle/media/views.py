from django.shortcuts import render
from rest_framework import status, permissions
from media.models import Image
from media.serializers import MultipleImageUploadSerializer, ImageViewSerializer

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response


class ImageUploadView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = MultipleImageUploadSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        images = serializer.save()
        image_id_list = [image.id for image in images]

        return Response(
            status=status.HTTP_201_CREATED,
            data={"message": "successful upload", "images_id": image_id_list},
        )

    def get(self, request):
        all_images = Image.objects.all()
        serializer = ImageViewSerializer(all_images, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
