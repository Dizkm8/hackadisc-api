# API Django Rest Framework con Websockets

## Prerequisitos

- [Python 3.11](https://www.python.org/downloads/release/python-3119/), puedes verificar tu versión ejecutando el
  comando `python --version`.
- Puerto 8000 (Django) 5432 (PostgreSQL) y 6000 (Postgre de prueba) disponibles.

## Instalación

1. Crear un ambiente virtual, usando el comando:
    ```bash
        python -m venv venv
    ```

2. Copiar el archivo .env.template y renombrarlo a .env, luego configurar las variables de entorno:
    ```bash
        touch .env.template .env # Usar powershell y no CMD en el caso de Windows
    ```
   **Nota**: La explicación de las variables de entero está en la sección de [variables de entorno](#variables-de-entorno)

3. Activar el ambiente virtual utilizando:
    ```bash
        env\Scripts\activate # En Windows
        source env/bin/activate # En Linux o MacOS
    ```

4. Instalar las dependencias del proyecto con:
    ```
        pip install -r requirements.txt
    ```

6. Levantar el servidor:
    ```
        python manage.py runserver
    ```

7. La aplicación estará disponible en [http://localhost:8000](http://localhost:8000)

## Variables de entorno

```bash
DJANGO_SECRET_KEY= #Secreto de Django, utilizado también por JWT

POSTGRESQL_DB_HOST  #Host, por defecto localhost o 127.0.0.1
POSTGRESQL_DB_PORT  #Puerto, PostgreSQL suele correr en el 5432
POSTGRESQL_DB_NAME  #Nombre de la DB, en el docker-compose se usa "myuser"
POSTGRESQL_DB_USER #Nombre de la DB, en el docker-compose se usa "myuser"
POSTGRESQL_DB_PASSWD #Nombre de la DB, en el docker-compose se usa "myuser"

FIREBASE_PROJECT_ID # ID del Proyecto de Firebase según las credenciales de Admin SDK
FIREBASE_PRIVATE_KEY  # Clave privada del proyecto de Firebase
FIREBASE_CLIENT_EMAIL # Email del cliente del proyecto de Firebase

OPENAI_API_KEY # Apikey de openAI
OPENAI_GPT_MODEL #Modelo de OpenAI, debe ser un nombre según la documentación https://platform.openai.com/docs/models
# Y además estar alineada con la Api Key (si la cuenta no está subscrita a GPT-4, tampoco podrá usar su API).

SENDER_MAIL # Correo electrónico del usuario de gmail
SENDER_MAIL_PWD  # Contraseña del usuario de gmail
SENDER_NAME # Nombre del usuario que enviará el correo, puede ser ficticio
TEST_MAIL # Correo electrónico para enviar notificaciones de prueba
# Util para evitar enviar correos a usuarios reales en ambientes productivos.
```