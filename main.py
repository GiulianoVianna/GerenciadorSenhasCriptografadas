import sys
import sqlite3
import string
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QPlainTextEdit
from cryptography.fernet import Fernet

def obter_chave():
    try:
        with open('chave.key', 'rb') as arquivo_chave:
            return arquivo_chave.read()
    except FileNotFoundError:
        nova_chave = Fernet.generate_key()
        with open('chave.key', 'wb') as arquivo_chave:
            arquivo_chave.write(nova_chave)
        return nova_chave

# Ler ou gerar e armazenar uma chave de criptografia
chave = obter_chave()
suite_cripto = Fernet(chave)

# Conectar ao banco de dados SQLite (ou criar um novo arquivo se não existir)
conexao = sqlite3.connect("senhas.db")

# Criar a tabela "senhas" se não existir
conexao.execute("""
CREATE TABLE IF NOT EXISTS senhas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    servico TEXT NOT NULL,
    senha_criptografada BLOB NOT NULL
);
""")
conexao.commit()

class GerenciadorSenhas(QWidget):
    def __init__(self):
        super().__init__()

        self.iniciar_ui()

    def iniciar_ui(self):
        self.setWindowTitle('Gerenciador de Senhas')

        layout = QVBoxLayout()

        # Criação dos elementos de interface do usuário
        self.lbl_servico = QLabel('Nome para a senha:')
        self.edit_servico = QLineEdit()

        self.lbl_senha = QLabel('Senha:')
        self.edit_senha = QLineEdit()

        self.btn_adicionar = QPushButton('Adicionar Senha')
        self.btn_adicionar.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                border: 1px solid black;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6aff6e, stop: 1 #00bf00);
            }
        """)
        self.btn_adicionar.clicked.connect(self.adicionar_senha)

        self.btn_mostrar = QPushButton('Mostrar Senhas')
        self.btn_mostrar.setStyleSheet("""
            QPushButton {
                background-color: blue;
                color: white;
                border: 1px solid black;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6a9aff, stop: 1 #0063bf);
            }
        """)
        self.btn_mostrar.clicked.connect(self.mostrar_senhas)

        self.btn_gerar_senha = QPushButton('Gerar Senha Aleatória')
        self.btn_gerar_senha.setStyleSheet("""
            QPushButton {
                background-color: orange;
                color: white;
                border: 1px solid black;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ff9a6a, stop: 1 #bf6300);
            }
        """)
        self.btn_gerar_senha.clicked.connect(self.gerar_senha_aleatoria)

        self.texto_saida = QPlainTextEdit()
        self.texto_saida.setReadOnly(True)

        # Adicionando os elementos de interface do usuário ao layout
        layout.addWidget(self.lbl_servico)
        layout.addWidget(self.edit_servico)
        layout.addWidget(self.lbl_senha)
        layout.addWidget(self.edit_senha)
        layout.addWidget(self.btn_adicionar)
        layout.addWidget(self.btn_mostrar)
        layout.addWidget(self.btn_gerar_senha)
        layout.addWidget(self.texto_saida)

        self.setLayout(layout)

    # Função para adicionar senha criptografada ao banco de dados SQLite
    def adicionar_senha(self):
        servico = self.edit_servico.text().strip()
        senha = self.edit_senha.text().strip()

        if servico and senha:
            senha_criptografada = suite_cripto.encrypt(senha.encode('utf-8'))

            with conexao:
                conexao.execute("INSERT INTO senhas (servico, senha_criptografada) VALUES (?, ?)", (servico, senha_criptografada))

            self.edit_servico.clear()
            self.edit_senha.clear()

    # Função para exibir senhas descriptografadas
    def mostrar_senhas(self):
        self.texto_saida.clear()

        with conexao:
            cursor = conexao.execute("SELECT servico, senha_criptografada FROM senhas")

            for servico, senha_criptografada in cursor.fetchall():
                senha_descriptografada = suite_cripto.decrypt(senha_criptografada).decode('utf-8')
                self.texto_saida.appendPlainText(f"{servico}: {senha_descriptografada}")

    # Função para gerar uma senha aleatória com 12 caracteres
    def gerar_senha_aleatoria(self):
        caracteres = string.ascii_letters + string.digits + string.punctuation
        senha_aleatoria = ''.join(random.choice(caracteres) for _ in range(12))
        self.edit_senha.setText(senha_aleatoria)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gerenciador_senhas = GerenciadorSenhas()
    gerenciador_senhas.show()
    gerenciador_senhas.setFixedSize(280, 400)
    sys.exit(app.exec_())

