import mysql.connector
from mysql.connector.errors import IntegrityError
from flask import Flask, request, render_template


app = Flask(__name__)

def connection():
    conexao = mysql.connector.connect(
        host = 'db',
        user = 'root',
        password ='root',
        database = 'crud'
    )

    return conexao

def criar_DB():
    conexao = mysql.connector.connect(
        host='db',
        user='root',
        password='root'
    )
    x = conexao.cursor()
    x.execute('CREATE DATABASE IF NOT EXISTS crud')
    conexao.commit()
    conexao.close()

def criar_tb():

    conexao = connection()

    x = conexao.cursor()
            
    x.execute('''CREATE TABLE IF NOT EXISTS pessoa(
                nome VARCHAR(100), 
                telefone VARCHAR(15), 
                endereco VARCHAR(100),
                numero VARCHAR(10),
                apt VARCHAR(10),
                rg VARCHAR(9) UNIQUE,
                cpf VARCHAR(14) PRIMARY KEY,
                convenio VARCHAR(50)
    )''')
    
    conexao.commit()           
    x.close()
    conexao.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    cadastro = None
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        numero = request.form['numero']
        apt = request.form['apt']
        rg = request.form['rg']
        cpf = request.form['cpf']
        convenio = request.form['convenio']

        conexao = connection()
        x = conexao.cursor(dictionary=True)
        x.execute("SELECT * FROM pessoa WHERE cpf = %s OR rg = %s", (cpf,rg))
        pessoa = x.fetchone()

        if not pessoa:
            query = ("INSERT INTO pessoa(nome, telefone, endereco, numero, apt, rg, cpf, convenio) values(%s, %s, %s, %s, %s, %s, %s, %s)")
            valores = (nome,telefone,endereco,numero,apt,rg,cpf,convenio)

            try:

                x.execute(query,valores)

                conexao.commit()

                cadastro = 'Cadastro realizado com sucesso.'

            except IntegrityError as err:
                print(f"Erro: {err}")
                cadastro = 'O usuário já está cadastrado no sistema.'

        else:
            cadastro = 'O Cadastrado já existe no sistema.'
        
        x.close()
        conexao.close()

    return render_template('cadastro.html', cadastro=cadastro)


@app.route('/buscar', methods=['GET', 'POST'])
def procurar():
    pessoa = None
    mensagem = None
    if request.method == 'POST':
        nome = request.form['nome']
        
        # Conectar ao banco de dados
        conexao = connection()

        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pessoa WHERE nome = %s", (nome,))
        pessoa = cursor.fetchone()

        if not pessoa:
            mensagem = "Usuário não encontrado no sistema: "
            pessoa = None
        else:
            # Buscar a pessoa pelo CPF
            query = "SELECT nome, telefone, endereco, numero, apt, rg, cpf, convenio FROM pessoa WHERE nome = %s"
            cursor.execute(query, (nome,))
            # Retorna a primeira pessoa encontrada
            pessoa = cursor.fetchone()  
        
        cursor.close()
        conexao.close()

    return render_template('buscar.html', pessoa=pessoa, mensagem=mensagem)


@app.route('/alterar', methods=['GET', 'POST'])
def alterar():
    mensagem = None
    if request.method == 'POST':
        cpf = request.form['cpf']

        conexao = connection()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pessoa WHERE cpf = %s", (cpf,))
        pessoa = cursor.fetchone()

        if not pessoa:
            mensagem = "CPF não encontrado no sistema."
        else:
            nome = request.form.get('nome')
            telefone = request.form.get('telefone')
            endereco = request.form.get('endereco')
            numero = request.form.get('numero')
            apt = request.form.get('apt')
            convenio = request.form.get('convenio')

            query = 'UPDATE pessoa SET '

            values = []
            fields = []

            if nome:
                fields.append("nome = %s")
                values.append(nome)
            if telefone:
                fields.append("telefone = %s")
                values.append(telefone)
            if endereco:
                fields.append("endereco = %s")
                values.append(endereco)
            if numero:
                fields.append("numero = %s")
                values.append(numero)
            if apt:
                fields.append("apt = %s")
                values.append(apt)
            if convenio:
                fields.append("convenio = %s")
                values.append(convenio)
            
            # Certificar que há algo a ser atualizado
            if fields:
                query += ", ".join(fields) + " WHERE cpf = %s"
                values.append(cpf)
                
                # Conectar ao banco de dados e executar a query
                conexao = connection()
                cursor = conexao.cursor()
                cursor.execute(query, tuple(values))

                conexao.commit()
                

                mensagem = "Dados alterados com sucesso!"
            else:
                mensagem = "Nenhum campo para alterar."

        cursor.close()
        conexao.close()

    return render_template('alterar.html', mensagem=mensagem)


# @app.route('/fixa')
# def fixa():
#     return render_template('fixa.html')

# @app.route('/agenda')
# def agenda():
#     return render_template('agenda.html')

if __name__ == '__main__':
    criar_DB()
    criar_tb()
    app.run(host='0.0.0.0', debug=True)