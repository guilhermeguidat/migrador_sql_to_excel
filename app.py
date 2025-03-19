from flask import Flask, render_template, request, redirect, flash, send_from_directory
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = ''

api_url = "https://www.rebasedata.com/api/v1/convert"

def send_to_api(input_file):
    if not os.path.exists(input_file):
        return None, "O arquivo não foi encontrado."

    files = {
        'files[]': open(input_file, 'rb')  
    }

    params = {
        'outputFormat': 'xlsx',  
        'errorResponse': 'json', 
    }

    try:
        response = requests.post(api_url, files=files, params=params)

        if response.status_code == 200:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_filename = f'{current_time}.zip'
            output_file = os.path.join('converted_files', output_filename)

            with open(output_file, 'wb') as f:
                f.write(response.content)

            return output_filename, None
        else:
            return None, f"Erro ao converter os arquivos: {response.json()}"
    except Exception as e:
        return None, f"Erro ao enviar a requisição: {e}"
    finally:
        files['files[]'].close()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Nenhum arquivo foi selecionado', 'error')
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        flash('Nenhum arquivo foi selecionado', 'error')
        return redirect(request.url)

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_extension = os.path.splitext(file.filename)[1]

    input_file = os.path.join('uploads', f'{current_time}{file_extension}')
    
    file.save(input_file)

    converted_file, error_message = send_to_api(input_file)

    if error_message:
        flash(f'Ocorreu um erro: {error_message}', 'error')

    return render_template('index.html', converted_file=converted_file)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join('converted_files', filename)

    if not os.path.exists(file_path):
        flash('Arquivo não encontrado', 'error')
        return redirect('/')

    return send_from_directory('converted_files', filename, as_attachment=True, download_name="BD_Convertido.zip")


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    if not os.path.exists('converted_files'):
        os.makedirs('converted_files')

    app.run(debug=True)
