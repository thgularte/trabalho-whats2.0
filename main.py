from client import Cliente

def cliente_interface():
    cliente = Cliente()
    while True:
        print("Selecione uma opção:")
        print("1. Registrar usuário")
        print("2. Conectar cliente")
        print("3. Enviar mensagem")
        print("4. Criar grupo")
        print("5. Enviar mensagem em grupo")
        escolha = input("Opção: ")

        if escolha == '1':
            cliente.registra_usuario()
        elif escolha == '2':
            client_id = input("Digite o ID do cliente: ")
            cliente.acessar_conta(client_id)
        elif escolha == '3':
            src_id = input("Digite o ID do remetente: ")
            dst_id = input("Digite o ID do destinatário: ")
            timestamp = input("Digite o timestamp: ")
            data = input("Digite a mensagem: ")
            cliente.enviar_mensagem(src_id, dst_id, timestamp, data)
        elif escolha == '4':
            criador_id = input("Digite o ID do criador: ")
            timestamp = input("Digite o timestamp: ")
            members = input("Digite os IDs dos membros (separados por espaço): ").split()
            cliente.criar_grupo(criador_id, timestamp, members)
        elif escolha == '5':
            group_id = input("Digite o ID do grupo: ")
            src_id = input("Digite o ID do remetente: ")
            timestamp = input("Digite o timestamp: ")
            data = input("Digite a mensagem: ")
            cliente.enviar_mensagem_grupo(group_id, src_id, timestamp, data)
        
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    cliente_interface()