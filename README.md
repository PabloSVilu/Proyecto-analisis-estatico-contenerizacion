Proyecto: análisis estático, contenerización

El proyecto es una aplicacion web para ver el clima, en la cual uno puede registrarse con un correo, quedando asi registrado en la base de datos.
La aplicacion tambien recomienda actividades dependiendo del estado climatico, temperatura actual, humedad y velocidad del viento.
Un usario registrado puede crear actividades personalizadas o marcar como favorito alguna de las actividades predeterminadas.

Instrucciones:

- Asegurese de tener descargado la ultima version de python

-Descargue/instale Docker Desktop para su sistema operativo y inicie la apliacacion.

-Abra su consola de comandos preferida.

-En la consola de comandos dirijase a la carpeta del proyecto, o simplemente donde se ubique el archivo "docker-compose-yml".

-En la consola ingrese el siguiente comando docker-compose up --build , para crear el build del proyecto en Docker.

-Una vez terminado el proceso anterior la aplicacion ya esta lista para su uso, puede ingresar a esta a atravez des mismo Docker o con el siguiente link: localhost:5173.

-Para probar las herramientas de analisis estatico, instale las herramientas con los siguientes comandos.

    	pip install pylint
    	pip install radon

-Una vez instaladas dirijase con su consola de comandos a la carpeta Backend, y use los siguientes comandos:

	 py pylint.py "nombre de archivo que quiera analizar".py 
 	py radon.py "nombre de archivo que quiera analizar".py 

Ejemplo
 	py pylint.py main.py
	py radon.py main.py

-Finalmente le mostrar por consola o por el archivo pylint-report.txt" y/o "radon-report.txt"los resultados de los analisis respectivamente.



Imagen de ejemplo de como se ve la aplicacion:
![image](https://github.com/user-attachments/assets/e7d1aae1-1979-47b8-869c-fb8c014c3c33)

