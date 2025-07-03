#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
db.init_app(app)
migrate = Migrate(app, db)

# ---------------------- ROUTES ----------------------

@app.route('/')
def index():
    return '<h1>Chatterbox API</h1>'

# GET /messages - List all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return make_response(jsonify([m.to_dict() for m in messages]), 200)

# POST /messages - Create new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()

    try:
        new_message = Message(
            body=data.get('body'),
            username=data.get('username')
        )
        db.session.add(new_message)
        db.session.commit()
        return make_response(jsonify(new_message.to_dict()), 201)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({"error": str(e)}), 400)

# PATCH /messages/<int:id> - Update message body
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    data = request.get_json()
    if "body" in data:
        message.body = data["body"]
        db.session.commit()

    return make_response(jsonify(message.to_dict()), 200)

# DELETE /messages/<int:id> - Delete message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    db.session.delete(message)
    db.session.commit()
    return make_response(jsonify({"message": "Message deleted"}), 200)

# ---------------------- MAIN ----------------------

if __name__ == '__main__':
    app.run(port=5000, debug=True)
