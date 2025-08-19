# Empathic Credit System Tests

This directory contains tests for the Empathic Credit System.

## Setup

To run the tests, you'll need to install pytest and its dependencies:

```bash
pip install pytest pytest-asyncio pytest-cov
```

## Running Tests

From the project root directory, run:

```bash
# Run all tests
pytest tests/

# Run a specific test file
pytest tests/services/test_credit_service.py

# Run API-specific tests
pytest tests/api/

# Run tests with verbose output
pytest tests/ -v

# Run tests matching a specific name pattern
pytest tests/ -k "test_apply_for_credit"
```

## Test Structure

- `conftest.py`: Contains shared fixtures used across multiple test files
- `services/`: Tests for service classes
  - `test_credit_service.py`: Tests for CreditService
  - `test_credit_offer_calculator.py`: Tests for CreditOfferCalculator
- `api/`: Tests for API endpoints
  - `v1/test_credit_routes.py`: Tests for credit-related endpoints

## Test Coverage

The tests cover:

1. **CreditOfferCalculator**
   - Mathematical utility functions (normalize, interpolate)
   - Credit offer calculation with different risk profiles
   - Interest rate calculations
   - Credit type determination

2. **CreditService**
   - Credit line application flow
   - Credit offer acceptance flow
   - Error handling for various edge cases:
     - Existing credit account
     - Existing credit offer
     - No active offer found
     - Offer ID mismatch
     - Expired offers

3. **API Endpoints**
   - Credit application endpoint
   - Credit offer acceptance endpoint
   - Authentication checks
   - Error handling and responses

## API Testing Approach

API tests use FastAPI's TestClient to simulate HTTP requests without starting an actual server:

1. **Dependency Mocking**: Service dependencies are overridden for unit testing endpoints
2. **Authentication**: JWT tokens are generated for authenticated endpoint testing
3. **Request-Response Cycle**: Full testing from HTTP request to response validation

## Writing New Tests

When adding new tests:

1. Use async/await for testing async functions
2. Use fixtures from conftest.py for common objects
3. Mock external dependencies as needed
4. Follow the existing pattern for test structure