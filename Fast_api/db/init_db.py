from Fast_api.db.session import engine
from Fast_api.db.base_class import Base
from Fast_api.models import user  # 이 임포트가 핵심!
from Fast_api.models import schedule

def init_db():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

if __name__ == "__main__":
    init_db()