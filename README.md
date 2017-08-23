
### Starting/Stoping HStream cluster

Start:
```sh
# add `-d` for running on background
docker-compose up 
```

Stop:
```sh
docker-compose rm
```

### Examples
#### Ex 1: Spark count

Sends `/examples/spark-count.py` to `spark://master:7077` to count the number of elements in an array.

```sh
    docker run --rm -it \
        --volume=$(pwd)/examples:/examples  \
        --network=hstream_default           \
        hstream  bin/spark-submit --master spark://master:7077 /examples/spark-count.py
```

#### Ex 2: Spark streaming

Illustrates how to receive tweets and compute word frequencies using spark.

**Tweets producer (TCP server)**
```sh
    docker run --rm -it \
        --name producer \
        --volume=$(pwd)/examples:/examples  \
        --network=hstream_default           \
        hstream  python /examples/tweets-tcp.py producer 10000
```
**Tweets consumer (Spark driver)**
```sh 
    docker run --rm -it \
        --volume=$(pwd)/examples:/examples  \
        --network=hstream_default           \
        hstream  bin/spark-submit --master spark://master:7077 /examples/spark-streaming.py  producer 10000
```

#### Ex 3: Spark streaming via RabbitMQ

Illustrates how to consume tweets from RabbitMQ. 

**Producer**
```sh
    docker run --rm -it \
        --name producer \
        --volume=$(pwd)/examples:/examples  \
        --network=hstream_default           \
        hstream  python /examples/tweets-rabbit.py  rabbit tweets
```

**TCP Server**
```sh
    docker run --rm -it \
        --name server \
        --volume=$(pwd)/examples:/examples  \
        --network=hstream_default           \
        hstream  python /examples/rabbit-tcp-server.py  rabbit tweets server 10000
```

**Spark Driver**
```sh
    docker run --rm -it \
        --volume=$(pwd)/examples:/examples  \
        --network=hstream_default           \
        hstream  bin/spark-submit --master spark://master:7077 /examples/spark-streaming.py  server 10000
```
        
