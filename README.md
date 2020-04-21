
# cloud_computing   #Alaa Alzghoul 
The goal of this project is to apply the techniques practised during the labs, in order to build a prototype of a mini-Cloud application.
this project was developed in python and flask, it is called Football history in which an external API was used to GET some recent goals videos and REST commands such as POST, PUT and DELETE
were used to allow users to add, modify or delete new informations about best player award history.

first, a t2.medium instance was created using AWS. then the below commands were used to install and pull the lastest image of cassandra docker.

        sudo apt update
        sudo apt install docker.io
        sudo docker pull cassandra:latest

then the below command was used to run a Cassandra instance within docker.

        sudo docker run --name cassandra-proj -p 9042:9042 -d cassandra:latest

To interact with our Cassandra via its native command line shell client called  (cqlsh)  using CQL (the Cassandra Query Language).  
The Cassandra is running inside a docker container. To run the cqlsh command inside it and be able to interact with it the below command was used.

        sudo docker exec -it cassandra-proj cqlsh

Then two database tables were created for two reasons: the first one is to make the users sign-up to the website to be able to access to the data, and the second one is to make 
the users able to GET, POST, PUT and DELETE the database (best player award history) using the below commands.

        CREATE KEYSPACE bestplayer WITH REPLICATION ={'class' : 'SimpleStrategy', 'replication_factor' : 1};
        CREATE TABLE bestplayer.users (username text PRIMARY KEY, password_hash text);
        CREATE TABLE bestplayer.stats (year int PRIMARY KEY, player_name text);

Four files were created to make this application works in the docker, they are described below:

        1.requirements.txt: containes the needed libraries in our applications.
        2.Dockerfile: cantains the needed commands to make the docker works and the files that should be used.
        3.main.py: caontains the code needed for the authintication -using hashed passwod- in order to make the user sign-up, login and logout from the website.
        4.app.py: contains the code needed for the website itself (home page, best player award history page and the external API database page).

at the end to run the application over the cloud the below commands were used.

        sudo docker build . --tag=cassandrarest:v1
        sudo docker run -p 80:80 cassandrarest:v1

notes:
users can use POST, PUT and DELETE using the terminal and the below commands - the DNS is always the same as i am using elastic IP service -

	curl -i -H "Content-Type: application/json" -X POST -d '{"year":***,"player_name":"***"}' http://ec2-54-88-212-181.compute-1.amazonaws.com/best
	curl -i -H "Content-Type: application/json" -X PUT -d '{"year":***,"player_name":"***"}' http://ec2-54-88-212-181.compute-1.amazonaws.com/best
	curl -i -H "Content-Type: application/json" -X DELETE -d '{"year":***}' http://ec2-54-88-212-181.compute-1.amazonaws.com/best

the stars (***) mean that the user should specify the value.
