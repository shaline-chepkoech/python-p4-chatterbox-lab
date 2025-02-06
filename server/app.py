from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Retrieve all messages from the database and order them by created_at in ascending order
        messos = Message.query.order_by(Message.created_at).all()
        all_messages = [mess.to_dict() for mess in messos]
        return jsonify(all_messages), 200

    elif request.method == 'POST':
        # Create a new message from request JSON data
        data = request.get_json()

        new_mess = Message(
            body=data.get('body'),
            username=data.get('username')
        )
        db.session.add(new_mess)
        db.session.commit()

        return jsonify(new_mess.to_dict()), 201

@app.route('/messages/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def messages_by_id(id):
    mess = Message.query.get(id)

    if not mess:
        return jsonify({'error': 'Message not found'}), 404

    if request.method == 'PATCH':
        # Update the message's body using the request JSON body
        data = request.get_json()
        new_body = data.get('body')
        if new_body:
            mess.body = new_body
            db.session.commit()
            return jsonify(mess.to_dict()), 200
        return jsonify({'error': 'No body provided to update'}), 400

    elif request.method == 'DELETE':
        # Delete the message from the database
        db.session.delete(mess)
        db.session.commit()
        return jsonify({'message': 'Message deleted'}), 204

    # Default to GET if no method matches (e.g. retrieving message by ID)
    return jsonify(mess.to_dict()), 200

if __name__ == '__main__':
    app.run(port=5555)