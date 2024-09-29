import mysql.connector
from mysql.connector.errors import IntegrityError
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv
import os
from datetime import time, timedelta, datetime

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

    conexao = connection()
    cursor = conexao.cursor()
            
    cursor.execute('''CREATE TABLE IF NOT EXISTS pessoa(
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100), 
                telefone VARCHAR(15), 
                nascimento DATE,
                tipo_sanguineo VARCHAR(3),
                endereco VARCHAR(100),
                numero VARCHAR(10),
                apt VARCHAR(10),
                rg VARCHAR(9) UNIQUE,
                cpf VARCHAR(14) UNIQUE,
                convenio VARCHAR(50),
                fichaMedica LONGTEXT
    )''')
    
    conexao.commit()           
    cursor.close()
    conexao.close()

def criar_con():
    conexao = connection()
    cursor = conexao.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS consulta (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nome VARCHAR(100), 
                    telefone VARCHAR(15),
                    data DATE,
                    hora TIME,  
                    UNIQUE (data, hora)
                    
    )''')


    conexao.commit()           
    cursor.close()
    conexao.close()

@app.before_request
def setup():
    criar_DB()
    criar_tb()
    criar_con()

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
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM pessoa WHERE cpf = %s OR rg = %s", (cpf,rg))
            pessoa = cursor.fetchall()

            if not pessoa:
                query = ("INSERT INTO pessoa(nome, telefone, nascimento, tipo_sanguineo, endereco, numero, apt, rg, cpf, convenio) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                valores = (nome,telefone,nascimento,tipo_sanguineo, endereco,numero,apt,rg,cpf,convenio)

                
                cursor.execute(query,valores)

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
            cursor.close()
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


@app.route('/ficha', methods=['GET', 'POST'])
def ficha():
    fichaMedica = ""  # Inicializa a variável
    nome = ""

    if request.method == 'POST':
        nome = request.form['nome']
        action = request.form.get('action')  # Obter a ação do botão

        if action == "cadastrar":
            fichaMedica = request.form['fichaMedica']
            conexao = connection()
            cursor = conexao.cursor(dictionary=True)

            try:
                query = ("UPDATE pessoa SET fichaMedica = %s WHERE nome = %s")
                valores = (fichaMedica, nome)

                cursor.execute(query, valores)
                conexao.commit()

                if cursor.rowcount > 0:
                    flash('Ficha cadastrada com sucesso.', 'sucesso')
                else:
                    flash('Nenhum registro encontrado para atualizar.', 'erro')

            except Exception as e:
                flash(f'A ficha não foi cadastrada: {str(e)}', 'erro')

            finally:
                cursor.close()
                conexao.close()

        elif action == "consultar":
            conexao = connection()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT fichaMedica FROM pessoa WHERE nome = %s", (nome,))
            result = cursor.fetchone()
            if result:
                fichaMedica = result['fichaMedica']  # Atribua o valor encontrado
            else:
                flash('Nenhum registro encontrado para consulta.', 'erro')
            cursor.close()
            conexao.close()
        
            
            session['fichaMedica'] = fichaMedica
            session['nome'] = nome
            
            return redirect(url_for('ficha'))  # Redirecionar para evitar envio duplicado

    # Recuperar dados da sessão para preenchimento nos campos
    fichaMedica = session.pop('fichaMedica', "")
    nome = session.pop('nome', "")

    return render_template('ficha.html', fichaMedica=fichaMedica, nome=nome)


@app.route('/api/events')
def events():
    conexao = connection()  
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT nome, telefone, data, hora FROM consulta")
    events = cursor.fetchall()
    
    
    calendar_events = []
    for event in events:
        
        formatted_date = event['data'].strftime('%Y-%m-%d')  

        
        if isinstance(event['hora'], datetime):  
            hora = event['hora'].time()  
        elif isinstance(event['hora'], timedelta):  
            hora = (datetime.min + event['hora']).time() 
        else:
            raise TypeError("O campo 'hora' deve ser um objeto datetime ou timedelta.")

        formatted_time = hora.strftime('%H:%M')  

        
        start_datetime = datetime.combine(event['data'], hora)  
        end_datetime = start_datetime + timedelta(minutes=1)  
        formatted_end_date = end_datetime.strftime('%Y-%m-%d')  
        formatted_end_time = end_datetime.strftime('%H:%M')  

        calendar_events.append({
            'id': event['telefone'],  
            'title': event['nome'],
            'start': formatted_date + 'T' + formatted_time,  
            'end': formatted_end_date + 'T' + formatted_end_time  
        })

    cursor.close()
    conexao.close()
    
    return jsonify(calendar_events)



@app.route('/api/consulta', methods=['POST'])
def add_consulta():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    data = request.form.get('data')
    hora = request.form.get('hora')

    conexao = connection()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO consulta (nome, telefone, data, hora) VALUES (%s, %s, %s, %s)",
                   (nome, telefone, data, hora))
    conexao.commit()

    cursor.close()
    conexao.close()

    return jsonify({'message': 'Consulta marcada com sucesso'}), 201


# Exemplo de como os eventos podem ser retornados do seu endpoint
@app.route('/api/events', methods=['GET'])
def get_events():
    conexao = connection()  # Usando a variável conexao
    cursor = conexao.cursor()

    # Busca todos os eventos no banco de dados
    cursor.execute("SELECT telefone, data, hora FROM consulta")
    eventos = cursor.fetchall()

    # Formata os eventos para o formato que o FullCalendar espera
    eventos_formatados = [{
        'id': telefone,  # Usando o telefone como ID do evento
        'title': 'Consulta',  # O título do evento pode ser fixo ou dinâmico
        'start': data,  # Usando apenas a data
        'hora': hora,  # Se necessário, mas não será exibido
    } for telefone, data, hora in eventos]

    return jsonify(eventos_formatados)



@app.route('/api/delete-event/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    data = request.get_json()
    date = data.get('date')
    hora = data.get('time')

    conexao = connection()
    cursor = conexao.cursor()
    print(f"ID do evento: {event_id}")
    print(f"Data recebida: {date}")
    print(f"Hora recebida: {hora}")
    # Construa sua consulta SQL para garantir que o evento correto seja removido
    cursor.execute("DELETE FROM consulta WHERE telefone = %s AND DATE(data) = %s AND TIME(hora) = %s", (event_id, date, hora))
    
    conexao.commit()
    cursor.close()
    conexao.close()
    
    return jsonify({'status': 'Consulta removida com sucesso!'})


@app.route('/agenda')
def agenda():
    return render_template('agenda.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)