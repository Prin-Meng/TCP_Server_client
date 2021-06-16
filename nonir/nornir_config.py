from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from nornir_jinja2.plugins.tasks import template_file
from nornir_utils.plugins.functions import print_result
from vault_test.vault_1_init import client
from nornir.core.task import Task, Result

# Nornir加载配置文件
nr = InitNornir(config_file="config.yaml")

# 通过过滤提取,希望应用Task(任务)的主机
routers = nr.filter(
    type="router",
)

# 模板目录
templates_path = './templates/'

# 从vault读取信息,并更新nornir inventory
for host in routers.inventory.hosts.keys():
    # 从vault读取用户名和密码
    vault_data = client.secrets.kv.v2.read_secret_version(
        mount_point='qytang',
        path=f'{nr.inventory.hosts[host].platform}/cred'
    )
    cred_data = vault_data['data']['data']
    nr.inventory.hosts[host].username = cred_data.get('username')
    nr.inventory.hosts[host].password = cred_data.get('password')
    nr.inventory.hosts[host].connection_options['netmiko'].extras['secret'] = cred_data.get('secret')


def config_routers(task:Task) -> Result:
    # -------------------------------配置接口------------------------------
    # 读取模板，并通过参数render为具体配置
    ios_interface_template = task.run(
        name='第一步.1:读取IOS接口配置模板',
        task=template_file,
        template='cisco_ios_interface.template',
        path=templates_path
    )

    # 传入具体配置, 对设备进行配置, 注意需要".split('\n')"把配置转换为列表
    task.run(
        task=netmiko_send_config,
        name='第一步.2:配置路由器接口',
        config_commands=ios_interface_template.result.split('\n'),
        cmd_verify=True
    )

    # -------------------------------配置OSPF------------------------------
    # 读取模板,并且通过参数render为具体配置
    ios_ospf_template = task.run(
        name='第二步.1:读取路由器OSPF模板',
        task=template_file,
        template='cisco_ios_ospf.template',
        path=templates_path
    )

    # 传入具体配置, 对设备进行配置, 注意需要".split('\n')"把配置转换为列表
    task.run(
        task=netmiko_send_config,
        name='第二步.2:配置路由器OSPF',
        config_commands=ios_ospf_template.result.split('\n'),
        cmd_verify=True
    )

    # ---------------------------------配置Logging----------------------------
    # 读取模板，并通过参数render为具体配置
    ios_logging_template = task.run(
        name='第三步.1:读取logging服务器配置模板',
        task=template_file,
        template='cisco_logging_config.template',
        path=templates_path
    )

    # 传入具体配置, 对设备进行配置, 注意需要".split('\n')"把配置转换为列表
    task.run(
        task=netmiko_send_config,
        name='第三步.2:配置logging服务器',
        config_commands=ios_logging_template.result.split('\n'),
        cmd_verify=True
    )
    # ---------------------------------配置管理员信息----------------------------
    # 读取模板，并通过参数render为具体配置
    ios_user_template = task.run(
        name='第四步.1:读取设备管理员配置模板',
        task=template_file,
        template='cisco_ios_user.template',
        path=templates_path
    )

    # 传入具体配置, 对设备进行配置, 注意需要".split('\n')"把配置转换为列表
    task.run(
        task=netmiko_send_config,
        name='第四步.2:配置管理员信息',
        config_commands=ios_user_template.result.split('\n'),
        cmd_verify=True
    )

    # ---------------------------------配置管理员信息----------------------------
    # 读取模板，并通过参数render为具体配置
    ios_dns_template = task.run(
        name='第五步.1:读取DNS服务器模板',
        task=template_file,
        template='cisco_dns_servers.template',
        path=templates_path
    )

    # 传入具体配置, 对设备进行配置, 注意需要".split('\n')"把配置转换为列表
    task.run(
        task=netmiko_send_config,
        name='第五步.2:配置DNS服务器',
        config_commands=ios_dns_template.result.split('\n'),
        cmd_verify=True
    )

    return Result(
        host=task.host,
        result=f"{task.host}运行完成"
    )


# 执行配置路由器并打印结果
run_result = routers.run(task=config_routers,
                         name='配置CSR路由器', )
print_result(run_result)

