import json
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.logger import operation_logger, error_logger

# Define the base class for declarative models
Base = declarative_base()

class User(Base):
    """ Represents the 'users' table in the database. """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)  # Unique identifier for each user
    username = Column(String(50), unique=True, nullable=False)  # Unique username
    password = Column(String(128), nullable=False)  # Encrypted password

class RunHistory(Base):
    """
        Represents the 'run_history' table in the database.
        Stores the history of user runs and automata state. 
    """
    __tablename__ = 'run_history'
    
    id = Column(Integer, primary_key=True)  # Unique identifier for each run
    username = Column(String(50), nullable=False)  # Username associated with the run
    automaton_json = Column(Text)  # Automaton snapshot in JSON format
    history_json = Column(Text)    # BFS run data in JSON format
    description = Column(String(200), default="")  # Optional description of the run

class DBManager:
    """
        Manages interactions with the database.
        Responsible for CreateReadUpdateDelete operations on users and run histories.
    """
    def __init__(self, db_url="sqlite:///automata.db"):
        """ Initializes the database manager. """
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)  
        self.Session = sessionmaker(bind=self.engine)  
        operation_logger.info("Database initialized.")
    
    def add_user(self, username, password):
        """ Adds a new user to the database. """
        sess = self.Session()
        existing = sess.query(User).filter_by(username=username).first()
        if existing:
            sess.close()
            error_logger.error(f"Attempt to add existing user: {username}")
            return False, "User already exists."
        user = User(username=username, password=password)
        sess.add(user)
        sess.commit()
        sess.close()
        operation_logger.info(f"User created: {username}")
        return True, "User created."
    
    def check_user_credentials(self, username, password):
        """ Checks user login credentials. """
        sess = self.Session()
        user = sess.query(User).filter_by(username=username).first()
        if not user:
            sess.close()
            error_logger.warning(f"Failed login attempt for non-existent user: {username}")
            return False
        valid = (user.password == password)
        sess.close()
        if valid:
            operation_logger.info(f"User logged in: {username}")
        else:
            error_logger.warning(f"Invalid credentials for user: {username}")
        return valid
    
    def save_run_history(self, username, automaton_data, history_data, description=""):
        """ Saves a new run history to the database. """
        sess = self.Session()
        rh = RunHistory(
            username=username,
            automaton_json=json.dumps(automaton_data),
            history_json=json.dumps(history_data),
            description=description
        )
        sess.add(rh)
        sess.commit()
        sess.close()
        operation_logger.info(f"Run history saved for user: {username}, Description: {description}")
        return True
    
    def list_run_histories(self, username):
        """ Retrieves all run histories for a specific user. """
        sess = self.Session()
        records = sess.query(RunHistory).filter_by(username=username).all()
        output = []
        for r in records:
            output.append((r.id, r.description, r.automaton_json, r.history_json))
        sess.close()
        operation_logger.info(f"Listed run histories for user: {username}")
        return output
