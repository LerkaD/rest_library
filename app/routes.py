from flask import Flask, request
from flask_restful import Api, Resource
from flasgger import APISpec, Swagger
from marshmallow import ValidationError
from flasgger.utils import swag_from

from constant import BOOKS_DATA, AUTHORS_DATA
from model_books import (
    get_all_books,
    init_db,
    add_book,
    get_book_by_id,
    delete_book_by_id,
    update_book_by_id,
    Book
)
from model_authors import(
    create_author_table,
    get_all_authors,
    get_author_by_id,
    get_books_by_author_id,
    delete_author_by_id,
    add_author
)

from schemas import BookSchema, AuthorSchema

from werkzeug.serving import WSGIRequestHandler

app = Flask(__name__)
api = Api(app)


class BookList(Resource):

    # @swag_from('docs/sw_books_get.yml')
    def get(self) -> tuple[list[dict], int]:
        schema = BookSchema()
        return schema.dump(get_all_books(), many=True), 200

    # @swag_from('docs/sw_books_post.yml')
    def post(self) -> tuple[dict, int]:
        data = request.json
        if isinstance(data['author'], dict):
            sch_author = AuthorSchema()
            try:
                author = sch_author.load(data['author'])
            except Exception as e:
                return f'Mistake: {e}', 400
            author = add_author(author)
            data['author'] = author.id
        schema = BookSchema(many=False)
        try:
            book = schema.load(data)
        except ValidationError as exc:
            return exc.messages, 400
        book = add_book(book)
        print(book)
        return schema.dump(book), 201


class BookInfo(Resource):
    # @swag_from('docs/books.yml')
    def get(self, id:int ) -> tuple[dict, int]:
        schema = BookSchema()
        return schema.dump(get_book_by_id(id), many=False), 200

    # @swag_from('docs/books.yml')
    def put(self, id:int)-> tuple[str, int]:
        update_data = request.json
        schema= BookSchema()
        try:
            book = schema.load(update_data)
        except ValidationError as exc:
            return exc.messages, 400
        book.id = id
        update_book_by_id(book)
        return '', 204

    # @swag_from('docs/books.yml')
    def delete(self, id:int) -> tuple[str, int]:
        try:
            get_book_by_id(id)
        except Exception:
            return f'No such id:{id}', 404
        delete_book_by_id(id)
        return '', 204


class AuthorsList(Resource):

    def get(self) -> tuple[list[dict], int]:
        schema = AuthorSchema()
        return schema.dump(get_all_authors(), many = True), 200

    def post(self):
        data = request.json
        schema = AuthorSchema()
        try:
            author = schema.load(data)
        except Exception as e:
            return f'Mistake: {e}', 400
        author = add_author(author)
        return schema.dump(author), 201



class AuthorsBooks(Resource):

    def get(self, id:int ):
        try:
            get_author_by_id(id)
        except Exception as e:
            return f'Exeption message :{e}', 400
        schema = BookSchema()
        return schema.dump(get_books_by_author_id(id), many= True), 200

    def delete(self, id):
        try:
            get_author_by_id(id)
        except Exception as e:
            return f'Exeption message :{e}', 400
        delete_author_by_id(id)
        return '', 204


swagger = Swagger(app, template_file='docs/app_swagger.json')

api.add_resource(BookList, '/api/books')
api.add_resource(BookInfo, '/api/books/<id>')

api.add_resource(AuthorsList, '/api/authors')
api.add_resource(AuthorsBooks, '/api/authors/<id>')


if __name__ == '__main__':
    create_author_table(data= AUTHORS_DATA)
    init_db(initial_records=BOOKS_DATA)
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run('0.0.0.0', debug=True)
    # app.run(debug=True)
