from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime, timezone
from sqlalchemy import or_
import os

load_dotenv()
app = Flask(__name__)

#---------Configurations-----------
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.environ.get('SQLALCHEMY_MODIFICATIONS')

#----------------Initialize Flask-SQLAlchemy extension and bind it with Flask app-------
db = SQLAlchemy(app)

#----------------Database Model: Blog Post-----------------
class Post(db.Model):
    """Represent a Blog Post in the database
        Attributes:
        id(integer): Primary key,
        title(str): Post title(Max 100 characters),
        content(text): Post body content(Unlimited),
        created_at(datetime): timestamp for Post creation
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    tags = db.relationship('Tag', secondary='post_tags', backref='posts')
    created_at = db.Column(db.Date, default=datetime.now())
    updated_at = db.Column(db.Date, default=datetime.now())

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

#-----------------Post_tags(Association table)----------------------------
post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)        
)

#-----------------Create database if it doesn't exist---------------------
with app.app_context():
    db.create_all()

#------------------Routes--------------------------------------------------
@app.route('/')
def home():
    """Display default route:
      -Log onto '/' to access the default route that display "Hello default route on the browser"
    """
    return "Hello default route"

#------------------Endpoint: Create new post (POST)------------
@app.route('/post', methods=['POST'])
def create_post():
    """
    Create new post from json data
    **Endpoint**: /post
    **Request body** :
         Requires:
          -title(str): Title of the post,
          -content(text): Content body of the post
    
    **Responses**:
    201(success) : Post was created successfully,
    400(Bad Request): Invalid or missing fields in json input,
    500(server error): Database commit failed (e.g duplicate ID)
    """ 
    try:
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data or 'category' not in data:
            raise ValueError("Title, content and category are required")
        new_post = Post(title=data['title'], content=data['content'], category=data['category'])

        #assign tags
        tag_names = data.get('tags', [])
        tags = Tag.query.filter(Tag.name.in_(tag_names)).all()
        new_post.tags=tags
        db.session.add(new_post)
        db.session.commit()

#-------Return success response with 201 HTTP status code-----------------------
        return jsonify({
            "status": "success",
            "message": "New post created and saved to the database successfully"
        }), 201

#-------Return error responses with 400 error code to handle Bad Request errors(Invalid/Missing fields)------
    except ValueError as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400
    
#-------Return error responses with 500 error to handle server error---------------------
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": str(e)#"Unexpected error occurred"
        }), 500
    
#-------Endpoint: Retrieve all the posts--------------------------- 
@app.route('/posts', methods=['GET'])
def get_posts():
    """
    **Endpoint**: GET /posts
    **Get posts**:
       -Query all the posts.
       -List all the posts with their id, title, content and date created.

    **Responses**:
       -200(ok) HTTP code indicating that retrieving posts was ok
           -id(integer): Unique identifier
           -title(str): Title of the post
           -content(text): Body of the posts
           -date_created(Date): Date the posts was created
       -500(server error) error code of an internal error
    
    **Example**:
    ```
    json
    {
    "status": "success",
    "message": "Posts retrieved successfully",
    posts:[
      {
       "id": 1,
       "title": "My first title",
       "content" : "This is my content",
       "date" : 29 April 2025
    }]
    }
    ```
    """
    try:
        search = request.args.get('search')
        if search:
            posts = Post.query.filter(
                or_(
                    Post.title.ilike(f"%{search}%"),
                    Post.content.ilike(f"%{search}%"),
                    Post.category.ilike(f"%{search}%")
                )
                ).all()
        else:
            #Retrieve all the posts from the database
            posts = Post.query.all()

            #Serialize posts into list of python dictionaries
        posts_list=[]
        for post in posts:
            posts_list.append(
            {
                "id": post.id, 
                 "title": post.title, 
                "content": post.content, 
                 "category": post.category,
                "tags":  [tag.name for tag in post.tags],
                "date": post.created_at
                }) 

        return jsonify({
            "status": "success",
            "message": "Posts retrieved successfully",
            "posts_list": posts_list
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)#"Unexpected error occurred"
        }), 500
    
#----------Endpoint /posts/id --------------------
@app.route('/posts/<int:id>', methods=['GET'])
def get_post(id):
    """
    **Endpoint**: GET post by its id
    **GET a post**:
       -Query post by id to get one

    **Serialize post**:
       -Serialize post into dictionaries

    **Responses**:
       -200(ok):
           -id(int): Unique identifier
           -title(str): title of the post
           -content(text): body of the post
           -created_at(date): Date post was created
       -500(server): Internal database error
    """
    
    try:
        #Retrieve a post by id
        post = Post.query.get_or_404(id)

        #Serialize post_item into python dictionaries
        post_item = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "category": post.category,
            "tags": [tag.name for tag in post.tags],
            "date": post.created_at
        }
        #Return a deserialized post_item with success status and a message
        return jsonify({
            "status": "success",
            "message": f"Post:{id} Retrieved Sucessfully",
            "post_item": post_item
        }), 200
    
    #Catch Internal errors that may occur in the database
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Unexpected error occurred"
        }), 500
        
#-----------Endpoint Update a post-----------------------
@app.route('/post/update/<int:id>', methods=['PUT'])
def update_post(id):
    """
    **Endpoint**: PUT /post/update/<int:id>
    **Get a single post by id**
         -name.title
         -name.content
      -Stage changes made(db.session.commit())
    **Responses**:
         -200(ok): 
             -status : success
             -message: Update successful
         -400(Bad request):
             -status: error
             -error: str(e)
      -Stage changes(db.session.commit())
         -500(Server error):
             -status: error
             -error: Unexpected error occurred
    """
    try:
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            raise ValueError("Title and content are required")
        
        #Get a single post by id
        post = Post.query.get_or_404(id)
        post.title = data['title']
        post.content = data['content']
        db.session.commit()
        
        #Return responses in json format
        return jsonify({
            "status": "success",
            "message": f"Post: {id} updated successfully"
        }), 200
    
    #Catch valueErrors that may have occurred
    except ValueError as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 400
    
    #Catch internal server errors
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": "Unexpected error occurred"
        }), 500


@app.route('/post/delete/<int:id>', methods=['DELETE'])
def delete_post(id):
    """
    **Endpoint** DELETE /post/delete/id
    **Get a single post**
     -delete post by id
     -Stage changes that may have occurred

    **Responses**
    -Return responses in json format
        -200(ok):
           -status : success
           -message: Post: {id} was deleted successfully
        -500(Internal server error):
           -status: error
           -error: Unexpected error occurred
    """
    try:
        post = Post.query.get_or_404(id)
        db.session.delete(post)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Post: {id} was deleted successfully"
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "error": "Unexpected error occurred"
        }), 500


if __name__ == '__main__':
    app.run(debug=True)