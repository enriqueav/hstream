
# HStream

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

### How to run the example with the provided data

#### Step 0: Explanation

**Historical Information**

The InfluxDB instance is already loaded with Neubot information, modified to be timestamped from 2 years in the past till 2 years in the future approximately (2015-2019).

This is to ensure every time we send a query like *__give me the avg of the last 2 hours__* we have a result with some data from Historical Provider.

**Streamed Information**

In order to have streamed information, taken in real time from RabbitMQ by Spark Streaming, we first need to start a *producer*: a configurable Ruby script that reads from a file and sending individual messages to RabbitMQ (see Step 1).

The necessary Ruby version and the dependencies of the script are already included in the image, or downloaded by '*docker compose*'.

**HStream**

The core program is a Spark application packaged in an [uber jar](https://spark.apache.org/docs/latest/submitting-applications.html) that is downloaded into the repository by Docker **TO DO**.

This jar is sent to the Spark cluster using spark-submit (see Step 2) to be executed.


#### Step 1: Start Ruby Producer

Illustrates how to start the Ruby script responsible for sending the streamed information to the RabbitMQ instance.

```sh
    docker run -it --rm --name my-running-script \
        -v $(pwd)/scripts:/scripts \
        -v $(pwd)/data/ruby/bundle:/usr/local/bundle \
        -v $(pwd)/data/:/data --network=hstream_default \
        -w /scripts ruby:2.1 ruby  \
        /scripts/neubot_producer.rb  --repeat 10000 -m 1000
```

**TO DO**: document the parameters of the Ruby script.

#### Step 2: Start HStream (IoTOperators)

Illustrates how to submit the uber jar to the spark cluster to start the execution of the Operator.

```sh
    docker run --rm -it -v $(pwd)/scripts:/scripts \
        -v $(pwd)/conf/spark/master:/conf \
        -e SPARK_CONF_DIR=/conf           \
        --network=hstream_default         \
        hstream bin/spark-submit          \
        --class iotoperator.Max           \
        --master spark://master:7077 /scripts/IoT-Operators-assembly-1.1.jar \
        download_speed 720000 120000         \
        landmark influxdb                    \
        http://root:root@influx:8086 neubot speedtest \
        amqp://guest:guest@rabbit:5672/%2f neubot     \
        amqp://guest:guest@rabbit:5672/%2f salida3
```

**Description of the '_docker run_' arguments**

| Argument       | Type          | Meaning  |
| ------------- |-------------| -----|
| --rm     | flag | Automatically remove the container when it exits |
| --it      | flag      | Keep STDIN open even if not attached |
| -v $(pwd)/scripts:/scripts | volume      | /scripts is the location of the .rb to run |
| -v $(pwd)/conf/spark/master:/conf | volume      | Mount configuration files to decrease verbosity of Spark driver |
| -e SPARK_CONF_DIR=/conf | environment variable  | Provide the path of conf files for Spark  |
| --network=hstream_default | network | Provide the network, so the containers can find each others  |
| hstream bin/spark-submit | argument | Run the image 'hstream' with the command 'bin/spark-submit' |

**Description of the 'spark-submit' arguments**

| Argument       | Type          | Meaning  |
| ------------- |-------------| -----|
| --class iotoperator.Max    | argument | The uber jar will contain all the Operators, this argument is to specify the entry class (in this case Max operator) |
| /scripts/IoT-Operators-assembly-1.1.jar | argument | The location of the Jar is in the mounted volume /scripts. The version number of the .jar may change |
| (arguments passed to the jar) |  | Described in next table |

**Description of the arguments passed to the .jar ('IoTOperators API')**

| Order | In example | Argument | Meaning  |
|-------|------------|----------|----------|
| 1 | download_speed | name of value | Is the name of the variable/value to be observed. Is the value to be searched in the JSON obtained from the RabbitMQ and in the query to historical |
| 2 | 720000 | Size of the window in milliseconds | The **12 minutes** in the query "*every 2 minutes, give me avg of the last __12 minutes__" |
| 3 | 120000 | Size of the hop size in milliseconds | The **2 minutes** in the query "*every __2 minutes__, give me avg of the last 12 minutes" |
| 4 | landmark | Type of window 'landmark' or 'sliding' | **Landmark**: considers the data in the data stream from the beginning until now. **Sliding**: considers the data from now up to a certain range in the past. |
| 5 | influxdb | Historical information provider 'influxdb' or 'cassandra' | Name of the historical information provider |
| 6 | http://root:root@influx:8086 | connection string of the historical provider | In the format http://user:password@hostname:port |
| 7 | neubot | Database name | Name of the Database to query the historical provider |
| 8 | speedtest | Series name | Depending on the historical provider, this can be mapped to a series (in influxdb) or a table (in cassandra) |
| 9 | amqp://guest:guest@rabbit:5672/%2f | Connection string of RabbitMQ to receive input | In the format amqp://user:password@hostname:port/vhost |
| 10 | neubot | Name of input RabbitMQ queue | The queue where Spark Streaming will take the messages from |
| 11 | amqp://guest:guest@rabbit:5672/%2f | Connection string of RabbitMQ to receive input | In the format amqp://user:password@hostname:port/vhost |
| 12 | salida3 | Name of output RabbitMQ queue | The queue where HStream will send the results of the aggregation function. |
