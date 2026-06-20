import re


class EntityExtractor:

    @staticmethod
    def extrair(texto):

        entidades = []

        ips = re.findall(
            r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            texto
        )

        for ip in ips:

            entidades.append(
                ("IP", ip)
            )

        ramais = re.findall(
            r"\b[1-9][0-9]{3}\b",
            texto
        )

        for ramal in ramais:

            entidades.append(
                ("RAMAL", ramal)
            )

        comandos = [

            "sip show peers",
            "core reload",
            "pjsip show endpoints",
            "reload"
        ]

        for comando in comandos:

            if comando.lower() in texto.lower():

                entidades.append(
                    ("COMANDO", comando)
                )

        return entidades