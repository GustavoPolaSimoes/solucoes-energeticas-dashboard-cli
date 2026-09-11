
import json
import os
import random
import plotext as plt

DB_FILE = "dados_energia.json"


def carregar_dados():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            print("⚠️ Não foi possível carregar o banco de dados.")
            return {"usuarios": {}}

    return {"usuarios": {}}


def salvar_dados(dados):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
    except OSError:
        print("❌ Erro ao salvar os dados.")


class SistemaEnergia:

    def __init__(self):
        self.dados = carregar_dados()
        self.usuario_atual = None

    # =========================================================
    # USUÁRIO
    # =========================================================

    def cadastrar_usuario(self):
        print("\n--- CADASTRO DE USUÁRIO ---")

        username = input("Nome de usuário: ").strip()

        if not username:
            print("❌ O nome de usuário não pode ficar vazio.")
            return

        if username in self.dados["usuarios"]:
            print("❌ Usuário já existe!")
            return

        senha = input("Senha: ").strip()

        if not senha:
            print("❌ A senha não pode ficar vazia.")
            return

        codigo_2fa = input("🔒 PIN de 4 dígitos para 2FA: ").strip()

        if len(codigo_2fa) != 4 or not codigo_2fa.isdigit():
            print("❌ O PIN deve possuir exatamente 4 dígitos.")
            return

        self.dados["usuarios"][username] = {
            "senha": senha,
            "2fa_pin": codigo_2fa,
            "imoveis": {}
        }

        salvar_dados(self.dados)

        print("✅ Usuário cadastrado com sucesso!")

    def login(self):
        print("\n--- LOGIN ---")

        username = input("Nome de usuário: ").strip()
        senha = input("Senha: ").strip()

        user = self.dados["usuarios"].get(username)

        if user and user["senha"] == senha:

            pin = input("🔑 Digite seu PIN 2FA: ").strip()

            if pin == user["2fa_pin"]:
                self.usuario_atual = username

                print(f"\n✅ Bem-vindo(a), {username}!")

                self.menu_principal()

            else:
                print("❌ PIN 2FA incorreto!")

        else:
            print("❌ Usuário ou senha inválidos!")

    # =========================================================
    # IMÓVEIS
    # =========================================================

    def cadastrar_imovel(self):
        print("\n--- CADASTRO DE IMÓVEL ---")

        nome_imovel = input(
            "Nome do Imóvel (ex: Casa, Apê, Escritório): "
        ).strip()

        if not nome_imovel:
            print("❌ O nome do imóvel não pode ficar vazio.")
            return

        user_data = self.dados["usuarios"][self.usuario_atual]

        if nome_imovel in user_data["imoveis"]:
            print("⚠️ Imóvel já cadastrado!")
            return

        user_data["imoveis"][nome_imovel] = {
            "equipamentos": [],
            "historico_meses": []
        }

        salvar_dados(self.dados)

        print(f"✅ Imóvel '{nome_imovel}' cadastrado!")

    # =========================================================
    # EQUIPAMENTOS
    # =========================================================

    def cadastrar_equipamento(self, imovel_nome):

        imovel = self.dados["usuarios"][
            self.usuario_atual
        ]["imoveis"][imovel_nome]

        if "equipamentos" not in imovel:
            imovel["equipamentos"] = []

        print(
            f"\n--- CADASTRO DE EQUIPAMENTO ({imovel_nome}) ---"
        )

        nome = input(
            "Nome do aparelho (ex: Geladeira, Ar Condicionado, TV): "
        ).strip()

        if not nome:
            print("❌ O nome do equipamento não pode ficar vazio.")
            return

        try:

            potencia = float(
                input("Potência em Watts (ex: 300 W): ")
            )

            qtd = int(
                input("Quantidade deste equipamento: ")
            )

            horas_normal = float(
                input(
                    "Horas de uso diário FORA do pico "
                    "(0h - 18h / 21h - 24h): "
                )
            )

            horas_pico = float(
                input(
                    "Horas de uso diário NO PICO "
                    "(18h às 21h - máx 3h): "
                )
            )

            # -----------------------------
            # VALIDAÇÕES
            # -----------------------------

            if potencia <= 0:
                print(
                    "❌ ALERTA PB13: "
                    "A potência deve ser maior que zero."
                )
                return

            if qtd <= 0:
                print(
                    "❌ ALERTA PB13: "
                    "A quantidade deve ser maior que zero."
                )
                return

            if horas_normal < 0 or horas_pico < 0:
                print(
                    "❌ ALERTA PB13: "
                    "As horas não podem ser negativas."
                )
                return

            if horas_pico > 3:
                print(
                    "⚠️ ALERTA PB13: "
                    "O horário de pico possui no máximo 3 horas "
                    "(18h às 21h)."
                )

                horas_pico = 3.0

            if horas_normal > 21:
                print(
                    "❌ ALERTA PB13: "
                    "O uso fora do pico não pode ultrapassar "
                    "21 horas por dia."
                )
                return

            if (horas_normal + horas_pico) > 24:
                print(
                    "❌ ALERTA PB13: "
                    "O total de horas no dia não pode exceder 24 horas!"
                )
                return

            equipamento = {
                "nome": nome,
                "potencia_w": potencia,
                "quantidade": qtd,
                "horas_normal": horas_normal,
                "horas_pico": horas_pico
            }

            imovel["equipamentos"].append(equipamento)

            salvar_dados(self.dados)

            print(
                f"✅ Equipamento '{nome}' "
                "adicionado com sucesso!"
            )

        except ValueError:
            print(
                "❌ Entrada inválida! "
                "Digite números válidos."
            )

    def listar_equipamentos(self, imovel_nome):

        imovel = self.dados["usuarios"][
            self.usuario_atual
        ]["imoveis"][imovel_nome]

        equipamentos = imovel.get("equipamentos", [])

        print(
            f"\n--- EQUIPAMENTOS CADASTRADOS ({imovel_nome}) ---"
        )

        if not equipamentos:
            print("Nenhum equipamento cadastrado ainda.")
            return

        for idx, eq in enumerate(equipamentos, start=1):

            kwh_dia_n = (
                eq["potencia_w"]
                * eq["horas_normal"]
                * eq["quantidade"]
            ) / 1000

            kwh_dia_p = (
                eq["potencia_w"]
                * eq["horas_pico"]
                * eq["quantidade"]
            ) / 1000

            consumo_mensal = (
                kwh_dia_n + kwh_dia_p
            ) * 30

            print(
                f"{idx}. {eq['nome']} "
                f"(x{eq['quantidade']}) - "
                f"{eq['potencia_w']}W | "
                f"Uso: {eq['horas_normal']}h Normal + "
                f"{eq['horas_pico']}h Pico -> "
                f"{consumo_mensal:.1f} kWh/mês"
            )

    # =========================================================
    # CONSUMO
    # =========================================================

    def _calcular_consumo_base_mensal(self, imovel_nome):

        imovel = self.dados["usuarios"][
            self.usuario_atual
        ]["imoveis"][imovel_nome]

        equipamentos = imovel.get("equipamentos", [])

        kwh_normal_mes = 0.0
        kwh_pico_mes = 0.0

        for eq in equipamentos:

            kwh_dia_n = (
                eq["potencia_w"]
                * eq["horas_normal"]
                * eq["quantidade"]
            ) / 1000

            kwh_dia_p = (
                eq["potencia_w"]
                * eq["horas_pico"]
                * eq["quantidade"]
            ) / 1000

            kwh_normal_mes += kwh_dia_n * 30
            kwh_pico_mes += kwh_dia_p * 30

        return kwh_normal_mes, kwh_pico_mes

    # =========================================================
    # SIMULAÇÃO
    # =========================================================

    def simular_tempo(self, imovel_nome):

        imovel = self.dados["usuarios"][
            self.usuario_atual
        ]["imoveis"][imovel_nome]

        if "historico_meses" not in imovel:
            imovel["historico_meses"] = []

        if not imovel.get("equipamentos"):
            print(
                "⚠️ Cadastre pelo menos um equipamento "
                "antes de simular o tempo!"
            )
            return

        print("\n--- SIMULAR PASSAGEM DE TEMPO ---")
        print("1. Passar 1 Mês")
        print("2. Passar 1 Ano (12 Meses)")

        op = input("Escolha: ").strip()

        if op == "1":
            meses_a_passar = 1

        elif op == "2":
            meses_a_passar = 12

        else:
            print("❌ Opção inválida.")
            return

        kwh_n_base, kwh_p_base = (
            self._calcular_consumo_base_mensal(imovel_nome)
        )

        for _ in range(meses_a_passar):

            fator_var = random.uniform(0.85, 1.15)

            c_normal = round(
                kwh_n_base * fator_var,
                2
            )

            c_pico = round(
                kwh_p_base * fator_var,
                2
            )

            imovel["historico_meses"].append({
                "kwh_normal": c_normal,
                "kwh_pico": c_pico
            })

        salvar_dados(self.dados)

        print(
            f"⏱️ Simulação concluída! "
            f"{meses_a_passar} mês(es) processado(s)."
        )

    # =========================================================
    # RESUMO
    # =========================================================

    def visualizar_resumo_e_gastos(self, imovel_nome):

        imovel = self.dados["usuarios"][
            self.usuario_atual
        ]["imoveis"][imovel_nome]

        historico = imovel.get(
            "historico_meses",
            []
        )

        if not historico:
            print(
                "⚠️ Nenhuma simulação executada ainda. "
                "Use a opção de passar o tempo."
            )
            return

        TARIFA_NORMAL = 0.65
        TARIFA_PICO = 0.98

        total_n = sum(
            m.get("kwh_normal", 0.0)
            for m in historico
        )

        total_p = sum(
            m.get("kwh_pico", 0.0)
            for m in historico
        )

        total_kwh = total_n + total_p

        gasto_n = total_n * TARIFA_NORMAL
        gasto_p = total_p * TARIFA_PICO

        gasto_total = gasto_n + gasto_p

        qtd_meses = len(historico)

        media_mensal_kwh = (
            total_kwh / qtd_meses
        )

        media_mensal_rs = (
            gasto_total / qtd_meses
        )

        print(
            f"\n================ RESUMO ENERGÉTICO: "
            f"{imovel_nome} ================"
        )

        print(
            f"Equipamentos Monitorados: "
            f"{len(imovel.get('equipamentos', []))}"
        )

        print(
            f"Meses Simulados: {qtd_meses}"
        )

        print(
            f"Consumo Total Acumulado: "
            f"{total_kwh:.2f} kWh"
        )

        print(
            f" -> Fora de Pico: "
            f"{total_n:.2f} kWh | "
            f"Custo: R$ {gasto_n:.2f}"
        )

        print(
            f" -> Pico (18h-21h): "
            f"{total_p:.2f} kWh | "
            f"Custo: R$ {gasto_p:.2f}"
        )

        print("-----------------------------------------------")

        print(
            f"Média de Consumo Mensal: "
            f"{media_mensal_kwh:.2f} kWh/mês"
        )

        print(
            f"Média de Consumo Anual Estimada: "
            f"{media_mensal_kwh * 12:.2f} kWh/ano"
        )

        print(
            f"Gasto Mensal Médio: "
            f"R$ {media_mensal_rs:.2f}/mês"
        )

        print(
            f"Gasto Total Acumulado: "
            f"R$ {gasto_total:.2f}"
        )

        print(
            "================================================="
        )

    # =========================================================
    # GRÁFICO
    # =========================================================

    def exibir_grafico_terminal(self, imovel_nome):
        imovel = self.dados["usuarios"][self.usuario_atual]["imoveis"][imovel_nome]
        historico = imovel.get("historico_meses", [])

        if not historico:
            print(
                "⚠️ Sem dados simulados suficientes para gerar o gráfico. "
                "Execute a opção 3 primeiro!"
            )
            return

        meses = list(range(1, len(historico) + 1))

        totais_kwh = [
            m.get("kwh_normal", 0.0) + m.get("kwh_pico", 0.0)
            for m in historico
        ]

        fig = plt.figure
        fig.clear()

        sinal = fig.signal(meses,totais_kwh)

        sinal.lines()

        fig.draw(sinal)

        fig.title(f"Consumo de Energia (PB12) - {imovel_nome}")
        fig.label("Meses",axis="x")
        fig.label("kWh", axis="y")

        fig.ruler("x").ticks(
            meses,
            [f"M{mes}" for mes in meses]
        )

        fig.show()

    def menu_imovel(self, imovel_nome):

        while True:

            print(
                f"\n--- Gerenciando Imóvel: "
                f"[{imovel_nome}] ---"
            )

            print("1. Cadastrar Aparelho / Equipamento")
            print("2. Listar Aparelhos Cadastrados")
            print(
                "3. Simular Passagem de Tempo "
                "(1 Mês / 1 Ano)"
            )
            print(
                "4. Ver Resumo Energético e Médias "
                "(PB11/PB17)"
            )
            print(
                "5. Exibir Gráfico de Consumo "
                "no Terminal (PB12)"
            )
            print("6. Voltar ao Menu Principal")

            opcao = input("Opção: ").strip()

            if opcao == "1":
                self.cadastrar_equipamento(
                    imovel_nome
                )

            elif opcao == "2":
                self.listar_equipamentos(
                    imovel_nome
                )

            elif opcao == "3":
                self.simular_tempo(
                    imovel_nome
                )

            elif opcao == "4":
                self.visualizar_resumo_e_gastos(
                    imovel_nome
                )

            elif opcao == "5":
                self.exibir_grafico_terminal(
                    imovel_nome
                )

            elif opcao == "6":
                break

            else:
                print("❌ Opção inválida.")

    # =========================================================
    # MENU PRINCIPAL
    # =========================================================

    def menu_principal(self):

        while True:

            print(
                f"\n--- MENU PRINCIPAL "
                f"({self.usuario_atual}) ---"
            )

            print("1. Cadastrar Novo Imóvel")
            print("2. Selecionar Imóvel")
            print("3. Sair / Logoff")

            op = input("Opção: ").strip()

            if op == "1":

                self.cadastrar_imovel()

            elif op == "2":

                imoveis = self.dados[
                    "usuarios"
                ][
                    self.usuario_atual
                ]["imoveis"]

                if not imoveis:
                    print(
                        "⚠️ Nenhum imóvel cadastrado."
                    )
                    continue

                print("\nSeus Imóveis:")

                lista_imoveis = list(
                    imoveis.keys()
                )

                for idx, nome in enumerate(
                    lista_imoveis,
                    start=1
                ):
                    print(
                        f"{idx}. {nome}"
                    )

                try:

                    escolha = int(
                        input(
                            "Escolha o número do imóvel: "
                        )
                    ) - 1

                    if (
                        0 <= escolha
                        < len(lista_imoveis)
                    ):

                        self.menu_imovel(
                            lista_imoveis[escolha]
                        )

                    else:
                        print(
                            "❌ Opção inválida."
                        )

                except ValueError:
                    print(
                        "❌ Digite um número válido."
                    )

            elif op == "3":

                self.usuario_atual = None

                print(
                    "🔒 Sessão encerrada."
                )

                break

            else:
                print("❌ Opção inválida.")

    # =========================================================
    # EXECUÇÃO
    # =========================================================

    def executar(self):

        while True:

            print(
                "\n=========================================="
            )

            print(
                "⚡ SISTEMA DE RESUMO ENERGÉTICO (SERS)"
            )

            print(
                "=========================================="
            )

            print("1. Login")
            print("2. Criar Conta")
            print("3. Sair")

            opcao = input("Opção: ").strip()

            if opcao == "1":

                self.login()

            elif opcao == "2":

                self.cadastrar_usuario()

            elif opcao == "3":

                print(
                    "Encerrando aplicação..."
                )

                break
                
            else:
                print("❌ Opção inválida.")


# =============================================================
# INÍCIO DO PROGRAMA
# =============================================================

if __name__ == "__main__":
    app = SistemaEnergia()
    app.executar()

