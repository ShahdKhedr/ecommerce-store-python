# Mini E-commerce Store

A Python command-line mini e-commerce system that manages customers, products, carts, orders, checkout, stock, discounts, authentication, and reports.

## Project Overview

The system provides a simple shopping workflow:

1. Browse available products
2. Register or log in as a customer
3. Add products to the cart
4. Calculate the cart total
5. Checkout and create an order
6. Apply customer-level discounts
7. Update product stock
8. View and cancel customer orders
9. Manage products and orders as an admin
10. Generate sales, low-stock, and top-selling-product reports

## Main Components

### Customer Management

- Customer registration and login
- Email, phone, and password validation using Regular Expressions
- Regular and Premium customer levels
- Premium level after reaching the required order count
- Discount engine implemented using a closure and `nonlocal`
- Customer data saved and loaded from JSON

### Product Management

The project supports three product types:

- **PhysicalProduct** — includes weight and shipping calculation
- **DigitalProduct** — includes a download link
- **Service** — includes duration and provider

The `ProductManager` supports:

- Add product
- Find product
- Delete product
- Get all products
- Update stock
- Detect low-stock products
- Sort products by price
- Get product names

### Cart

The cart supports:

- Add product
- Remove product
- Update quantity
- Check product availability
- Calculate total using `reduce()`
- Clear the cart

The system checks requested quantities against available stock before checkout.

### Orders

Orders include:

- Order ID
- Customer email
- Items
- Total
- Discount
- Final total
- Order status

Supported statuses:

- Pending
- Processing
- Shipped
- Delivered
- Cancelled

Orders can be saved to and loaded from JSON.

### Reports

The admin can generate:

- Total completed orders and total sales
- Low-stock products
- Top-selling products

The reports use `filter()`, `reduce()`, `lambda`, and sorting.

### Authentication

The project provides:

- Customer registration
- Customer login
- Admin login
- Custom authentication exception handling

## Data Files

The project uses JSON files for persistent data:

- `customers.json` — stores customer information
- `products.json` — stores product information
- `orders.json` — stores orders

The included `products.json` contains the starter products used by the project. Customer and order files are initially empty and are populated when the program is used.

## Technologies

- Python
- Object-Oriented Programming (OOP)
- Inheritance
- Polymorphism
- Custom Exceptions
- Regular Expressions
- JSON
- Closures
- `nonlocal`
- `lambda`
- `map()`
- `filter()`
- `reduce()`

## Project Structure

```text
Mini-E-commerce-Store/
│
├── handed_code_edited.py
├── products.json
├── customers.json
├── orders.json
└── README.md
```

## How to Run

1. Make sure Python is installed.
2. Put the Python file and the JSON files in the same project folder.
3. Run:

```bash
python handed_code_edited.py
```

The program starts with the main menu:

```text
===== Mini E-commerce Store =====
1. Browse Products
2. Register/Login
3. View Cart/Checkout
0. Exit
```

## Example Product Codes

- `P00001` — Wireless Mouse
- `P00002` — Mechanical Keyboard
- `D00001` — Python Programming E-Book
- `D00002` — Photo Editing Software License
- `S00001` — Laptop Repair Service
- `S00002` — 1-on-1 Programming Tutoring

## Admin Account

The current code defines the default admin credentials as:

```text
Email: admin@store.com
Password: AdminPass
```

Keep these credentials only for local/demo use.

## Notes

The JSON files are used to keep data after the program closes. When the application exits normally, products, customers, and orders are saved automatically.

The project is designed as a command-line application and demonstrates several Python programming concepts through a practical e-commerce scenario.
