from cliente import Cliente

def cliente_interface():
    while True:
        cliente = Cliente()
        if cliente.conectado:
            break
        print("Falha ao conectar ao servidor. Tentar novamente? (S/n)")
        retry = input().lower()
        if retry != 's':
            return

    while True:
        print("\n========= Menu Principal =========")
        print("1. Registrar usuário")
        print("2. Conectar cliente")
        print("3. Sair")
        print("==================================")
        escolha = input("Opção: ")

        if escolha == '1':
            cliente.registra_usuario()
            print("Usuário registrado com sucesso!")
        elif escolha == '2':
            while True:
                client_id = input("Digite o ID do cliente: ")
                if not Cliente.validar_id(client_id):
                    print("ID inválido. Deve ter 13 dígitos. Tente novamente.")
                else:
                    break
            cliente.acessar_conta(client_id)
        elif escolha == '3':
            cliente.desconectar()
            print("Desligando o programa...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    cliente_interface()
