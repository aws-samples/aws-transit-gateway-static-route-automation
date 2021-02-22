import boto3
import logging
import os

client = boto3.client('ec2', region_name=os.environ.get('REGION'))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def already_exists(route,tgw_rt_id):
    logger.info("funct:: already_exists started... ")

    #Search if the route is already the TGW route table
    route_search = client.search_transit_gateway_routes(
        TransitGatewayRouteTableId=tgw_rt_id,
        Filters=[
            {
                'Name': 'route-search.exact-match',
                'Values': [
                    route,
                ]
            },
        ],
        MaxResults=10,
        DryRun=False
    )

    # If the search is emtry return True
    if route_search['Routes']:
        logger.info("funct:: already_exists: route {} found in TGW RT {} ".format(route, tgw_rt_id))
        return True
    else:
        logger.info("funct:: already_exists: route {} NOT found in TGW RT {} ".format(route, tgw_rt_id))
        return False


def lambda_handler(event, context):
    logger.info("funct:: lambda_handler started... ")
    # Define variables
    tgw_rt_id=os.environ.get('TGW_ROUTE_TABLE')
    tgw_attachment_id=os.environ.get('TGW_DESTINATION_ATTACHMENT_ID')
    route=os.environ.get('ROUTE')


    if not already_exists(route, tgw_rt_id):
        try:
            logger.info("Adding route {} via {} to TGW RT {}".format(route,tgw_attachment_id,tgw_rt_id))
            client.create_transit_gateway_route(
                DestinationCidrBlock=route,
                TransitGatewayRouteTableId=tgw_rt_id,
                TransitGatewayAttachmentId=tgw_attachment_id,
                Blackhole=False,
                DryRun=False
            )
        except Exception as ex:
            logger.info("exception occured while adding a tgw route: {} ".format(ex))
            raise

    logger.info("funct:: lambda_handler completed... ")
