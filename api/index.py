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

        cor_destaque = "#FF0000" if now_listening else "#555555"
        status_texto = "LISTENING NOW..." if now_listening else "LAST SEEN..."
        gif_base64 = "data:image/gif;base64,R0lGODlhIAAPAPAAAP///wAAACH/C05FVFNDQVBFMi4wAwEAAAAh+QQJCAAAACwAAAAAIAAPAAACJ4yPqcvtD6OctNqLs968+w+G4kiW5omm6sq27gvH8kzX9o3r+s4FACH5BAkIAAAALAAAAAAgAA8AAAIojI+py+0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jev6zgUAIfkECQgAAAAsAAAAACAADwAAAiWMj6nL7Q+jnLTai7PevPsPhuJIluaJpurKtu4Lx/JM1/aN6/rOBQAh+QQJCAAAACwAAAAAIAAPAAACJIyPqcvtD6OctNqLs968+w+G4kiW5omm6sq27gvH8kzX9o3r+s4FACH5BAkIAAAALAAAAAAgAA8AAAIljI+py+0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jev6zgUAIfkECQgAAAAsAAAAACAADwAAAiSMj6nL7Q+jnLTai7PevPsPhuJIluaJpurKtu4Lx/JM1/aN6/rOBQA7"
        equalizer_animado = f'<image x="230" y="22" width="30" height="15" href="{gif_base64}"/>' if now_listening else ""

        svg_code = f"""
        <svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="396" height="116" fill="#0D1117" stroke="{cor_destaque}" stroke-width="2" rx="10"/>

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
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(svg_code.encode("utf-8"))