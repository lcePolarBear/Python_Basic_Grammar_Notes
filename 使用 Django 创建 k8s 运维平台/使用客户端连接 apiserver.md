# 使用客户端连接 apiserver

### 官方的 Python 客户端库的使用方法
- [官方连接](https://github.com/kubernetes-client/python/)
- Python 安装 Kubernetes 客户端库
    ```shell
    pip install kubernetes -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```
- 使用 kubeconfig 证书创建 k8s 连接
    ```python
    # k8s.py
    from kubernetes import client, config
    import os

    # 获取当前目录并拼接文件
    kubeconfig = os.path.join(os.getcwd(),"kubeconfig")

    # 指定kubeconfig配置文件（/root/.kube/config）
    config.load_kube_config(kubeconfig)

    # 资源接口类实例化
    apps_api = client.AppsV1Api()

    # 打印 Deployment 对象名称
    for dp in apps_api.list_deployment_for_all_namespaces().items:
        print(dp.metadata.name)
    ```
    - 如能打印出 k8s 群集中的所有 deployment 资源类型说明连接成功
- 使用 Token 创建 k8s 连接
    ```python
    from kubernetes import client
    import os

    configuration = client.Configuration()

    # 指定 apiserver 地址
    configuration.host = "https://192.168.102.249:16443"

    # 指定 k8s 群集证书
    ca_file = os.path.join(os.getcwd(),"ca.crt")
    configuration.ssl_ca_cert = ca_file

    # 启用证书验证
    configuration.verify_ssl = True

    # 指定 k8s 字符串
    token = "xxxxxxxxxxxxxxx"
    configuration.api_key = {"authorization": "Bearer " + token}
    client.Configuration.set_default(configuration)
    apps_api = client.AppsV1Api()

    # 打印 Deployment 对象名称
    for dp in apps_api.list_deployment_for_all_namespaces().items:
        print(dp.metadata.name)
    ```
### 使用客户端操作 Deployment 资源
- 查询 deployment 资源
    ```python
    from kubernetes import client, config
    import os

    kubeconfig = os.path.join(os.getcwd(),"kubeconfig")
    config.load_kube_config(kubeconfig)
    apps_api = client.AppsV1Api()

    # 打印 Deployment 对象名称
    for dp in apps_api.list_deployment_for_all_namespaces().items:
        print(dp.metadata.name)
    ```
- 创建 deployment 资源
    ```python
    from kubernetes import client,config
    import os

    kubeconfig = os.path.join(os.getcwd(), "config")
    config.load_kube_config(kubeconfig)
    apps_api = client.AppsV1Api()

    namespace = "default"
    name = "api-test"
    replicas = 3
    labels = {'a':'1', 'b':'2'}
    image = "nginx"
    body = client.V1Deployment(
        api_version = "apps/v1",
        kind = "Deployment",
        metadata = client.V1ObjectMeta(name = name),
        spec = client.V1DeploymentSpec(
            replicas = replicas,
            template = client.V1PodTemplateSpec(
                metadata= client.V1ObjectMeta(labels= labels),
                spec= client.V1PodSpec(
                    containers= [client.V1Container(
                        name = "web",
                        image= image
                    )]
                )
            ),
            selector= {'matchLabels': labels}
        )
    )
    try:
        # 根据指定的实例创建 deployment
        apps_api.create_namespaced_deployment(namespace= namespace, body= body)
    except Exception as e:
        print(e)
    ```
- 删除 deployment 资源
    ```python
    from kubernetes import client,config
    import os

    kubeconfig = os.path.join(os.getcwd(), "config")
    config.load_kube_config(kubeconfig)
    apps_api = client.AppsV1Api()

    try:
        # 删除指定命名空间和名称的 deployment
        apps_api.delete_namespaced_deployment(namespace="default", name="api-test")
    except Exception as e:
        print(e)
    ```
### 使用客户端操作 Service 资源
- 查询 Service 资源
    ```python
    from kubernetes import client,config
    import os

    kubeconfig = os.path.join(os.getcwd(), "config")
    config.load_kube_config(kubeconfig)
    core_api = client.CoreV1Api()

    # 查询所有命名空间为 default 的 service 资源
    for svc in core_api.list_namespaced_service(namespace="default").items:
        print(svc.metadata.name)
    ```
- 创建 Service 资源
    ```python
    from kubernetes import client,config
    import os

    kubeconfig = os.path.join(os.getcwd(), "config")
    config.load_kube_config(kubeconfig)
    core_api = client.CoreV1Api()

    namespace = "default"
    name = "api-test"
    selector = {'a':'1', 'b':'2'}
    port = 80
    target_port = 80
    type = "NodePort"
    body = client.V1Service(api_version="v1",
                            kind= "Service",
                            metadata= client.V1ObjectMeta(name= name),
                            spec= client.V1ServiceSpec(selector= selector,
                                                    ports= [client.V1ServicePort(port= port,
                                                                                target_port=  arget_port)],
                                                    type= type)
                            )
    try:
        # 创建 service 资源
        core_api.create_namespaced_service(namespace= namespace, body= body)
    except Exception as e:
        print(e)
    ```
- 删除 Service 资源
    ```python
    from kubernetes import client,config
    import os

    kubeconfig = os.path.join(os.getcwd(), "config")
    config.load_kube_config(kubeconfig)
    core_api = client.CoreV1Api()

    try:
        # 删除指定的 service 资源
        core_api.delete_namespaced_service(namespace= "default", name= "api-test")
    except Exception as e:
        print(e)
    ```