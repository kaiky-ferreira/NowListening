from http.server import BaseHTTPRequestHandler
import os
import requests
import base64

def load_image_base64(URL):
    if not URL:
        return ""
    
    try:
        response = requests.get(URL, timeout=5)

        if response.status_code == 200:
            encoded = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded}"
    except:
        pass
    return ""

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        API_KEY = os.environ.get("API_KEY")
        USER = os.environ.get("USER")
        URL = "http://ws.audioscrobbler.com/2.0/"
        USER_AGENT = os.environ.get("USER_AGENT", "GitHubProfile/1.0")
        headers = {'User-Agent': USER_AGENT}    

        params = {
            'method': 'user.getrecenttracks',
            'user': USER,
            'api_key': API_KEY,
            'format': 'json',
            'limit': 1
        }

        music_name = "Offline"
        artist = "No Music"
        imagem_url = None
        now_listening = False

        try:
            response = requests.get(URL, headers=headers, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if 'recenttracks' in data and 'track' in data['recenttracks'] and len(data['recenttracks']['track']) > 0:
                    music = data['recenttracks']['track'][0]
                    music_name = music['name']
                    artist = music['artist']['#text']
                    album = music['album']['#text']
            
                    if 'image' in music and len(music['image']) > 3:
                        imagem_url = music['image'][3]['#text']


                    status_attr = music.get('@attr')
                    if status_attr and status_attr.get('nowplaying') == 'true':
                        now_listening = True
        
        except Exception as e:
            print(f"Erro na API: {e}")


        image_base64 = load_image_base64(imagem_url) if imagem_url else ""

        cor_destaque = "#ffffff" if now_listening else "#555555"
        status_texto = "LISTENING NOW..." if now_listening else "LAST SEEN..."
        equalizer_animado = f"""
        <g transform="translate(245, 23)">
            <rect x="0" y="5" width="3" height="10" fill="{cor_destaque}">
                <animate attributeName="height" values="5;15;5" dur="1s" repeatCount="indefinite"/>
                <animate attributeName="y" values="10;0;10" dur="1s" repeatCount="indefinite"/>
            </rect>
            <rect x="5" y="0" width="3" height="15" fill="{cor_destaque}">
                <animate attributeName="height" values="15;5;15" dur="0.8s" repeatCount="indefinite"/>
                <animate attributeName="y" values="0;10;0" dur="0.8s" repeatCount="indefinite"/>
            </rect>
            <rect x="10" y="8" width="3" height="7" fill="{cor_destaque}">
                <animate attributeName="height" values="7;15;7" dur="1.2s" repeatCount="indefinite"/>
                <animate attributeName="y" values="8;0;8" dur="1.2s" repeatCount="indefinite"/>
            </rect>
            <rect x="15" y="2" width="3" height="13" fill="{cor_destaque}">
                <animate attributeName="height" values="13;4;13" dur="0.9s" repeatCount="indefinite"/>
                <animate attributeName="y" values="2;11;2" dur="0.9s" repeatCount="indefinite"/>
            </rect>
        </g>
        """ if now_listening else ""

        svg_code = f"""
        <svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="396" height="116" fill="#0D1117" stroke="{cor_destaque}" stroke-width="2" rx="2"/>

        <image x="15" y="15" width="90" height="90" href="{image_base64}" clip-path="inset(0% round 6px)"/>
        {equalizer_animado}     

        <style>
            .titulo {{ font-family: monospace; font-size: 12px; fill: {cor_destaque}; font-weight: bold; }}
            .musica {{ font-family: monospace; font-size: 16px; fill: #FFFFFF; font-weight: bold; }}
            .artista {{ font-family: monospace; font-size: 14px; fill: #AAAAAA; }}
        </style>

        <text x="120" y="35" class="titulo">{status_texto}</text>

        <text x="120" y="65" class="musica">{music_name[:25] + '...' if len(music_name) > 25 else music_name}</text>

        <text x="120" y="90" class="artista">{artist}</text>
        </svg>
        """

        self.send_response(200)
        self.send_header("Content-type", "image/svg+xml")
        self.send_header("Cache-Control", "max-age=0, s-maxage=0, no-cache, no-store, must-revalidate")
        self.end_headers()
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.wfile.write(svg_code.encode("utf-8"))
