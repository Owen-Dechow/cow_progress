# cowprogress
***Simulate Holstein breeding programs, focusing on PTAs, genetic recessives and inbreeding coefficients.***
<br>
[cowprogress](https://cowprogress.herokuapp.com), a full stack website dedicated to teaching about genetics in the dairy cattle industry.

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

1. Run tests
```bash
$ python3 manage.py test --parallel
```

1. ***You're all set up!***
