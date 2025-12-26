from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

teacher = User(
    username="teacher",
    password=generate_password_hash("teacher123"),
    role="teacher"
)

db.session.add(teacher)
db.session.commit()

print("Teacher created successfully")
