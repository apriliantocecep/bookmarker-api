from flask import Blueprint, jsonify, request
import validators
from src.constans.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, \
    HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from src.database import Bookmark, db
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import and_

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route('/', methods=['GET', 'POST'])
# @jwt_required()
def bookmarks_route():
    print(q)
    current_user = get_jwt_identity()

    if request.method == 'POST':
        body = request.get_json().get('body', '')
        url = request.get_json().get('url', '')

        if not validators.url(url):
            return jsonify({'error': 'enter a valid url'}), HTTP_400_BAD_REQUEST

        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'error': 'url already exists'}), HTTP_409_CONFLICT

        bookmark = Bookmark(body=body, url=url, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'body': bookmark.body,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at,
        }), HTTP_201_CREATED
    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        bookmarks_data = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)

        data = []
        for bookmark in bookmarks_data.items:
            data.append({
                'id': bookmark.id,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'body': bookmark.body,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at,
            })

        meta = {
            'page': bookmarks_data.page,
            'pages': bookmarks_data.pages,
            'total_count': bookmarks_data.total,
            'prev_page': bookmarks_data.prev_num,
            'next_page': bookmarks_data.next_num,
            'has_next': bookmarks_data.has_next,
            'has_prev': bookmarks_data.has_prev,
        }

        return jsonify({'data': data, 'meta': meta}), HTTP_200_OK


@bookmarks.get('/<int:bookmark_id>')
@jwt_required()
def get_bookmark(bookmark_id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=bookmark_id).first()

    if not bookmark:
        return jsonify({'error': 'record not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    })


@bookmarks.put('/<int:bookmark_id>')
@bookmarks.patch('/<int:bookmark_id>')
@jwt_required()
def edit_bookmark(bookmark_id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=bookmark_id).first()

    if not bookmark:
        return jsonify({'error': 'record not found'}), HTTP_404_NOT_FOUND

    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
        return jsonify({'error': 'enter a valid url'}), HTTP_400_BAD_REQUEST

    if Bookmark.query.filter(Bookmark.url != bookmark.url, Bookmark.url == url).first():
        return jsonify({'error': 'url already exists'}), HTTP_409_CONFLICT

    bookmark.url = url
    bookmark.body = body

    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_200_OK


@bookmarks.delete('<int:bookmark_id>')
@jwt_required()
def delete_bookmark(bookmark_id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=bookmark_id).first()

    if not bookmark:
        return jsonify({'error': 'record not found'}), HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT
