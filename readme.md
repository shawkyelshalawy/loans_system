## Step 6: Create Superuser

To manage your Django application's admin panel, create a superuser:

```bash
python manage.py createsuperuser
```

Enter your desired username, email, and password when prompted.

---

## Step 7: API Testing (Postman)

Test your API endpoints using Postman:

- **User Authentication**: Ensure you authenticate users correctly when testing API endpoints.
- **Endpoints to test:**
  - User registration and authentication
  - Loan creation, approval, and rejection
  - Payment scheduling and transaction handling

---

## Step 7: Run Tests

Run unit and integration tests using:

```bash
python manage.py test
```

Confirm that all tests pass to ensure application stability.





---

## Business Logic & Application Flow

### User Roles:
- **Loan Providers (LP)**: Offer loan funds.
- **Loan Customers (LC)**: Request and receive loans.
- **Bank Personnel (BP)**: Approve or reject loans and funds.

### Loan Handling:
- Loans are requested by customers and approved/rejected by bank personnel.
- Loans cannot exceed available approved funds from loan providers.
- Interest rates and compounding frequencies are set via `LoanConfig`.

### Interest and Payments:
- Interest calculations use monthly compounding by default.
- Payments are scheduled and handled transactionally, ensuring data integrity.
- Automatic generation of unique reference numbers for payments if not provided.

### Error Handling:
- Robust error handling ensures meaningful responses for API consumers.

---


