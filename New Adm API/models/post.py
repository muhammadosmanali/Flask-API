from typing import List
from db import db

class PostModel(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
    post_image = db.Column(db.String(80))
    post_date = db.Column(db.String(80))
    likes = db.Column(db.Integer)
    dis_likes = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    @classmethod
    def find_by_id(cls, _id: int) -> "PostModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls, _id: int) -> List["PostModel"]:
        return cls.query.filter_by(user_id=_id).all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()