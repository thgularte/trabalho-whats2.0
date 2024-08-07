from client import Cliente

def cliente_interface():
    cliente = Cliente()
    while True:
        print("Selecione uma opção:")
        print("1. Registrar usuário")
        print("2. Conectar cliente")
        escolha = input("Opção: ")

        if escolha == '1':
            cliente.registra_usuario()
        elif escolha == '2':
            client_id = input("Digite o ID do cliente: ")
            cliente.acessar_conta(client_id)
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    cliente_interface()