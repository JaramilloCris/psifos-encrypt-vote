# psifos-encrypt-vote

## Config
Los siguientes campos se encuentran en el archivo config

| Variable | Descripción |
|----------|----------|
| ELECTION_NAME    | Nombre de la elección   |
| ELECTION_UUID   | UUID de la elección  |
| QUESTIONS    | Arreglo de diccionarios, cada uno de estos corresponde a una pregunta teniendo el campo min, max y total_answers  |
| ANSWERS    | Arreglo de arreglos, cada uno de estos corresponde a los indices de las respuestas de cada pregunta  |
| PUBLICK_KEY_JSON    | Llave publica de la elección, por lo general se debe modificar el y   |
| BACKEND_URL    | URL de la API del backend operativo  |

Algunos de estas variables no son necesarias solo para encriptar pero si para enviar votos.

## Encriptar un voto
Para realizar esta acción de debe ejecutar el comando `python main.py encrypt`

## Enviar un voto
Para realizar esta acción se debe ejecutar el comando `python main.py send <total_votes>` siendo `total_votes` el parametro que indica la cantidad de votos a enviar
