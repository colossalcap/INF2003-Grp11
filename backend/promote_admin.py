"""Quick script to promote a user to admin role."""
import sys
sys.path.insert(0, '/app')
from models.relational import SessionLocal, User

username = sys.argv[1] if len(sys.argv) > 1 else 'testuser123'

db = SessionLocal()
user = db.query(User).filter_by(username=username).first()
if user:
    user.role = 'admin'
    db.commit()
    print(f'SUCCESS: {user.username} promoted to {user.role}')
else:
    print(f'ERROR: User {username} not found')
db.close()
