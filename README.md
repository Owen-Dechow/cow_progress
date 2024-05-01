# cow_progress <img src="staticfiles/media/favicon.svg" alt="cow progress icon" height=18em>
## This Program is only used seasonally it may be offline during this time

![Contributors](https://img.shields.io/github/contributors/Owen-Dechow/cow_progress)
![Forks](https://img.shields.io/github/forks/Owen-Dechow/cow_progress)
![Stars](https://img.shields.io/github/stars/Owen-Dechow/cow_progress)
![Issues](https://img.shields.io/github/issues/Owen-Dechow/cow_progress)
![License](https://img.shields.io/github/license/Owen-Dechow/cow_progress)

[Cow Progress](https://cowprogress.com), a full stack web simulation, dedicated to teaching about genetics in the dairy cattle industry. ***Simulate Holstein breeding programs, focusing on PTAs, genetic recessives and inbreeding coefficients.*** Cow Progress aims for accuracy of PTA/Trait correlations and trends. It is a classroom based system targeting group learning with every simulation belonging to a class.

The backend of Cow Progress is built using Django. Correlation/Matrix math is handled with Scypi & Numpy. XLSX files are handled using XlsxWriter. For more information see [Packages Used](#packages-used).

## Installation

1. Clone Repository
   ```bash
   git clone https://github.com/Owen-Dechow/cow_progress.git
   cd cow_progress
   ```

1. Create/Activate virtual environment
   ```bash
   python3 -m venv venv
   venv/bin/activate # MacOs/ Linux
   venv/Scripts/activate # Windows
   ```

1. Install dependencies
   ```bash
   pip install -r requirements.txt
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
   python3 manage.py migrate
   ```

1. Create super user
   ```bash
   python3 manage.py createsuperuser
   # Follow prompts from there
   ```

## Testing

```bash
python3 manage.py test --parallel --shuffle
```
`--parallel` Run tests asynchronously

`--shuffle` Run tests in random order

## Running
```bash
python3 manage.py runserver
```
Website will then be available at http://127.0.0.1:8000/

## Contributing

#### Note to Contributors
> If you are unfamiliar with *(or have never even heard of)* PTAs and/or the dairy cattle industry in general, please refrance the following [resources](#resources) for help.

#### Step by Step for Contributions
1. *(Optional)* Raise an issue on repository

1. Fork repository

1. Clone your forked repository
   ```bash
   git clone <forked-repo-url>
   ```

1. Create a branch with your changes
   ```bash
   git checkout -b <new-branch-name>
   ```

1. *Make your changes!*

1. Write tests if possible

1. Update credits if necessary

1. Open new pull request
   
   If you want to link pull request to issue, use the `closes` keyword at the top of your request.
   ```
   closes #<issue-id>
   ```

1. *Wait for pull request to be reviewed/merged*

#### Thanks to Contributors
> No matter how small (or big) your contribution is, you are greatly appreciated!
>
> ***Owen Dechow***

## Resources
* [Net merit as a measure of lifetime profit: 2021 revision](https://www.ars.usda.gov/ARSUserFiles/80420530/Publications/ARR/nmcalc-2021_ARR-NM8.pdf)
* [How To Read Holstein Sire Information](https://www.holsteinusa.com/pdf/print_material/read_sire_%20info.pdf)
* [Genetic Correlations for HOL breed](https://www.ars.usda.gov/arsuserfiles/80420530/publications/arr/nm8%20supplemental%20table_correlations_2021.txt)

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

## For More Information
* See Docs located in the `docs` directory or on [github](https://github.com/Owen-Dechow/cow_progress/tree/main/docs).

* See License.md in the root directory or on [github](https://github.com/Owen-Dechow/cow_progress/blob/main/LICENSE.md).
