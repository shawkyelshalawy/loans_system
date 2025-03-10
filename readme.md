# Loan Management System

A comprehensive Django-based loan management application that enables banks and loan providers to manage loan funds, loan requests, interest calculations, and payment schedules effectively.

## Features

- **User Roles Management:**
  - Loan Provider
  - Loan Customer
  - Bank Personnel

- **Loan Management:**
  - Users can apply for loans, which are validated against available funds.
  - Bank personnel can approve or reject loan applications and loan funds.

- **Interest Calculations**:
  - Supports sophisticated interest calculations with compound frequency.
  - Automatically calculates EMI (Equated Monthly Installment).

- **Payments & Transactions:**
  - Payments are processed transactionally to maintain data integrity.
  - Automatically generates unique reference numbers for payments.

## Installation & Setup

### Step 1: Clone the Repository
```bash
https://github.com/shawkyelshalawy/loans_system.git
cd loans_system
```

### Step 1: Set up Environment
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Environment Variables
Create a `.env` file in the root directory:
```env
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
DJANGO_LOGLEVEL=info
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=loan_db
DATABASE_USERNAME=dbuser
DATABASE_PASSWORD=dbpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Step 3: Database Setup
Make sure PostgreSQL is installed and running. Create your database and user:

```bash
CREATE DATABASE yourdbname;
CREATE USER yourdbuser WITH PASSWORD 'yourdbpassword';
ALTER ROLE yourdbuser SET client_encoding TO 'utf8';
ALTER ROLE yourdbuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE yourdbuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE yourdbname TO yourdbuser;
```

### Step 4: Django Setup
Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser
Create an admin user to access the Django admin:
```bash
python manage.py createsuperuser
```

### Step 6: Run the Application
Start your Django server:
```bash
python manage.py runserver
```

---

## API Testing (Postman)
Use Postman to verify API endpoints:

- **User Authentication:** Authenticate using provided endpoints.
- **Key Endpoints:**
  - User authentication
  - Loan Funds management
  - Loan Requests and approvals
  - Payment submissions


---

## Business Logic & Workflow

### User Roles
- **Loan Provider:** Adds funds available for loans.
- **Loan Customer:** Requests loans and makes payments.
- **Bank Personnel:** Reviews and approves/rejects loans and loan funds.

### Loan Management
- Loans must not exceed approved total loan funds.
- Interest rates and compounding frequency are set by admin in `LoanConfig`.

### Payments & Interest
- Supports multiple compounding frequencies: Monthly, Quarterly, Annually.
- EMI calculations are automatic and account for compound interest.
- Payments are processed transactionally with unique reference numbers generated automatically if omitted.

### Error Handling
- Comprehensive error handling with meaningful responses.

---

## Running the Application Locally
Start your server with:

```bash
python manage.py runserver
```

Access the application at [http://localhost:8000](http://localhost:8000).

---


