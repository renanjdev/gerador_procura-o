from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_RIGHT
from datetime import datetime
import io
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'

def validar_cpf(cpf):
    return re.match(r'^\d{11}$', cpf)

def validar_cep(cep):
    return re.match(r'^\d{8}$', cep)

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/form_fisica')
def form_fisica():
    return render_template('form_fisica.html')

@app.route('/form_juridica')
def form_juridica():
    return render_template('form_juridica.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Obtenha os dados do formulário
    nome_outorgante = request.form['nome_outorgante'].upper()
    cpf_outorgante = re.sub(r'\D', '', request.form['cpf_outorgante'])
    cep_outorgante = re.sub(r'\D', '', request.form['cep_outorgante'])
    rua_outorgante = request.form['rua_outorgante'].upper()
    numero_outorgante = request.form['numero_outorgante']
    bairro_outorgante = request.form['bairro_outorgante'].upper()
    cidade_outorgante = request.form['cidade_outorgante'].upper()
    estado_outorgante = request.form['estado_outorgante'].upper()
    concessionaria = request.form['concessionaria'].upper()

    # Validação do CPF e CEP
    if not validar_cpf(cpf_outorgante):
        flash("CPF inválido. O CPF deve ter 11 dígitos.")
        return redirect(url_for('form_fisica'))
    
    if not validar_cep(cep_outorgante):
        flash("CEP inválido. O CEP deve ter 8 dígitos.")
        return redirect(url_for('form_fisica'))

    # Formatar CPF e CEP
    cpf_formatado = f"{cpf_outorgante[:3]}.{cpf_outorgante[3:6]}.{cpf_outorgante[6:9]}-{cpf_outorgante[9:]}"
    cep_formatado = f"{cep_outorgante[:5]}-{cep_outorgante[5:]}"

    # Formate a data atual
    hoje = datetime.now()
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    data_formatada = f"{cidade_outorgante}, {hoje.day} de {meses[hoje.month - 1]} de {hoje.year}"

    # Função para determinar "de" ou "do"
    def artigo_estado(estado):
        estados_com_do = ["AMAZONAS", "AMAPÁ", "ESPÍRITO SANTO", "PARÁ", "PARANÁ", "RIO DE JANEIRO", "RIO GRANDE DO NORTE", "RIO GRANDE DO SUL", "PIAUÍ", "TOCANTINS"]
        if estado in estados_com_do:
            return "do"
        else:
            return "de"

    artigo = artigo_estado(estado_outorgante)
    estado_extenso = f"{artigo} {estado_outorgante}"

    # Crie um arquivo PDF em memória
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Estilos de parágrafo
    styles = getSampleStyleSheet()
    styles['Title'].fontSize = 16
    styles['Title'].spaceAfter = 20
    styles['Normal'].fontSize = 12
    styles['Normal'].leading = 16  # Adiciona espaçamento entre as linhas
    styles.add(ParagraphStyle(name='Right', parent=styles['Normal'], alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='Left', parent=styles['Normal'], alignment=TA_LEFT))
    styles.add(ParagraphStyle(name='Justify', parent=styles['Normal'], alignment=TA_JUSTIFY, leftIndent=-10, rightIndent=-10))  # Ajuste os valores aqui

    # Elementos do PDF
    elements = []

    # Título
    elements.append(Paragraph("PROCURAÇÃO – PESSOA FÍSICA", styles['Title']))

    # Texto principal
    texto1 = (f"Por este instrumento particular de procuração, eu, {nome_outorgante}, "
              f"BRASILEIRO(A), portador(a) do CPF nº {cpf_formatado}, com residência no endereço "
              f"{rua_outorgante}, Nº {numero_outorgante}, bairro {bairro_outorgante}, cidade de "
              f"{cidade_outorgante}, no estado {estado_extenso}, CEP {cep_formatado}, doravante "
              f"denominado(a) Outorgante, nomeio e constituo como meu bastante procurador o Sr. "
              f"RENAN JANUÁRIO SILVA, BRASILEIRO, ELETROTÉCNICO, inscrito no CPF nº 391.835.518-75, "
              f"residente e domiciliado na RUA JOSÉ HOMERO MOREIRA, 155, no bairro JARDIM IMPERIAL, na cidade de "
              f"PROMISSÃO, no estado de SÃO PAULO.")
    
    texto2 = ("Este procurador fica investido de amplos e ilimitados poderes para representar o Outorgante perante a "
              f"{concessionaria} pelo período de 12 meses a partir da data de assinatura deste documento, com a finalidade "
              "específica de tratar todos os processos relacionados ao acesso ao sistema de compensação de energia elétrica "
              "por meio da Geração Distribuída, conforme descrito na Lei 14.300/2022.")
    
    elements.append(Paragraph(texto1, styles['Justify']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(texto2, styles['Justify']))

    # Data
    elements.append(Spacer(1, 25))
    elements.append(Paragraph(data_formatada, styles['Right']))

    # Assinatura
    elements.append(Spacer(1, 100))
    elements.append(Paragraph("_____________________________", styles['Left']))
    elements.append(Paragraph(f"{nome_outorgante}", styles['Left']))
    elements.append(Paragraph(f"CPF nº {cpf_formatado}", styles['Left']))

    # Construir o PDF
    doc.build(elements)

    buffer.seek(0)

    # Nome do arquivo PDF
    nome_arquivo = f"procuracao_{nome_outorgante.replace(' ', '_')}.pdf"

   # Envie o PDF como resposta
    return send_file(buffer, as_attachment=True, download_name=nome_arquivo, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
