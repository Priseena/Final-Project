### Final Project User Management

## Project Set Up.

1. Fork Repositry
2. Clone Repositry
3. Alembic and Pytest:

When you run Pytest, it deletes the user table but doesn't remove the Alembic table. This can cause Alembic to get out of sync.
To resolve this, drop the Alembic table and run the migration (docker compose exec fastapi alembic upgrade head) when you want to manually test the site through http://localhost/docs.
If you change the database schema, delete the Alembic migration, the Alembic table, and the users table. Then, regenerate the migration using the command: docker compose exec fastapi alembic revision --autogenerate -m 'initial migration'.
Since there is no real user data currently, you don't need to worry about database upgrades, but Alembic is still required to install the database tables. 
4. Run the project docker compose up --build
5. pytest Docker compose exec fastapi pytest
6. Set up PGAdmin at localhost:5050
7. docker compose logs fastapi -f
8. add new feature in new branch
9. add the 10 tests 
10. add 5QA issues
11. push the changes to the Github Repositry

