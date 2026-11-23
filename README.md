# E-Commerce Platform

A full-stack e-commerce web application designed to provide a structured online shopping experience, with customer authentication, product browsing, shopping cart, order management and payment processing.

## Project Overview

This project is being developed using a modular architecture, with a separate frontend and backend.

### Project Structure

```text
ecommerce-platform/
├── frontend/
├── backend/
├── .gitignore
└── README.md
```

## Tech Stack

### Backend
- Python
- Django
- Django REST Framework
- PostgreSQL
- SimpleJWT
- Pillow

### Frontend
- To be documented as frontend development progresses.

## Implemented Features

### Accounts Module
- Customer registration
- Email-based login using JWT authentication
- Customer profile retrieval and updates
- Address management
- JWT-based logout

## Upcoming Features

- Product and category management
- Product variants and images
- Shopping cart management
- Coupon and discount management
- Order creation and management
- Payment integration
- Shipment tracking
- Product reviews and ratings

## Getting Started

### Backend Setup

1. Clone the repository:

```bash
git clone <your-repository-url>
cd ecommerce-platform/backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure your environment variables using `.env.example`.

5. Run database migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

## Project Status

**In Development**

The initial database design and Accounts APIs have been implemented. Additional modules and frontend integration are planned.

## Author

Developed as a full-stack software development project.