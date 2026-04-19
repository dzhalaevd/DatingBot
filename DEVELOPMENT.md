# :building_construction: Development Instructions

## :books: Table of Contents

- [Installation](#construction_worker-getting-started)
    - [With docker](#construction-with-docker)
    - [Manually](#wheelchair-manually)
        - [requirements](#with-requirements)
        - [poetry](#with-poetry)
  - [Localization](#globe_with_meridians-i18n)
- [Tests](#test_tube-tests)

## :construction_worker: Getting Started

### :construction: With docker

First, rename the file `.env.dist` to `.env`.\
Afterward, fill it with the required data.

| Variable          | Type | Importance | Description                                                                             |
|-------------------|------|------------|-----------------------------------------------------------------------------------------|
| BOT_TOKEN         | str  | True       | Bot token                                                                               |
| ADMINS            | list | True       | list of admins id                                                                       |
| SUPPORTS          | list | True       | list of supports id                                                                     |
| IP                | str  | True       | ip for other services                                                                   |
| TIMEZONE          | str  | True       | your time zone for working with the scheduler                                           |
| MODERATE_CHAT     | str  | True       | telegram chat where the event will be moderated                                         |
| POSTGRES_USER     | str  | True       | username of the database owner                                                          |
| POSTGRES_PASSWORD | str  | True       | password from the database                                                              |
| DB_HOST           | str  | True       | IP address of the database (Name of the service in the docker-compose.yml (User `db`)). |
| DB_PORT           | str  | True       | the database port. Usually the db running on port `5432`                                |
| POSTGRES_DB       | str  | True       | database name                                                                           |
| SECRET_KEY        | str  | True       | secret key for django                                                                   |
| API_KEY           | str  | True       | yandex api key for yandex map                                                           |
| QIWI_KEY          | str  | True       | qiwi api key for receiving payments                                                     |
| PHONE_NUMBER      | str  | True       | your phone number (need for qiwi)                                                       |
| SECRET_P2         | str  | True       | public p2 key which allows you to issue an invoice and open a transfer form             |
| USE_REDIS         | bool | False      | Optional parameter                                                                      |

Once done, run the following command:

```shell
$ docker-compose build
```

### :wheelchair: Manually

If you prefer not to use Docker, you can manually build the app.
Before installing the DatingBot project, ensure Python is installed:

```sh
$ python -V
```

If Python is installed, clone the DatingBot repository:

```sh
$ git clone https://github.com/DavidRomanovizc/DatingBot.git
```

Create a virtual environment:

```sh
$ python -m venv venv
```

Activate the virtual environment:

<u>On Windows:</u>

```sh
$ venv\Scripts\activate
```

<u>On macOS and Linux:</u>

```sh
$ source venv/bin/activate
```

#### with requirements

```shell
$ pip install -r requirements.txt
```

#### with poetry

After setting up the virtual environment, install Poetry with pip:

```shell
$ pip install poetry
```

Then install Poetry dependencies:

```shell
poetry install
```

## :rocket: Usage

Follow the same steps as described in the Docker section for setting up the .env file. But use `localhost` for `DB_HOST`

### :green_book: Django

To create a `SECRET_KEY`, use this site - [generate secret keys](https://djecrety.ir/)
and paste it into the `.env` file

```dotenv
SECRET_KEY=jjv@^0qv^=aydunfjo$qpd_66j+)egm1#-c1iwt%mtjinm)ftj
```

Run the following commands to set up the Django application:
```sh
$ python django_app.py makemigrations
$ python django_app.py migrate
$ python django_app.py createsuperuser
$ python django_app.py makemigrations usersmanage 
$ python django_app.py migrate usersmanage
$ python django_app.py runserver
```

## :globe_with_meridians: i18n

### Title - dating

#### Launching for the first time

1. Extract texts from files (he finds it himself)
   ```sh
   $ pybabel extract -F babel.cfg -o locales/dating.pot .
   ```
2. Create a folder for English translation
   ```sh
   $ pybabel init -i locales/dating.pot -d locales -D dating -l en
   ```
3. For Russian translation
   ```sh
   $ pybabel init -i locales/dating.pot -d locales -D dating -l ru
   ```
4. Translate and compile
   ```sh
   $ pybabel compile -d locales -D dating
   ```

#### Updating translations

1. Extract texts from files, add text to translated versions
   ```sh
   $ pybabel extract -F babel.cfg -o locales/dating.pot .
   $ pybabel update -d locales -D dating -i locales/dating.pot
   ```
2. Manually translate, then compile
   ```sh
   $ pybabel compile -d locales -D dating
   ```

## :test_tube: Tests