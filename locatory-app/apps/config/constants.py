brazil_state_code_map = {
'AC':'Acre',
'AL':'Alagoas',
'AP':'Amapá',
'AM':'Amazonas',
'BA':'Bahia',
'CE':'Ceará',
'DF':'Distrito Federal',
'ES':'Espírito Santo',
'GO':'Goiás',
'MA':'Maranhão',
'MT':'Mato Grosso',
'MS':'Mato Grosso do Sul',
'MG':'Minas Gerais',
'PA':'Pará',
'PB':'Paraíba',
'PR':'Paraná',
'PE':'Pernambuco',
'PI':'Piauí',
'RJ':'Rio de Janeiro',
'RN':'Rio Grande do Norte',
'RS':'Rio Grande do Sul',
'RO':'Rondônia',
'RR':'Roraima',
'SC':'Santa Catarina',
'SP':'São Paulo',
'SE':'Sergipe',
'TO':'Tocantins',
}

# TODO
# load secrets from env
import os

mapbox_access_token = 'pk.eyJ1IjoiYWhzLXZhIiwiYSI6ImNraGsyMWVmdDByOWszNnNkdzJqcHpwOWMifQ.llITOAaVvDUflVgenIPPlw'

default_object_id = "5fbe90c4003b52fdc9b8382d"

CURRENT_ENV = 'dev'
RFM_API_CREDENTIALS = {
    "dev": {
            "username": os.environ.get('API_USERNAME', "envisageinsights"),
            "password": os.environ.get('API_PASSWORD', "EIsegmentation@2020#4"),
            "host": os.environ.get('API_URL', "http://127.0.0.1:8000/"),
        },
    "prod": {
            "username": os.environ.get('API_USERNAME', "envisageinsights"),
            "password": os.environ.get('API_PASSWORD', "EIsegmentation@2020#4"),
            "host": os.environ.get('API_URL', "http://127.0.0.1:8000/"),
        }
}
