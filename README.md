# cow_progress <img src="https://cowprogress.herokuapp.com/static/media/favicon.0f5d3c01fb06.png" alt="cow progress icon" height=18em>

[Cow Progress](https://cowprogress.herokuapp.com), a full stack web simulation, dedicated to teaching about genetics in the dairy cattle industry. ***Simulate Holstein breeding programs, focusing on PTAs, genetic recessives and inbreeding coefficients.*** Cow Progress aims for accuracy of PTA/Trait correlations and trends. It is a classroom based system targeting group learning with every simulation belonging to a class.

The backend of Cow Progress is built using Django. Correlation/Matrix math is handled with Scypi & Numpy. XLSX files are handled using XlsxWriter. For more information see [Packages Used](#packages-used).



## Installation

1. Clone Repository
   ```bash
   $ git clone https://github.com/Owen-Dechow/cow_progress.git
   $ cd cow_progress
   ```

1. Create/Activate virtual environment
   ```bash
   $ python3 -m venv venv
   $ venv/bin/activate
   # Depending on operating system you may need to use venv/Scripts/activate 
   ```

1. Install dependencies
   ```bash
   $ pip install -r requirements.txt
   ```

1. Create .env file in the cow_progress directory
   ```bash
      .
      ├── base/
      ├── media/
      ├── cow_progress/
      ├── ├── .env.example    # copy this file into new .env file
      ├── └── .env            # new file
      └── .gitignore
      ```

1. Apply migrations
   ```bash
   $ python3 manage.py migrate
   ```

1. Create super user
   ```bash
   $ python3 manage.py createsuperuser
   # Follow prompts from there
   ```

## Testing

```bash
$ python3 manage.py test --parallel --shuffle
```
`--parallel` Run tests asynchronously

`--shuffle` Run tests in random order

## Running
```bash
$ python3 manage.py runserver
```
Website will then be available at http://127.0.0.1:8000/

## Packages Used
* [Django](https://www.djangoproject.com/)
* [django-debug-toolbar](https://django-debug-toolbar.readthedocs.io/en/latest/)
* [django-environ](https://django-environ.readthedocs.io/en/latest/)
* [django-heroku](https://github.com/heroku/django-heroku)
* [dj-database-url](https://github.com/jazzband/dj-database-url)
* [gunicorn](https://gunicorn.org/)
* [whitenoise](https://github.com/evansd/whitenoise)
* [XlsxWriter](https://github.com/jmcnamara/XlsxWriter)
* [scipy](https://scipy.org/)
* [numpy](https://numpy.org/)
* [certifi](https://github.com/certifi/python-certifi)
