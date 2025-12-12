from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import (
    MappedAsDataclass,
    relationship,
    DeclarativeBase,
    Mapped,
    mapped_column,
)
from sqlalchemy import Integer, String, Text
from flask_login import UserMixin


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(MappedAsDataclass, UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    blog_posts: Mapped[list["BlogPost"]] = relationship(
        "BlogPost", back_populates="author", init=False
    )

    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="comment_author", init=False
    )


class BlogPost(MappedAsDataclass, db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = relationship("User", back_populates="blog_posts", init=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="blog_post", init=False
    )


class Comment(MappedAsDataclass, db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, init=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    comment_author: Mapped["User"] = relationship(
        "User", back_populates="comments", init=False
    )
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))

    blog_post: Mapped["BlogPost"] = relationship(
        "BlogPost", back_populates="comments", init=False
    )
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
