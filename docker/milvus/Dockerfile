FROM milvusdb/milvus:v2.5.8

RUN mkdir -p /var/lib/milvus/etcd
COPY ./embedEtcd.yaml /milvus/configs/embedEtcd.yaml

RUN mkdir -p /milvus/configs
COPY ./user.yaml /milvus/configs/user.yaml
