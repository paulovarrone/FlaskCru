import mysql.connector
from mysql.connector.errors import IntegrityError
from flask import Flask, request, render_template, redirect, url_for, flash, session
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

def connection():
    conexao = mysql.connector.connect(
        host = 'db',
        user=user,          
        password=password,
        database = 'crud',
        port='3306'
    )

    return conexao

def criar_DB():
    conexao = mysql.connector.connect(
        host='db',
        user=user,       
        password=password,
    )
    x = conexao.cursor()
    x.execute('CREATE DATABASE IF NOT EXISTS crud')
    conexao.commit()
    conexao.close()

    

def criar_tb():

    conexao = mysql.connector.connect(
        host='db',
        user=user,        
        password=password,
        database='crud',
        port='3306'
    )

    x = conexao.cursor()
            
    x.execute('''CREATE TABLE IF NOT EXISTS pessoa(
                nome VARCHAR(100), 
                telefone VARCHAR(15), 
                nascimento DATE,
                tipo_sanguineo VARCHAR(3),
                endereco VARCHAR(100),
                numero VARCHAR(10),
                apt VARCHAR(10),
                rg VARCHAR(9) UNIQUE,
                cpf VARCHAR(14) PRIMARY KEY,
                convenio VARCHAR(50),
                fichaMedica LONGTEXT
    )''')
    
    conexao.commit()           
    x.close()
    conexao.close()

@app.before_request
def setup():
    criar_DB()
    criar_tb()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():   
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        nascimento = request.form['nascimento']
        tipo_sanguineo = request.form['tipo_sanguineo']
        endereco = request.form['endereco']
        numero = request.form['numero']
        apt = request.form['apt']
        rg = request.form['rg']
        cpf = request.form['cpf']
        convenio = request.form['convenio']

        # data_nascimento_mysql = datetime.strptime(nascimento, "%d/%m/%Y").strftime("%Y-%m-%d")

        conexao = connection()
        x = conexao.cursor(dictionary=True)

        try:
            x.execute("SELECT * FROM pessoa WHERE cpf = %s OR rg = %s", (cpf,rg))
            pessoa = x.fetchall()

            if not pessoa:
                query = ("INSERT INTO pessoa(nome, telefone, nascimento, tipo_sanguineo, endereco, numero, apt, rg, cpf, convenio) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                valores = (nome,telefone,nascimento,tipo_sanguineo, endereco,numero,apt,rg,cpf,convenio)

                
                x.execute(query,valores)

                conexao.commit()

                flash('Cadastro realizado com sucesso.', 'sucesso')
                    
            else:
                if pessoa[0]['cpf'] == cpf:
                    flash('Usuário já cadastrado com este CPF.', 'erro')
                elif pessoa[0]['rg'] == rg:
                    flash('Usuário já cadastrado com este RG.', 'erro')


        except IntegrityError as err:
            flash(f"Erro de integridade: {err}", 'erro')

        
        finally:
            x.close()
            conexao.close()

        return redirect(url_for('cadastro'))
    
    return render_template('cadastro.html')


@app.route('/buscar', methods=['GET', 'POST'])
def procurar():
    if request.method == 'POST':
        nome = request.form['nome']

        # Conectar ao banco de dados
        conexao = connection()

        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""SELECT *, TIMESTAMPDIFF(YEAR, nascimento, CURDATE()) AS idade 
                FROM pessoa 
                WHERE nome = %s""", (nome,))
        pessoa = cursor.fetchone()

        if not pessoa:
            flash("Usuário não encontrado no sistema.", 'erro')
        else:
            pessoa['nascimento'] = pessoa['nascimento'].strftime('%d/%m/%Y')
            session['pessoa'] = pessoa
            
        
        cursor.close()
        conexao.close()

        return redirect(url_for('procurar'))
    
    pessoa = session.pop('pessoa', None)

    return render_template('buscar.html', pessoa=pessoa)


@app.route('/alterar', methods=['GET', 'POST'])
def alterar():
    
    if request.method == 'POST':
        cpf = request.form['cpf']

        conexao = connection()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pessoa WHERE cpf = %s", (cpf,))
        pessoa = cursor.fetchone()

        if not pessoa:
            flash("CPF não encontrado no sistema.", 'erro')
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
                

                flash("Dados alterados com sucesso!", 'sucesso')
            else:
                flash("Nenhum campo para alterar.", 'erro')

        cursor.close()
        conexao.close()

        return redirect(url_for('alterar'))

    return render_template('alterar.html')



# @app.route('/fixa')
# def fixa():
#     return render_template('fixa.html')

# @app.route('/agenda')
# def agenda():
#     return render_template('agenda.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)