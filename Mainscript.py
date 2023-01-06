from pytube import YouTube
import re
import moviepy.editor as mp
from moviepy.editor import *
import os
from os import remove
from os import path

"""
Note: The legacy streams that contain the audio and video in a single file 
(referred to as “progressive download”) are still available, but only for resolutions 720p and below.
Esto quiere decir que de 1080p para arriba hay que descargar la parte del video.mp4 por un lado y 
el audio por otro para despues samplearlo con, por ejemplo, FFmpeg.
"""
# Dejamos que el usuario ponga el link del video
ingresoLink = input("ingresar link del video: ")
# ingresoLink = "link to short video" For Debugging 

# creamos el objeto tipo YouTube
videito = YouTube(str(ingresoLink))

# printeamos titulo del video para chequear
print("Titulo del video: ", videito.title)

# En la siguiente linea el usuario elige que quiere. Lo ideal seria visualmente, con un desplegable.
election = input("Escribir V para Video y Audio, A para solo Audio: ")

selected = (str(election)).lower()

#Si se eligio Video, damos a elegir las Resoluciones posibles
if selected == "v":
  ### Evaluo posibles streams (resoluciones) antes de elegir.
  lista_res_posibles = []
  for i in videito.streams:
    reso = str(i)
    filter = re.findall("res=\"(.+?)\"", reso)
    if len(filter) != 0:
      lista_res_posibles.append(" ".join(filter))
  # Eliminar duplicados con un set
  setcito = set(lista_res_posibles)
  print("Las resoluciones disponibles son:", setcito)
  ###
  resolucion = input("Ingrese resolucion deseada (solo numero): ")
  if int(resolucion) > 720:
    # No podemos usar el get_by_resolution de pytube porque solo funciona con progressive mp4, osea con resoluciones<=720p
    # Hay que filtrar lo que sea mp4 e idear una forma de automatizar la eleccion del video en XXXXp.
    lista_streams = videito.streams.filter(file_extension='mp4')
    for i in lista_streams:
      interes = str(i)
      try:
        # Filtramos el str que tenga la reso elegida, por ejemplo 1080.
        if str(resolucion) in interes:
          # sabiendo cual es el stream de XXXXp, filtramos el numero de itag.
          itag_filter = re.findall("itag=\"(...)\"", interes)
          itag = int(itag_filter[0])
          # Metemos el break porque con que encuentre una coincidencia de un .mp4 a XXXXp nos basta.
          break
      except:
        print("Stream en", str(resolucion)+"p", "no encontrado")
    
    # usamos el itag filtrado en el bucle para pickear nuestro .mp4.
    pickV = videito.streams.get_by_itag(itag)
    pickV.download(filename_prefix="video-")
    # pickeamos tambien el audio porque lo vamos a necesitar para samplear
    pickA = videito.streams.get_audio_only()
    pickA.download(filename_prefix="audio-")

    ### Merging Audio+Video using moviepy
    videoclip = VideoFileClip("video-"+videito.title+".mp4")
    audioclip = AudioFileClip("audio-"+videito.title+".mp4")
    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip
    videoclip.write_videofile(resolucion + "p" + videito.title + ".mp4") #Nombre con el que se guarda el archivo final
    ###

  ## Si resolucion == 720p.
  elif int(resolucion) == 720:
    pickV = videito.streams.get_by_resolution("720p")
    pickV.download(filename_prefix="video_720p-")

  ## Si resolucion < 720p.
  elif int(resolucion) < 720:
    pickV = videito.streams.get_lowest_resolution()
    pickV.download(filename_prefix="video_low_res-")

# SOLO Audio,ademas QUEREMOS .mp3. Lamentablemente tenemos que crear un video+audio y despues pasarlo a MP3. 
# Es medio rancio pero no encontre otra forma.
elif selected == "a":
  pickV = videito.streams.get_lowest_resolution()
  pickV.download(filename_prefix="video-")
  #Ponemos nombre del video (si estamos en la misma carpeta)
  video = mp.VideoFileClip("video-"+videito.title+".mp4")
  #Lo pasamos a mp3
  video.audio.write_audiofile(videito.title+".mp3")
  #Faltaria paso para eliminar el .mp4

locationVid = "location of the downloaded video"+videito.title+".mp4"
locationAud = "location of the downloaded audio"+videito.title+".mp4"

# Falta borrar los .mp4 que quedan al pedo cuando descargamos solo audio o cuando sampleamos un video a mas de 720p
# (no puedo hacer que ande esta parte pero no es escencial para el funcionamiento)
if path.exists(locationVid):
  remove(locationVid)
if path.exists(locationAud):
  remove(locationAud)
