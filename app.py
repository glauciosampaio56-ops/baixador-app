from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import uuid

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = '/tmp/downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/baixar', methods=['POST'])
def baixar():
    data = request.json
    url = data.get('url')
    tipo = data.get('tipo', 'video')

    if not url:
        return jsonify({'erro': 'URL não fornecida'}), 400

    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f'{file_id}.%(ext)s')

    if tipo == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }
    else:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': True
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            titulo = info.get('title', 'midia')
            titulo_limpo = "".join([c for c in titulo if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
            
            for arquivo in os.listdir(DOWNLOAD_FOLDER):
                if arquivo.startswith(file_id):
                    caminho_completo = os.path.join(DOWNLOAD_FOLDER, arquivo)
                    extensao = arquivo.split('.')[-1]
                    return send_file(
                        caminho_completo,
                        as_attachment=True,
                        download_name=f"{titulo_limpo}.{extensao}"
                    )

        return jsonify({'erro': 'Erro no download'}), 500
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
