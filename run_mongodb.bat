@echo start 
d:
cd D:\Program Files\MongoDB\Server\3.4\bin\
start mongod --dbpath=D:\programming\MongoDB\data\db
start mongod --logpath=D:\programming\MongoDB\data\MongoDB.log
pause
start mongo 