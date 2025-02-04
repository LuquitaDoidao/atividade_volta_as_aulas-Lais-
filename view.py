from flask import Flask, jsonify, request
from main import app, con

@app.route('/livro', methods=['GET'])
def livro():
    cur = con.cursor()
    cur.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM livros')
    livros = cur.fetchall()
    livros_dic = []
    for livro in livros:
        livros_dic.append({
            'id_livro': livro[0],
            'titulo': livro[1],
            'autor': livro[2],
            'ano_publicacao': livro[3]

        })
    return jsonify(mensagem='lista de livros', livros=livros_dic)

@app.route('/livro', methods=['POST'])
def livro_post():
        data = request.get_json()
        titulo = data.get('titulo')
        autor = data.get('autor')
        ano_publicacao = data.get('ano_publicacao')

        cursor = con.cursor()
        cursor.execute("select 1 from livros where titulo = ?", (titulo,))

        if cursor.fetchone():
            return jsonify({"error ": "O livro já esta cadastrado"}), 404

        cursor.execute("insert into livros(titulo, autor, ano_publicacao) values (?,?,?)", (titulo, autor, ano_publicacao))

        con.commit()
        cursor.close()

        return jsonify({
            'mensagem':'livro cadastrado com sucesso!',
            'livro': {
                'titulo': titulo,
                'autor': autor,
                'ano_publicacao': ano_publicacao
            }
        })


@app.route('/livro/<int:id>', methods=['PUT'])
def livro_put(id):
    cursor = con.cursor()

    # Consulta para verificar se o livro existe
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicacao FROM livros WHERE id_livro = ?", (id,))
    livro_data = cursor.fetchone()

    if not livro_data:
        cursor.close()
        return jsonify({"error": "Livro não foi encontrado"}), 404

    # Captura os dados da requisição
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    # Atualiza os dados do livro
    cursor.execute("UPDATE livros SET titulo=?, autor=?, ano_publicacao=? WHERE id_livro=?",
                   (titulo, autor, ano_publicacao, id))

    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': "Livro atualizado",
        'livro': {
            'id_livro': id,
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })



