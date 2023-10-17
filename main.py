from aviao import *
from gerente_major import *
from torre import *

if __name__ == "__main__":
    agentes = [GerenteEspacoAereo("agente_gerente_espaco_aereo@localhost", "password"),
               AgenteAeronave("agente_aeronave@localhost", "password"),
               AgenteCoordenacaoCentral("agente_coordenacao_central@localhost", "password")]

    for agente in agentes:
        agente.start()