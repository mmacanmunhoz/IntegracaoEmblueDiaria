
import requests
import json
from shared.credenciais import *


#TODO Carregar de um arquiv json
MVX_API = credencial('mvx_api')
MVX_CHAVE = credencial('mvx_chave')
MVX_USUARIO = credencial('mvx_usuario')
MVX_SENHA = credencial('mvx_senha')

MVX_XML_ESQUELETO = f"""<?xml version="1.0" encoding="utf-8" ?>
<LinxMicrovix>
    <Authentication user="{MVX_USUARIO}" password="{MVX_SENHA}" />
    <ResponseFormat>json</ResponseFormat>
    {{}}
</LinxMicrovix>
"""

def mvx_montar_corpo_req(nome_comando,lst_params):
    return MVX_XML_ESQUELETO.format(mvx_montar_comando(nome_comando,lst_params))

def mvx_montar_comando(nome,lst_params):
    comando = f"""<Command>
        <Name>{nome}</Name>
        <Parameters>
            {{}}
        </Parameters>
        </Command>
    """

    param_format = """<Parameter id="PID">PV</Parameter>"""

    params = []
    for p in lst_params:
        params.append(param_format.replace("PID",p['id']).replace("PV",p['value']))

    all_params = ""
    for p in params:
        all_params += p
    return comando.format(all_params)

def mvx_req_xml(xml_string):
    headers = {
        'Content-Type': 'application/xml',
        'Accept': 'text/json; charset=utf-8',
    }
    response = requests.post(MVX_API, data=xml_string, headers=headers)
    return response

def mvx_sanitize_json(jsonStr):
    
    idx = jsonStr.rfind(",")
    if idx > 0:
        jsonStr = jsonStr[:idx] + ' ' + jsonStr[idx + 1:]

    return jsonStr

    

