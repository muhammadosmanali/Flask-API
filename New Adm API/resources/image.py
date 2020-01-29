from flask_restful import Resource
from flask_uploads import UploadNotAllowed
from flask import request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback
import os

from libs import image_helper
from libs.strings import gettext
from libs import ml_model
from schemas.image import ImageSchema

image_schema = ImageSchema()


class ImageUpload(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        """
        This endpoint is used to upload an image file. It uses the
        JWT to retrieve user information and save the image in the user's folder.
        If a file with the same name exists in the user's folder, name conflicts
        will be automatically resolved by appending a underscore and a smallest
        unused integer. (eg. filename.png to filename_1.png).
        """
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        folder = f"user_{user_id}/Prediction"
        try:
            # save(self, storage, folder=None, name=None)
            image_helper.save_image(data["image"], folder=folder)
            run = ml_model.MLModel.predict(data["image"])
            prediction = ""
            for x in range(1, len(run[0]) + 1):
                prediction = prediction + " Prediction # " + str(x) + ": " + run[1][x-1] + " " + str(run[0][x-1]) + ","
            # here we only return the basename of the image and hide the internal folder structure from our user
            # basename = image_helper.get_basename(image_path)
            return {"message": "{}".format(prediction)}, 201
        except UploadNotAllowed:  # forbidden file type
            extension = image_helper.get_extension(data["image"])
            return {"message": gettext("image_illegal_extension").format(extension)}, 400
    



class Image(Resource):
    @classmethod
    @jwt_required
    def get(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}/Prediction"
        if not image_helper.is_filename_safe(filename):
            return {"message": gettext("image_illegal_file_name").format(filename)}, 400
        
        try:
            return send_file(image_helper.get_path(filename, folder=folder))
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404 


    @classmethod
    @jwt_required
    def delete(cls, filename: str):
        user_id = get_jwt_identity()
        folder = f"user_{user_id}"

        if not image_helper.is_filename_safe(filename):
            return {"message": gettext("image_illegal_file_name").format(filename)}, 400
        
        try:
            os.remove(image_helper.get_path(filename, folder=folder))
            return {"message": gettext("image_deleted").format(filename)}
        except FileNotFoundError:
            return {"message": gettext("image_not_found").format(filename)}, 404
        except:
             traceback.print_exc()
             return {"message": gettext("image_deleted_failed")}, 
             


class AvatarUpload(Resource):
    @classmethod
    @jwt_required
    def put(cls):
        data = image_schema.load(request.files)
        user_id = get_jwt_identity()
        filename = f"user_{user_id}"
        folder = "avatars"
        avatar_path = image_helper.find_image_any_format(filename, folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                return {"message": gettext("avatar_delete_failed")}, 500

        try:
            ext = image_helper.get_extension(data["image"].filename)
            avatar = filename + ext
            avatar_path = image_helper.save_image(
                data["image"], folder=folder, name=avatar
            )
            basename = image_helper.get_basename(avatar_path)
            return {"message": gettext("avatar_uploaded").format(basename)}, 200
        except UploadNotAllowed:
            extension = image_helper.get_extension(data["image"])
            return {"message": gettext("image_illegal_extension").format(extension)}, 400


class Avatar(Resource):
    @classmethod
    @jwt_required
    def get(cls, user_id: int):
        folder = "avatars"
        filename = f"user_{user_id}"
        avatar = image_helper.find_image_any_format(filename, folder)
        if avatar:
            return send_file(avatar)
        return {"message": gettext("avatar_not_found")}, 404