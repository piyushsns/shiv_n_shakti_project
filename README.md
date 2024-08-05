# Django Project: Shiv & Shakti App

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

Shiv & Shakti App is a Django-based backend application designed to support a hybrid mobile app built with React Native. The app provides a new experience for capturing and storing memories on a cloud server, with a primary focus on weddings and events. The key features include event and wedding memory capturing, user invitations, accounting, user authentication, album creation, face recognition-based selfie detection, and photo classification.

## Features

- User authentication and registration
- Event and wedding memory capturing
- User invitations
- Album creation and management
- Face recognition-based selfie detection
- Photo classification
- Account management
- Responsive design

## Technologies Used

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Storage**: Amazon S3 (for media storage)
- **Authentication**: JWT
- **Other**: Celery (for background tasks), Redis (as Celery broker)

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Amazon S3 account
- Poetry (for dependency management)

### Backend Setup

1. **Clone the repository**:

    ```sh
    git clone https://github.com/piyushsns/shiv_n_shakti_project.git
    cd shiv_n_shakti_project
    ```

2. **Install Poetry** (if not already installed):

    ```sh
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. **Install the dependencies**:

    ```sh
    poetry install
    ```

4. **Activate the virtual environment**:

    ```sh
    poetry shell
    ```

5. **Configure the database**:

    Update the `DATABASES` settings in `shiv_shakti/settings.py` to match your PostgreSQL setup.

6. **Apply migrations**:

    ```sh
    poetry run python manage.py migrate
    ```

7. **Create a superuser**:

    ```sh
    poetry run python manage.py createsuperuser
    ```

8. **Run the development server**:

    ```sh
    poetry run python manage.py runserver
    ```

## Running the Project

To run the project in a development environment, follow these steps:

1. **Start the backend server**:

    ```sh
    poetry run python manage.py runserver
    ```

2. **Open your browser** and navigate to `http://localhost:8000`.

## Usage

1. **Register a new user** or log in with an existing account.
2. **Create events and albums** from the dashboard.
3. **Invite users** to your events.
4. **Capture and upload photos** to your albums.
5. **Use the face recognition feature** to automatically classify photos.

## API Endpoints

### Authentication

- **POST** `/api/auth/register/`: Register a new user
- **POST** `/api/auth/login/`: Log in a user
- **POST** `/api/auth/logout/`: Log out a user

### Events

- **GET** `/api/events/`: List all events
- **POST** `/api/events/`: Create a new event
- **GET** `/api/events/{id}/`: Retrieve event details
- **PUT** `/api/events/{id}/`: Update an event
- **DELETE** `/api/events/{id}/`: Delete an event

### Albums

- **GET** `/api/albums/`: List all albums
- **POST** `/api/albums/`: Create a new album
- **GET** `/api/albums/{id}/`: Retrieve album details
- **PUT** `/api/albums/{id}/`: Update an album
- **DELETE** `/api/albums/{id}/`: Delete an album

### Photos

- **GET** `/api/photos/`: List all photos
- **POST** `/api/photos/`: Upload a new photo
- **GET** `/api/photos/{id}/`: Retrieve photo details
- **PUT** `/api/photos/{id}/`: Update a photo
- **DELETE** `/api/photos/{id}/`: Delete a photo

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push your branch and create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please contact us at:

- **Email**: piyush.jain@snssystem.com
- **Website**: [www.snssystem.com](https://www.snssystem.com)
