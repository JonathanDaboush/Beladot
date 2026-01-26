import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from sqlalchemy import delete
from backend.persistance.base import get_sessionmaker
from backend.persistance.user import User

def main():
    Session = get_sessionmaker()
    with Session() as session:
        session.execute(delete(User))
        session.commit()
    print("Cleared all users from users table.")

if __name__ == "__main__":
    main()
