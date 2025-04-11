from marshmallow import Schema, fields, validates, ValidationError, post_load

from model_books import get_book_by_title, Book
from model_authors import get_author_by_id, Author


class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    author = fields.Int(required=True)

    @validates('title')
    def validate_title(self, title: str) -> None:
        if get_book_by_title(title) is not None:
            raise ValidationError(
                'Book with title "{title}" already exists, '
                'please use a different title.'.format(title=title)
            )

    @validates('author')
    def validate_author(self, author_id: int) -> None:
        try:
            get_author_by_id(author_id)
        except Exception:
            raise ValidationError(
                'No author with id = {id}'.format(id=author_id)
            )

    @post_load
    def create_book(self, data: dict, **kwargs) -> Book:
        return Book(**data)

class AuthorSchema(Schema):
    id = fields.Int(dump_only= True)
    first_name = fields.Str(required= True)
    last_name = fields.Str(required= True)
    middle_name = fields.Str(allow_none= True)


    @post_load
    def create_author(self, data: dict, **kwargs) -> Author:
        return Author(**data)