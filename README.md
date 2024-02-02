Image Annotation Service

An Image Annotation Service that allows users to upload images, annotate them, add comments, and get a summary of comments for each image.

## Table of Contents
- [Getting Started](#getting-started)
  - [Installation](#installation)
- [Usage](#usage)
- [Accessing the Admin Interface](#accessing-the-admin-interface)
- [API Documentation](#api-documentation)

  
## Getting Started

### Instalation

1. To get started, clone the repository using the following command:

```bash
git clone https://github.com/vfiliplima/dark-room.git
cd image-annotation-service
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate
```

3. Install the project dependencies:

```bash
pip install -r requirements.txt
```

### Usage

Navigate to the project root where the manage.py file is located:

```bash
cd path/to/image_annotation_service
```

Apply database migrations:

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

Create a superuser for admin access:

```bash
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

### Accessing the Admin Interface

1. Open [127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) in your browser.

2. Log in using the superuser credentials created during the setup.

3. In the admin interface, create Image entries and add comments to the images.


### API Documentation

For detailed API documentation, follow these steps:

1. Visit [127.0.0.1:8000/api/schema/swagger-ui](http://127.0.0.1:8000/api/schema/swagger-ui) in your browser.

2. The Swagger UI page will display available endpoints, request and response formats, and other relevant information.

3. Explore the API to understand and interact with the provided functionalities.
