import datetime as datetime
import time

import google_auth_oauthlib
from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import re
import json

# PIL compatibility fix for newer versions
try:
    from PIL import Image
    # Check if ANTIALIAS exists, if not, use LANCZOS
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class YouTubeAutomation:
    def __init__(self, url="", output_path='output', account_name="", acc_data=None):
        if acc_data is None:
            acc_data = {}
        self.credentials = None
        self.url = url
        self.output_path = output_path
        self.video_path = None
        self.audio_path = None
        self.final_output_path = None
        self.account_name = account_name
        self.clips_folder = acc_data.get("clip_folder")
        self.acc_data = acc_data
        self.original_video_title = None  # Store original YouTube video title
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.po_token = None

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def download_video(self):
        yt = YouTube(self.url)
        title = self.sanitize_filename(yt.title)
        # Store original title for later use in clip titles
        self.original_video_title = yt.title
        video_stream = yt.streams.filter(only_video=True, file_extension='mp4').order_by('resolution').desc().first()
        self.video_path = os.path.join(self.output_path, f"{title}_video.mp4")
        video_stream.download(output_path=self.output_path, filename=f"{title}_video.mp4")
        print(f"Video downloaded to {self.video_path}")

    def download_audio(self):
        yt = YouTube(self.url)
        title = self.sanitize_filename(yt.title)
        audio_stream = yt.streams.filter(only_audio=True).first()
        self.audio_path = os.path.join(self.output_path, f"{title}_audio.mp4")
        audio_stream.download(output_path=self.output_path, filename=f"{title}_audio.mp4")
        print(f"Audio downloaded to {self.audio_path}")

    def combine_video_audio(self):
        if self.video_path and self.audio_path:
            video_clip = VideoFileClip(self.video_path)
            audio_clip = AudioFileClip(self.audio_path)

            final_clip = video_clip.set_audio(audio_clip)
            final_output_path = os.path.join(self.output_path,
                                             f"{os.path.splitext(os.path.basename(self.video_path))[0]}_final.mp4")
            final_clip.write_videofile(final_output_path, codec='libx264', audio_codec='aac')
            print(f"Final video with audio saved to {final_output_path}")

            os.remove(self.video_path)
            os.remove(self.audio_path)
            print("Temporary files removed.")

            self.final_output_path = final_output_path
        else:
            print("Video or audio file is missing. Please download both before combining.")

    def download_and_combine(self, create_clips=False, upload_short=False, mobile_format=True):
        """
        Descarga video, audio y los combina. Opcionalmente crea clips y sube shorts.
        Args:
            create_clips (bool): Si True, crea clips del video
            upload_short (bool): Si True, sube el video como short
            mobile_format (bool): Si True, los clips se crean en formato vertical móvil
        """
        self.download_video()
        self.download_audio()
        self.combine_video_audio()

        if create_clips:
            self.create_clips(mobile_format=mobile_format)

        if upload_short:
            self.upload_and_log_short()

    def upload_and_log_short(self):
        credentials = self.authenticate_youtube_account(self.account_name)

        if not credentials:
            print("No se pudo autenticar con la cuenta de YouTube")
            return
        else:
            project_root = os.path.dirname(os.path.dirname(__file__))
            token_file = os.path.join(project_root, "web_app/backend/youtube_automation/account_tokens", f"token_{self.account_name}.pickle")

            if os.path.exists(token_file):
                with open(token_file, 'rb') as token_file_obj:
                    credentials = pickle.load(token_file_obj)

        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

        # Determinar el siguiente número de parte
        log_file = f"youtube_automation/logs/{self.account_name}_uploaded_videos.json"
        part_number = self.get_next_part_number(log_file)

        file_path = f"{self.clips_folder}/clips/clip_{part_number}.mp4"

        # Generate title - use configured title or fallback to original video title
        account_title = self.acc_data.get("title", "").strip()
        if account_title:
            title = account_title + " pt: " + str(part_number)
        elif self.original_video_title:
            # Use original video title + part number
            title = f"{self.original_video_title} - Part {part_number}"
        else:
            # Final fallback to generic title
            title = f"Video Clip #{part_number}"
        
        # Generate description
        account_description = self.acc_data.get("description", "").strip()
        if account_description:
            description = account_description + " pt: " + str(part_number)
        else:
            description = f"Automatically generated video clip #{part_number}"

        # Generate an array of tags from ,
        tags = self.acc_data.get("tags")

        if tags:
            tags = tags.split(",")

        # Subir el short
        response = self.upload_short(youtube, file_path, tags,
                                     description, title,
                                     self.acc_data.get("category_id"))

        if (response):
            print(f"Short numero {part_number} subido correctamente")

            # Registrar el video en el JSON
            self.log_video(log_file)
        else:
            print("Short no subido por un error ocurrido")

    @staticmethod
    def get_next_part_number(log_file):
        # Cargar los datos existentes
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
                return len(data.get("videos", [])) + 1  # Retornar el siguiente número de parte
        else:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
        return 1  # Si no existe, empezar desde 1

    def create_clips(self, mobile_format=True, clip_duration=57):
        """
        Crea clips del video descargado
        Args:
            mobile_format (bool): Si True, convierte a formato vertical móvil (9:16)
            clip_duration (int): Duración de cada clip en segundos
        """
        video_path = self.final_output_path

        # Si se descargó el video, proceder a crear los clips
        if video_path and os.path.exists(video_path):
            # Cargar el video descargado
            video = VideoFileClip(video_path)

            # Definir la duración del clip en segundos
            print(f"Creando clips de {clip_duration} segundos cada uno")
            if mobile_format:
                print("Formato móvil activado - los clips se convertirán a 9:16")
            total_duration = int(video.duration)  # Duración total del video

            # Crear clips en un bucle
            # Se hace esa resta para evitar el primer clip
            number_of_clips = len(os.listdir("clips"))

            for start in range(clip_duration, total_duration, clip_duration):
                end = min(start + clip_duration, total_duration)  # Asegurarse de que no sobrepase la duración total

                # Si el clip dura menos que la duración deseada, no se hace
                if end - start < clip_duration:
                    break

                clip = video.subclip(start, end)
                
                # Convertir a formato vertical móvil (9:16) si está habilitado
                if mobile_format:
                    clip = self.convert_to_mobile_format(clip)

                path = ""

                # Si hay algun clip en la carpeta clips, se le suma 1 al nombre
                number = start // clip_duration

                if number_of_clips > 0:
                    number += number_of_clips

                path = os.path.join("clips", f"clip_{number}.mp4")

                clip.write_videofile(path, codec='libx264', audio_codec='aac')

            # Cerrar el objeto de video
            video.close()
        else:
            print("No se pudo descargar el video.")

    def convert_to_mobile_format(self, clip, crop_position='center'):
        """
        Convierte un clip a formato vertical móvil (9:16 aspect ratio)
        Recorta inteligentemente el video para que se vea bien en móviles
        Args:
            clip: El clip de video a convertir
            crop_position: Posición del recorte ('center', 'top', 'bottom', 'left', 'right')
        """
        # Dimensiones objetivo para móvil (9:16) - YouTube Shorts optimizado
        target_width = 1080
        target_height = 1920
        target_ratio = target_height / target_width  # 1.778 aproximadamente
        
        # Obtener dimensiones actuales del clip
        current_width = clip.w
        current_height = clip.h
        current_ratio = current_height / current_width
        
        print(f"Video original: {current_width}x{current_height} (ratio: {current_ratio:.2f})")
        print(f"Formato móvil objetivo: {target_width}x{target_height} (ratio: {target_ratio:.2f})")
        
        if current_ratio < target_ratio:
            # El video es más ancho que el formato móvil - recortar horizontalmente
            # Calcular nueva anchura manteniendo la altura
            new_width = int(current_height / target_ratio)
            
            # Determinar posición de recorte horizontal
            if crop_position == 'left':
                x_start = 0
            elif crop_position == 'right':
                x_start = current_width - new_width
            else:  # center por defecto
                x_center = current_width / 2
                x_start = int(x_center - new_width / 2)
            
            x_start = max(0, x_start)
            x_end = min(current_width, x_start + new_width)
            
            # Recortar el video
            clip = clip.crop(x1=x_start, x2=x_end)
            print(f"Recortado horizontalmente ({crop_position}): {new_width}x{current_height}")
            
        elif current_ratio > target_ratio:
            # El video es más alto que el formato móvil - recortar verticalmente
            # Calcular nueva altura manteniendo la anchura
            new_height = int(current_width * target_ratio)
            
            # Determinar posición de recorte vertical
            if crop_position == 'top':
                y_start = 0
            elif crop_position == 'bottom':
                y_start = current_height - new_height
            else:  # center por defecto, con ligero sesgo hacia arriba para mejor encuadre
                y_center = current_height / 2
                y_offset = current_height * 0.05  # 5% hacia arriba para mejor composición
                y_start = int(y_center - new_height / 2 - y_offset)
            
            y_start = max(0, y_start)
            y_end = min(current_height, y_start + new_height)
            
            # Recortar el video
            clip = clip.crop(y1=y_start, y2=y_end)
            print(f"Recortado verticalmente ({crop_position}): {current_width}x{new_height}")
        
        # Redimensionar al tamaño exacto para móvil con algoritmo de alta calidad
        clip = clip.resize((target_width, target_height))
        print(f"Redimensionado a: {target_width}x{target_height}")
        
        # Aplicar filtros para mejorar calidad en móvil
        # Aumentar ligeramente la saturación para que se vea mejor en pantallas móviles
        try:
            # Solo aplicar si moviepy lo soporta
            clip = clip.fx(lambda gf, t: gf(t).multiply_brightness(1.02).multiply_saturation(1.1))
        except:
            pass  # Si hay error, continuar sin filtros
        
        return clip
    
    def get_platform_dimensions(self, platform='youtube_shorts'):
        """
        Obtiene las dimensiones optimizadas para diferentes plataformas
        Args:
            platform: 'youtube_shorts', 'tiktok', 'instagram_reels', 'youtube_standard'
        Returns:
            tuple: (width, height)
        """
        dimensions = {
            'youtube_shorts': (1080, 1920),    # 9:16 - Óptimo para YouTube Shorts
            'tiktok': (1080, 1920),           # 9:16 - TikTok estándar
            'instagram_reels': (1080, 1920),   # 9:16 - Instagram Reels
            'instagram_story': (1080, 1920),   # 9:16 - Instagram Stories
            'youtube_standard': (1920, 1080),  # 16:9 - YouTube estándar
            'square': (1080, 1080),           # 1:1 - Instagram post
        }
        return dimensions.get(platform, (1080, 1920))

    @staticmethod
    def authenticate_youtube_account(account_name, scopes=None):
        """
        Authenticates with YouTube for a specific account, using a token file
        named 'token_{account_name}.pickle'. Returns True if successful, False otherwise.
        """
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        # Get the project root directory (where core/ and web_app/ are located)
        project_root = os.path.dirname(os.path.dirname(__file__))
        token_file = os.path.join(project_root, "web_app/backend/youtube_automation/account_tokens", f"token_{account_name}.pickle")
        secrets_file = os.path.join(project_root, "web_app/backend/youtube_automation/account_secrets", f"client_secrets_{account_name}.json")

        creds = None

        # 1) Check if we have an existing token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token_file_obj:
                creds = pickle.load(token_file_obj)

        # 2) If no valid creds, prompt user
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Failed to refresh token for {account_name}: {e}")
                    creds = None
            else:
                # Manual authentication
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        secrets_file, scopes
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Authentication canceled or failed for {account_name}: {e}")
                    return False  # user closed the browser or something

            # 3) If we got creds, save them
            if creds and creds.valid:
                with open(token_file, 'wb') as token_file_obj:
                    pickle.dump(creds, token_file_obj)
            else:
                return False

        return True

    def upload_short(self, youtube, file_path, tags=None, description=None, title=None, category_id=None):
        print(f"Subiendo {file_path} a YouTube...")

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            },
            media_body=file_path
        )
        response = None

        try:
            response = request.execute()
        except:
            print("Probablemente error de timeout")

        return response

    def log_video(self, title):
        log_file = "uploaded_videos.json"

        # Cargar los datos existentes
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
                f.close()
        else:
            data = {"videos": []}

        # Añadir el nuevo video
        data["videos"].append({"title": title})

        # Guardar de nuevo en el archivo
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=4)
