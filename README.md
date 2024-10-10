# Lyrics-Search-Engine
The objective of the project is to design and implement software capable of storing and searching for songs using an inverted index. The application was developed within a Docker container, ensuring a consistent and isolated environment for development and deployment across different systems. This approach facilitates cross-platform compatibility and streamlines the management of dependencies, making the software more robust and portable.

# Installation guide

* Download [Docker](https://www.docker.com/products/docker-desktop/)
* Install (follow the Wizard) and open Docker
* Open a terminal from inside the project-folder and run:
    * ```docker build --tag false_image:latest .``` (to build the Docker image)
* Download [Xming X Server for Windows](https://sourceforge.net/projects/xming/)
* Install Xming (follow the wizard)
* Open "Command Prompt"
* Run ```ipconfig``` and copy the "IPv4 Address" of your network (for me it was 192.168.1.41)
* Run ```set DISPLAY=IPv4 Address:0.0``` (where IPv4 Address your own)
* Find where the "Xming.exe" is located (default location: "C:\Program Files (x86)")
* Open a terminal from that folder and run ```.\Xming.exe -ac```
* Open another instance of "Command Prompt" and run:
    * ```docker run -it -v PATH:/usr/src/ --rm -e DISPLAY=%DISPLAY% --network="host" --name false false_image``` (where PATH the absolute path to the folder containing the Dockerfile)

## How much time/storage it will take

* The storage requirement for the Docker Desktop app is around 3GB
* The construction of the "false_image" is anticipated to take approximately 15 to 20 minutes, with a storage consumption of about 3.5GB

## Command Explanation:
* ```-it```, interactive
* ```-v```, mount a system folder from the host before the colon, to a folder inside the Docker container after the colon
* ```-rm```, removes the container after it stops running
* ```-e DISPLAY=%DISPLAY%```, sets the display environmental variable of the docker as the "192.168.1.4:0.0"
* ```--network="host"```, the container will share the network namespace with the host machine
* ```--name container_name image_name```

## Useful commands:

* ```docker start -i false```, to start the Container again
*  ```docker stop false```, to stop the Container
* ```docker rm -f false```, to forcefully remove the Container
* ```docker rmi -f false_image```, to forcefully remove the false_image
* ```docker exec -it false <command_to_execute_inside_the_container>```, to run commands from inside the Docker container
<br><br>

## Potential Problems:

* If you forcefully exit the FALSE_ENGINE from the command prompt (e.g. with CTRL + C), you must exit the Xming Server and re-run it like in the [Installation guide](#installation-guide) if you wish to re-run the Docker container
* If the "IPv4 Address" changes, you can update the environmental variable from the command line by running:
    *```set DISPLAY=NEW_VALUE```

