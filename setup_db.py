# If you have a fresh project or have deleted your database, 
# you need to run the setup_db.py script to create the database and tables.

from myapp import app, db

with app.app_context():     
    db.create_all()
    

# After running setup_db.py once and creating the database and tables, you do not need to run it again 
# unless you delete the database or make changes to the database structure (e.g., adding new tables or adding custom validators).

# bash command run: python setup_db.py