# Image Annotation Service

An Image Annotation Service that allows users to upload images, annotate them, add comments, and get a summary of comments for each image.

## Table of Contents
- [Getting Started](#getting-started)
  - [Installation](#installation)
- [Usage](#usage)
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

### Api Documentation
Open 127.0.0.1:8000/admin in your browser to access the admin interface. Use the superuser credentials created earlier.

Create Image entries and add comments to images in the admin interface.

For API documentation, visit 127.0.0.1:8000/api/schema/swagger-ui to explore available endpoints.
