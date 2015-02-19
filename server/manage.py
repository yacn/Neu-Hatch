from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
import os
from neuhatch import app, db
from neuhatch.models import *

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hatch@db/neuhatch'

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()


