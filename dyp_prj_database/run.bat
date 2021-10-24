@echo OFF

echo Validating files...

IF NOT EXIST database (
	echo Missing directory "database", creating...
	mkdir database
	echo Created directory database
)
IF EXIST database (
	cd database

	IF NOT EXIST Dockerfile (
		echo Missing file database/Dockerfile, creating...
		(
			echo FROM mysql:5.7
			echo COPY ./initdb/ /docker-entrypoint-initdb.d/
			echo COPY ./custom.cnf /etc/mysql/conf.d/custom.cnf
		)>"Dockerfile"
		echo Created file database/Dockerfile
	)

	IF NOT EXIST persistant_storage (
		echo Missing directory database/persistant_storage, creating...
		mkdir persistant_storage
		echo Created directory database/persistant_storage
	)

	IF NOT EXIST initdb (
		echo Missing directory database/initdb, creating...
		mkdir initdb
		echo Created directory database/initdb
	)

cd ..
) ELSE (
	echo Could not create default database files.
	PAUSE
	EXIT
)

docker-compose up