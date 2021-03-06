from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    cdk,
)

app = cdk.App()
stack = cdk.Stack(app, "aws-ecs-integ-ecs")

# Create a cluster
vpc = ec2.VpcNetwork(
    stack, "Vpc",
    max_a_zs=2
)

cluster = ecs.Cluster(
    stack, "EcsCluster",
    vpc=vpc
)
cluster.add_capacity("DefaultAutoScalingGroup",
                     instance_type=ec2.InstanceType("t2.micro"))

# Create a task definition with placement constraints
task_definition = ecs.Ec2TaskDefinition(
    stack, "TaskDef",
    placement_constraints=[
        {"type": ecs.PlacementConstraintType.DistinctInstance}
    ]
)

container = task_definition.add_container(
    "web",
    image=ecs.ContainerImage.from_registry("nginx:latest"),
    memory_limit_mi_b=256,
)
container.add_port_mappings(
    container_port=80,
    host_port=8080,
    protocol=ecs.Protocol.Tcp
)

# Create Service
service = ecs.Ec2Service(
    stack, "Service",
    cluster=cluster,
    task_definition=task_definition,
)
service.place_packed_by(ecs.BinPackResource.Memory)
service.place_spread_across(ecs.BuiltInAttributes.AVAILABILITY_ZONE)

app.run()
