from flask import Flask, jsonify, request
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash


@app.route('/usuario', methods=['GET'])
def usuario():
    cur = con.cursor()
    cur.execute('SELECT id_usuario, nome, email, senha FROM usuario')
    usuario2 = cur.fetchall()
    usuario_dic = []
    for user in usuario2:
        usuario_dic.append({
            'id_usuario': user[0],
            'nome': user[1],
            'email': user[2],
            'senha': user[3]

        })
    return jsonify(mensagem='lista de usuarios', usuario=usuario_dic)


def validar_senha(senha):
    """ Valida se a senha atende aos critérios de segurança sem usar regex. """
    if len(senha) < 6:
        return "A senha deve ter pelo menos 6 caracteres."

    tem_minuscula = any(c.islower() for c in senha)
    tem_maiuscula = any(c.isupper() for c in senha)
    tem_numero = any(c.isdigit() for c in senha)
    caracteres_especiais = "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~"
    qtd_especiais = sum(1 for c in senha if c in caracteres_especiais)

    if not tem_minuscula:
        return "A senha deve ter pelo menos uma letra minúscula."

    if not tem_maiuscula:
        return "A senha deve ter pelo menos uma letra maiúscula."

    if not tem_numero:
        return "A senha deve ter pelo menos um número."

    if qtd_especiais < 2:
        return "A senha deve ter pelo menos dois caracteres especiais."

    return None  # Se passar por todas as validações, a senha é válida


@app.route('/usuario', methods=['POST'])
def usuario_post():
    try:
        data = request.get_json(force=True, silent=True)

        if data is None:
            return jsonify({
                "error": "Requisição inválida, envie um JSON válido",
                "detalhes": "Verifique se o Content-Type é 'application/json' e o corpo contém um JSON válido."
            }), 415

        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')

        if not nome or not email or not senha:
            return jsonify({"error": "Nome, email e senha são obrigatórios"}), 400

        # 🔹 Valida a senha antes de cadastrar o usuário
        erro_senha = validar_senha(senha)
        if erro_senha:
            return jsonify({"error": erro_senha}), 400

        cursor = con.cursor()
        cursor.execute("SELECT 1 FROM usuario WHERE nome = ?", (nome,))
        if cursor.fetchone():
            return jsonify({"error": "Usuário já está cadastrado"}), 409

        senha = generate_password_hash(senha).decode('utf-8')

        cursor.execute("INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        con.commit()
        cursor.close()

        return jsonify({
            'mensagem': 'Usuário cadastrado com sucesso!',
            'User': {
                'nome': nome,
                'email': email
            }
        }), 201

    except Exception as e:
        return jsonify({
            "error": "Erro interno no servidor",
            "detalhes": str(e)
        }), 500




@app.route('/usuario/<int:id>', methods=['PUT'])
def usuario_put(id):
    cursor = con.cursor()

    # Consulta para verificar se o livro existe
    cursor.execute("SELECT id_usuario, nome, mail, senha FROM usuario WHERE id_usuario = ?", (id,))
    usuario_data = cursor.fetchone()

    if not usuario_data:
        cursor.close()
        return jsonify({"error": "Usuario não encontrado"}), 404

    # Captura os dados da requisição
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    # Atualiza os dados do livro
    cursor.execute("UPDATE usuario SET nome=?, email=?, senha=? WHERE id_usuario=?",
                   (nome, email, senha, id))

    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': "Usuario atualizado",
        'User': {
            'id_usuario': id,
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })


@app.route('/usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    cursor = con.cursor()

    # Verificar se o livro existe
    cursor.execute("SELECT 1 FROM usuario WHERE ID_usuario = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Usuario não encontrado"}), 404

    # Excluir o livro
    cursor.execute("DELETE FROM usuario WHERE ID_usuario = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Usuario excluído com sucesso!",
        'id_usuario': id
    })



@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json(force=True, silent=True)

        if data is None:
            return jsonify({
                "error": "Requisição inválida, envie um JSON válido",
                "detalhes": "Verifique se o Content-Type é 'application/json' e o corpo contém um JSON válido."
            }), 415

        email = data.get('email')
        senha = data.get('senha')

        if not email or not senha:
            return jsonify({"error": "Email e senha são obrigatórios"}), 400

        cursor = con.cursor()
        cursor.execute("SELECT senha FROM usuario WHERE email = ?", (email,))
        resultado = cursor.fetchone()

        if resultado is None:
            return jsonify({"error": "Usuário não encontrado"}), 404

        senha_hash = resultado[0]

        if check_password_hash(senha_hash, senha):
            return jsonify({"mensagem": "Login com sucesso!"}), 200
        else:
            return jsonify({"error": "Senha incorreta"}), 401

    except Exception as e:
        return jsonify({
            "error": "Erro interno no servidor",
            "detalhes": str(e)
        }), 500


