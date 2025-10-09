from db.session import engine
from db.base_class import Base
from models import user  # 이 임포트가 핵심!
from models import schedule

def init_db():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

if __name__ == "__main__":
    init_db()