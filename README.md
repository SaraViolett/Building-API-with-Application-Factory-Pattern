# Coding Temple - Backend Specialization Module 1 Assignment: Building API with Application Factory Pattern

## Overview

This project is a Flask-based API for managing a mechanics shop. It is built using the application factory pattern and includes functionality for managing customers, mechanics, and service tickets. The API is structured using Flask blueprints for modularity and scalability.

## Features

- **Customers Management**:
  - Create, read, update, and delete customer records.
  - Endpoints:
    - `POST /customers`: Create a new customer.
    - `GET /customers`: Retrieve all customers.
    - `GET /customers/<customer_id>`: Retrieve a single customer by ID.
    - `PUT /customers/<customer_id>`: Update a customer's details.
    - `DELETE /customers/<customer_id>`: Delete a customer.

- **Mechanics Management**:
  - Create, read, update, and delete mechanic records.
  - Endpoints:
    - `POST /mechanics`: Create a new mechanic.
    - `GET /mechanics`: Retrieve all mechanics.
    - `GET /mechanics/<mechanic_id>`: Retrieve a single mechanic by ID.
    - `PUT /mechanics/<mechanic_id>`: Update a mechanic's details.
    - `DELETE /mechanics/<mechanic_id>`: Delete a mechanic.

- **Service Tickets Management**:
  - Create, read, update, and delete service tickets.
  - Assign or remove mechanics from tickets.
  - Endpoints:
    - `POST /service-tickets`: Create a new service ticket.
    - `GET /service-tickets`: Retrieve all service tickets.
    - `GET /service-tickets/<ticket_id>`: Retrieve a single service ticket by ID.
    - `PUT /service-tickets/<ticket_id>`: Update a service ticket.
    - `PUT /service-tickets/<ticket_id>/add-mechanic/<mechanic_id>`: Assign a mechanic to a ticket.
    - `PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>`: Remove a mechanic from a ticket.
    - `DELETE /service-tickets/<ticket_id>`: Delete a service ticket.
