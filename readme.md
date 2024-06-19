# API Django Rest Framework con Websockets

## Prerequisitos

- [Python 3.11](https://www.python.org/downloads/release/python-3119/), puedes verificar tu versión ejecutando el
  comando `python --version`.
- Puerto 8080 (Django) disponibles.

## Instalación

1. crear un ambiente virtual, usando el comando:
    ```bash
        python -m venv env
    ```

2. Copiar el archivo .env.example y renombrarlo a .env, luego configurar las variables de entorno:
    ```bash
        touch .env.example .env # Usar powershell y no CMD en el caso de Windows
    ```
   Luego configurar las variables de entorno en el archivo .env, como las credenciales de la mongoDB y la ApiKey de
   OpenAI.

   **Nota**: El secreto de DJANGO funciona tal como está, pero debe ser cambiado para ambientes productivos.

3. activar el ambiente virtual utilizando:
    ```bash
        env\Scripts\activate # En Windows
        source env/bin/activate # En Linux o MacOS
    ```

4. instalar las dependencias del proyecto con:
    ```
        pip install -r requirements.txt
    ```

6. levantar el servidor:
    ```
        python manage.py runserver
    ```

7. La aplicación estará disponible en [http://localhost:8080](http://localhost:8080)