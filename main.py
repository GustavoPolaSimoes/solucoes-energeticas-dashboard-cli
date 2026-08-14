class Eletrodomestico:
    def __init__(self,nome='',watts=0.0):
        self.watts=watts
        self.nome=nome

class Casa:
    def __init__(self):
        self.eletrodomesticos = []

    def mostrarEletrodomesticos(self):
        for e in self.eletrodomesticos:
            print("=====")
            print(f"Nome: {e.nome}")
            print(f"Watts: {e.watts}")
            print("=====")
            print("")

    def adicionarEletrodomestico(self, eletrodomestico):
        self.eletrodomesticos.append(eletrodomestico)

    def mediaEmWatts(self):
        if len(self.eletrodomesticos) == 0:
            return 0

        soma=0

        for e in self.eletrodomesticos:
            soma+=e.watts

        media=soma/len(self.eletrodomesticos)

        return media


eletrodomesticos = [
    Eletrodomestico('Aparelho de som', 200),
    Eletrodomestico('Computador', 350),
    Eletrodomestico('Condicionador de ar', 1600),
    Eletrodomestico('Chuveiro elétrico', 5000),
    Eletrodomestico('Forno de microondas', 1300),
    Eletrodomestico('Freezer acima de 200 litros', 150),
    Eletrodomestico('Liquidificador', 400),
    Eletrodomestico('Máquina de lavar roupa', 1500),
    Eletrodomestico('Refrigerador Duplex ou freezer', 350),
    Eletrodomestico('Secador de cabelo', 1300),
    Eletrodomestico('Televisor', 200),
    Eletrodomestico('Ventilador', 100),
    Eletrodomestico('Cafeteira', 300),
    Eletrodomestico('Ferro elétrico Comum', 750),
    Eletrodomestico('Forno elétrico', 5000),
]

def inicio():
    print("=====SEJA BEM VINDO====")
    print("- Dashboards de custo energético")

def mostrarOpcoes():
    print("[1] - Mostrar eletrodomesticos")
    print("[2] - Cadastrar eletrodomestico")
    print("[3] - Cálculo médio de custo energético")
    print("")

def inserirEletrodomesticos(casa):
    for eletrodomestico in eletrodomesticos:
        casa.adicionarEletrodomestico(eletrodomestico)

def loop(casa):
    mostrarOpcoes()

    opcaoSelecionada = input("Escolha a sua opção: ")

    if opcaoSelecionada == "1":
        casa.mostrarEletrodomesticos()

    if opcaoSelecionada == "2":
        try:
            nome = input("Digite o nome: ")
            watts = float(input("Digite a quantidade de watts: "))
            novo_eletrodomestico = Eletrodomestico(nome,watts)
            casa.adicionarEletrodomestico(novo_eletrodomestico)
        except ValueError:
            print('Não foi possível cadastrar, verifique se os dados estão corretos.')

    if opcaoSelecionada == "3":
        print("====")
        print(f"O custo médio da casa é: {casa.mediaEmWatts()}")
        print("====")
        print("")

    if opcaoSelecionada == "exit":
        exit()

    loop(casa)

def main():
    casa = Casa()
    inserirEletrodomesticos(casa)

    inicio()
    loop(casa)

main()