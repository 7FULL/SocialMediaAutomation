import datetime as datetime
import time

import google_auth_oauthlib
from pytubefix import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import re
import json
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
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.po_token = None

    @staticmethod
    def sanitize_filename(filename):
        return re.sub(r'[\\/*?:"<>|]', "", filename)

    def download_video(self):
        yt = YouTube(self.url)
        title = self.sanitize_filename(yt.title)
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

    def download_and_combine(self, create_clips=False, upload_short=False):
        self.download_video()
        self.download_audio()
        self.combine_video_audio()

        if create_clips:
            self.create_clips()

        if upload_short:
            self.upload_and_log_short()

    def upload_and_log_short(self):
        credentials = self.authenticate_youtube_account(self.account_name)

        if not credentials:
            print("No se pudo autenticar con la cuenta de YouTube")
            return
        else:
            token_file = f"youtube_automation/account_tokens/token_{self.account_name}.pickle"

            if os.path.exists(token_file):
                with open(token_file, 'rb') as token_file_obj:
                    credentials = pickle.load(token_file_obj)

        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

        # Determinar el siguiente número de parte
        log_file = f"youtube_automation/logs/{self.account_name}_uploaded_videos.json"
        part_number = self.get_next_part_number(log_file)

        file_path = f"{self.clips_folder}/clips/clip_{part_number}.mp4"

        title = self.acc_data.get("title") + " pt: " + str(part_number)
        description = self.acc_data.get("description") + " pt: " + str(part_number)

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

    def create_clips(self):
        video_path = self.final_output_path

        # Si se descargó el video, proceder a crear los clips
        if video_path and os.path.exists(video_path):
            # Cargar el video descargado
            video = VideoFileClip(video_path)

            # Definir la duración del clip en segundos
            clip_duration = 57  # Duración de cada clip
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

                path = ""

                # Si hay algun clip en la carpeta clips, se le suma 1 al nombre
                number = start // clip_duration

                if number_of_clips > 0:
                    number += number_of_clips

                path = os.path.join("clips", f"clip_{number}.mp4")

                clip.write_videofile(path, codec='libx264')

            # Cerrar el objeto de video
            video.close()
        else:
            print("No se pudo descargar el video.")

    @staticmethod
    def authenticate_youtube_account(account_name, scopes=None):
        """
        Authenticates with YouTube for a specific account, using a token file
        named 'token_{account_name}.pickle'. Returns True if successful, False otherwise.
        """
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        token_file = f"youtube_automation/account_tokens/token_{account_name}.pickle"
        secrets_file = f"youtube_automation/account_secrets/client_secrets_{account_name}.json"

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
