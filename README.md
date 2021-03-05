# AWS Transit Gateway automation for static routes

## About
This project is intended to help with automating creating/deleting of [AWS Transit Gateway](https://aws.amazon.com/transit-gateway/) (TGW) static routes triggered by specific network event. Conceptually, it can be thought of as creating an API driven, 'floating/conditional' static route in the TGW route table.

## What challenge are we solving?
AWS TGW is a highly available, scalable distributed routing service managed by AWS. It operates like a logical router that allows for connecting different environments (Amazon VPCs, datacenters, TGWs in other AWS regions) and creating hub-and-spoke topologies.

Just like a router, TGW makes forwarding decisions based on the information in its routing table. There are a couple of ways to populate that routing table:
* crate a static routes using the TGW APIs
* automatically propagate routes learned from a particular attachment:
  * [AWS Direct Connect](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-dcg-attachments.html)(DX), [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpn-attachments.html)(S2S VPN) and [AWS TGW Connect](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-connect.html) attachments support learning routes over eBGP
  * [Amazon VPC attachment](https://docs.aws.amazon.com/vpc/latest/tgw/tgw-vpc-attachments.html) will learn all the CIDRs defined as part of the VPC.

To account for situations where the same route is received from multiple sources (i.e. 10.10.10.0/24 received over DX and VPN) TGW follows a strict [evaluation order](https://docs.aws.amazon.com/vpc/latest/tgw/how-transit-gateways-work.html) for deciding which routes to prefer:
* The most specific route for the destination address.
* If routes are the same with different targets:
  * Static routes, including static Site-to-Site VPN routes, have a higher precedence than propagated routes.
  * For propagated routes, the following order is used:
    * VPCs have the highest precedence.
    * Direct Connect gateways have the second highest precedence.
    * Transit Gateway Connects have the third highest precedence.
    * Site-to-Site VPNs have the fourth highest precedence.

This document focuses on a scenario where you need the TGW to preffer the routes in different order to the one documented above. For example, you might want the **default route to go over VPN and have a backup route over TGW peering attachment** (at the time of writing it supports static routing). If you created the static route over peering it would be preferred over the VPN route.

To solve it you have two options:
* setup more-specific/less-specific routing model:
  * configure the VPN to advertise 2x, more specific routes (instead of 1x): **0.0.0.0/1** and **128.0.0.0/1**
  * configure the static **0.0.0.0/0 via peering**
  * Because the VPN routes are more specific they'd be preferred over the less specific static route.
* if you must use the same route (i.e. you can't edit the remote route advertisement) then **the TGW static route automation** in this document can help you. It will allow you to add the static default route only when the dynamic, VPN route disappears.

## Architecture
For this setup to work you will need to have at least two route tables configured on your TGW. The first one, **production route table**, will be used by all the attachments - effectively controlling how traffic is forwarded between them. The second one, let's call it **'monitoring route table'** will be used to track any dynamic routing changes that the automation will trigger changes on.

The architecture below shows an overview of how the setup will work.

1. Steady State
In the example below there is a TGW with two attachments: VPN and Peering. There are two route tables - Monitoring, not used by any attachments and Production, used by all attachments (this would include any VPCs that the TGW would attach to). All the routes are propagated into both Route Tables.
![Steady State](/images/steady-state.png)
Format: ![Alt Text](url)

2. VPN goes down
When the VPN connection goes down the dynamic route would be removed from both route tables. There is a CloudWatch event enabled for the Monitoring route table. The CloudWatch event will trigger a Step Function that will act based on the event. Because a route was un-installed it will add a static route via alternative path (peering attachment) to the production route table.
![VPN Down](/images/VPN goes down.png)
Format: ![Alt Text](url)

3. VPN comes back up
When VPN re-establishes the dynamic route gets added to the Monitoring route table. This triggers another event that will initiate a Step Funtion to remove the static route via peering now that the dynamic route is back again.
![VPN Up](/images/VPN comes back up.png)
Format: ![Alt Text](url)


## Prerequisites


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
