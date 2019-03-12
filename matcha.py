from app import current_app
from app.models import User, Tags

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Tags': Tags}