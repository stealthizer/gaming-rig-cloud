# gaming-rig-cloud
How to create a gaming rig in the cloud



```
                   +---------+
                   | Remote  |
                   |  User   |
                   +----+----+
                        |
                        |
+------------------+----v-----+-+
|                  |          | |
|                  |   VPN    | |
|                  |  Server  | |
| Public Subnet    |          | |
+------------------+----^-----+-+
                        |
+------------------+----+-----+-+
|                  |          | |
|                  |  Gaming  | |
|                  |  Machine | |
| Private Subnet   |          | |
+------------------+----------+-+
```

First we will have to export the profile that we will use. For example:

```
$ export AWS_PROFILE=aws_profile_dev
```

Create the VPC

To create the VPC you will have to use sceptre. You will have to export your aws profile into the environment variable AWS_PROFILE

```
$ sceptre create-stack dev vpc
```

Once the VPC has been created we will create a bucket to store the openvpn certificates. To create the bucket:

```
$ sceptre create-stack dev s3bucket
```

Once the bucket has been created we will launch the openvpn instance in the public subnet

```
$ sceptre create-stack dev openvpn
```

Once the openvpn server is ready, we will launch the gaming rig

```
//TODO
$ sceptre create-stack dev gaming-rig
```