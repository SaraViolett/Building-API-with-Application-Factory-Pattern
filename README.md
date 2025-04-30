# Coding Temple - Backend Specialization Module 1 Assignment: Building API with Application Factory Pattern

## Overview

This project is a Flask-based API for managing a mechanics shop. It is built using the application factory pattern and includes functionality for managing customers, mechanics, parts, services, and service tickets. The API is structured using Flask blueprints for modularity and scalability.

## Features

- **Customers Management**:
  - Create, read, update, and delete customer records.
  - Endpoints:
    - `POST /customers/login`: Customer login.
    - `POST /customers`: Create a new customer.
    - `GET /customers`: Retrieve all customers.
    - `GET /customers/paginated`: Retrieve all customers paginated.
    - `GET /customers/search`: Retrieve customers by searching name.
    - `GET /customers/<customer_id>`: Retrieve a single customer by ID.
    - `GET /customers/my-tickets`: Retrieve all tickets for customer.
      - Customer login token is required for this route
    - `PUT /customers`: Update a customer's details.
      - Customer login token is required for this route
    - `DELETE /customers`: Delete a customer.
      - Customer login token is required for this route

- **Mechanics Management**:
  - Create, read, update, and delete mechanic records.
  - Endpoints:
    - `POST /mechanics/login`: Mechanics login.
    - `POST /mechanics`: Create a new mechanic.
    - `GET /mechanics`: Retrieve all mechanics.
    - `GET /mechanics/<mechanic_id>`: Retrieve a single mechanic by ID.
    - `GET /mechanics/activity-tracker`: Retrieve all mechanics and sort in desending order by those assigned to the most tickets.
    - `GET /mechanics/search`: Retrieve mechanics by searching name.
    - `GET /mechanics/paginated`: Retrieve all mechanics paginated.
    - `PUT /mechanics`: Update a mechanic's details.
      - token reguired from mechanic login
    - `DELETE /mechanics/<mechanic_id>`: Delete a mechanic.
      - token reguired from mechanic login

- **Service Tickets Management**:
  - Create, read, update, and delete service tickets.
  - Assign or remove mechanics, parts, and services from tickets.
  - Endpoints:
    - `POST /service-tickets`: Create a new service ticket.
    - `GET /service-tickets`: Retrieve all service tickets.
    - `GET /service-tickets/<ticket_id>`: Retrieve a single service ticket by ID.
    - `GET /service-tickets/receipt/<ticket_id>`: Retrieve a single service ticket by ID with total costs for parts, service labor, and ticket total.
    - `PUT /service-tickets/<ticket_id>`: Update a service ticket.
    - `PUT /service-tickets/<ticket_id>/add-mechanic/<mechanic_id>`: Assign a mechanic to a ticket.
    - `PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>`: Remove a mechanic from a ticket.
    - `PUT /service-tickets/<ticket_id>/add-part/<part_id>`: Assign a part to a ticket.
    - `PUT /service-tickets/<ticket_id>/remove-part/<part_id>`: Remove a part from a ticket.
    - `PUT /service-tickets/<ticket_id>/add-service/<service_id>`: Assign a service to a ticket.
    - `PUT /service-tickets/<ticket_id>/remove-service/<service_id>`: Remove a service from a ticket.
    - `DELETE /service-tickets/<ticket_id>`: Delete a service ticket.

- **Parts Management**:
  - Manage part description for the shop.
  - Endpoints:
    - `POST /part_description`: Add a new part to the inventory.
    - `GET /part_description`: Retrieve all parts in the inventory.
    - `GET /part_description/<part_id>`: Retrieve details of a specific part by ID.
    - `PUT /part_description/<part_id>`: Update details of a specific part.
    - `DELETE /part_description/<part_id>`: Delete a part from the inventory.

  - **Serialized Part Management**:
  - Manage part inventory for the shop.
  - Endpoints:
    - `POST /serialized-parts`: Create serialized part.
    - `GET /serialized-parts`: Retrieve all serialized parts.
    - `GET /serialized-parts/<part_id>`: Retrieve details of a specific serialized part by ID.
    - `PUT /serialized-parts/<part_id>`: Update details of a specific serialized part.
    - `DELETE /serialized-parts/<part_id>`: Delete a serialized part from the inventory.

- **Services Management**:
  - Manage services offered by the shop.
  - Endpoints:
    - `POST /services`: Add a new service to the catalog.
    - `GET /services`: Retrieve all available services.
    - `GET /services/<service_id>`: Retrieve details of a specific service by ID.
    - `PUT /services/<service_id>`: Update details of a specific service.
    - `DELETE /services/<service_id>`: Delete a service from the catalog.
