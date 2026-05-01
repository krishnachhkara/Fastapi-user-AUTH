# FastAPI Authentication System

## Features
- JWT-based authentication
- Argon2 password hashing
- Role-Based Access Control (RBAC)
- Protected routes using dependency injection
- SQLAlchemy 2.0 + PostgreSQL

## Tech Stack
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- python-jose (JWT)
- Argon2

## API Endpoints
- POST /register
- POST /login
- GET /protected
- GET /admin (RBAC)

## Security
- Password hashing (Argon2)
- Stateless JWT authentication
- Role-based authorization
